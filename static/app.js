// CascadeSight Dashboard - Advanced Frontend Engine & Visualizer

let currentGraphMode = 'synthetic';
let graphData = { nodes: [], edges: [] };
let selectedNode = 'Internal Config Service';
let currentThreshold = 0.40;

let simulationResult = null;
let currentStepIndex = 0;
let playbackTimer = null;
let isPlaying = false;

// Canvas & Physics Engine
let canvas = null;
let ctx = null;
let nodePositions = {}; // id -> {x, y, vx, vy, radius, state, label, category, degree}
let isDragging = false;
let draggedNode = null;
let hoveredNode = null;
let particleOffset = 0;

// Chart Instance
let tippingChart = null;

document.addEventListener('DOMContentLoaded', () => {
    canvas = document.getElementById('graphCanvas');
    ctx = canvas.getContext('2d');
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Canvas Mouse & Touch Events
    canvas.addEventListener('mousedown', handleMouseDown);
    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('mouseup', handleMouseUp);
    canvas.addEventListener('mouseleave', handleMouseUp);

    // Physics & Particle Animation Loop
    requestAnimationFrame(animationLoop);

    // Initial Dashboard Load
    initDashboard();
});

function resizeCanvas() {
    if (!canvas) return;
    const rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;
    if (graphData.nodes && graphData.nodes.length > 0) {
        setupNodePositions();
    }
}

async function initDashboard() {
    await loadGraph(currentGraphMode);
    await loadRiskScores();
    await loadTippingPoint();
}

async function switchGraphMode(mode) {
    currentGraphMode = mode;
    document.getElementById('btn-synthetic').classList.toggle('active', mode === 'synthetic');
    document.getElementById('btn-meta').classList.toggle('active', mode === 'meta');

    selectedNode = (mode === 'meta') ? 'Backbone BGP Router Config' : 'Internal Config Service';
    document.getElementById('lbl-selected-node').innerText = selectedNode;
    
    resetSimulation();
    await initDashboard();
}

async function loadGraph(mode) {
    try {
        const res = await fetch(`/api/graph?type=${mode}`);
        graphData = await res.json();
        setupNodePositions();
        drawGraph();
    } catch (err) {
        console.error('Error loading graph:', err);
    }
}

function setupNodePositions() {
    const width = canvas.width || 800;
    const height = canvas.height || 520;
    const centerX = width / 2;
    const centerY = height / 2;
    const numNodes = graphData.nodes.length;
    const radius = Math.min(width, height) * 0.36;

    nodePositions = {};

    graphData.nodes.forEach((node, i) => {
        const angle = (i / numNodes) * 2 * Math.PI;
        nodePositions[node.id] = {
            id: node.id,
            label: node.label || node.id,
            category: node.category || 'default',
            x: centerX + radius * Math.cos(angle) + (Math.random() - 0.5) * 20,
            y: centerY + radius * Math.sin(angle) + (Math.random() - 0.5) * 20,
            vx: 0,
            vy: 0,
            radius: Math.max(14, 12 + (node.degree || 1) * 1.6),
            state: 'healthy', // 'healthy', 'at-risk', 'failed'
            inDegree: node.inDegree,
            outDegree: node.outDegree,
            degree: node.degree
        };
    });
}

// Animation & Physics Loop
function animationLoop() {
    particleOffset = (particleOffset + 0.8) % 30;
    applyForcePhysics();
    drawGraph();
    requestAnimationFrame(animationLoop);
}

function applyForcePhysics() {
    const nodes = Object.values(nodePositions);
    if (nodes.length === 0) return;

    const width = canvas.width || 800;
    const height = canvas.height || 520;
    const centerX = width / 2;
    const centerY = height / 2;

    // Repulsion between nodes
    for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
            const n1 = nodes[i];
            const n2 = nodes[j];
            const dx = n2.x - n1.x;
            const dy = n2.y - n1.y;
            const dist = Math.hypot(dx, dy) || 1;
            const minDist = (n1.radius + n2.radius) * 2.2;

            if (dist < minDist) {
                const force = (minDist - dist) / dist * 0.05;
                n1.vx -= dx * force;
                n1.vy -= dy * force;
                n2.vx += dx * force;
                n2.vy += dy * force;
            }
        }
    }

    // Spring attraction along edges
    graphData.edges.forEach(edge => {
        const src = nodePositions[edge.source];
        const tgt = nodePositions[edge.target];
        if (!src || !tgt) return;

        const dx = tgt.x - src.x;
        const dy = tgt.y - src.y;
        const dist = Math.hypot(dx, dy) || 1;
        const targetDist = 130;
        const force = (dist - targetDist) * 0.002;

        src.vx += dx * force;
        src.vy += dy * force;
        tgt.vx -= dx * force;
        tgt.vy -= dy * force;
    });

    // Central gravity & position update
    nodes.forEach(n => {
        if (n === draggedNode) return; // User is dragging this node

        const dx = centerX - n.x;
        const dy = centerY - n.y;
        n.vx += dx * 0.0005;
        n.vy += dy * 0.0005;

        // Damping
        n.vx *= 0.85;
        n.vy *= 0.85;

        n.x += n.vx;
        n.y += n.vy;

        // Boundary padding
        const pad = n.radius + 10;
        n.x = Math.max(pad, Math.min(width - pad, n.x));
        n.y = Math.max(pad, Math.min(height - pad, n.y));
    });
}

function drawGraph() {
    if (!ctx || !canvas) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw Edges (Directed Arrows & Particles)
    graphData.edges.forEach(edge => {
        const src = nodePositions[edge.source];
        const tgt = nodePositions[edge.target];
        if (!src || !tgt) return;

        ctx.beginPath();
        ctx.moveTo(src.x, src.y);
        ctx.lineTo(tgt.x, tgt.y);

        let strokeColor = 'rgba(255, 255, 255, 0.12)';
        let lineWidth = 1.2;

        if (src.state === 'failed' && tgt.state === 'failed') {
            strokeColor = 'rgba(239, 68, 68, 0.7)';
            lineWidth = 2.5;
        } else if (src.state === 'failed') {
            strokeColor = 'rgba(245, 158, 11, 0.6)';
            lineWidth = 2.0;
        } else if (src.id === hoveredNode || tgt.id === hoveredNode) {
            strokeColor = 'rgba(96, 165, 250, 0.6)';
            lineWidth = 2.0;
        }

        ctx.strokeStyle = strokeColor;
        ctx.lineWidth = lineWidth;
        ctx.stroke();

        // Draw Arrowhead
        drawArrowHead(src, tgt, strokeColor);

        // Particle Pulses on Active Edges
        if (src.state === 'failed') {
            drawEdgeParticle(src, tgt, 'rgba(239, 68, 68, 0.9)');
        }
    });

    // Draw Nodes
    Object.values(nodePositions).forEach(node => {
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.radius, 0, 2 * Math.PI);

        let fillColor = '#10b981'; // Green
        let glowColor = 'rgba(16, 185, 129, 0.4)';

        if (node.state === 'failed') {
            fillColor = '#ef4444'; // Red
            glowColor = 'rgba(239, 68, 68, 0.85)';
        } else if (node.state === 'at-risk') {
            fillColor = '#f59e0b'; // Yellow
            glowColor = 'rgba(245, 158, 11, 0.7)';
        }

        if (node.id === selectedNode) {
            glowColor = 'rgba(59, 130, 246, 1.0)';
        }

        ctx.fillStyle = fillColor;
        ctx.shadowColor = glowColor;
        ctx.shadowBlur = (node.id === selectedNode || node.state === 'failed') ? 18 : 10;
        ctx.fill();
        ctx.shadowBlur = 0; // reset

        ctx.strokeStyle = (node.id === selectedNode) ? '#ffffff' : (node.id === hoveredNode ? '#60a5fa' : 'rgba(255, 255, 255, 0.25)');
        ctx.lineWidth = (node.id === selectedNode) ? 3.5 : (node.id === hoveredNode ? 2.5 : 1.5);
        ctx.stroke();

        // Node Label
        ctx.fillStyle = (node.id === selectedNode) ? '#ffffff' : '#e2e8f0';
        ctx.font = (node.id === selectedNode) ? '600 12px Inter, sans-serif' : '500 11px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(node.label, node.x, node.y + node.radius + 15);
    });
}

function drawArrowHead(src, tgt, color) {
    const angle = Math.atan2(tgt.y - src.y, tgt.x - src.x);
    const offset = tgt.radius + 4;

    const arrowX = tgt.x - offset * Math.cos(angle);
    const arrowY = tgt.y - offset * Math.sin(angle);

    ctx.beginPath();
    ctx.moveTo(arrowX, arrowY);
    ctx.lineTo(arrowX - 8 * Math.cos(angle - Math.PI / 6), arrowY - 8 * Math.sin(angle - Math.PI / 6));
    ctx.lineTo(arrowX - 8 * Math.cos(angle + Math.PI / 6), arrowY - 8 * Math.sin(angle + Math.PI / 6));
    ctx.closePath();
    ctx.fillStyle = color;
    ctx.fill();
}

function drawEdgeParticle(src, tgt, color) {
    const angle = Math.atan2(tgt.y - src.y, tgt.x - src.x);
    const dist = Math.hypot(tgt.x - src.x, tgt.y - src.y);
    const pDist = (particleOffset / 30) * dist;

    const px = src.x + pDist * Math.cos(angle);
    const py = src.y + pDist * Math.sin(angle);

    ctx.beginPath();
    ctx.arc(px, py, 3, 0, 2 * Math.PI);
    ctx.fillStyle = color;
    ctx.shadowColor = color;
    ctx.shadowBlur = 8;
    ctx.fill();
    ctx.shadowBlur = 0;
}

// Mouse Event Handlers
function getNodeAtPosition(x, y) {
    for (let node of Object.values(nodePositions)) {
        const dist = Math.hypot(x - node.x, y - node.y);
        if (dist <= node.radius + 6) return node;
    }
    return null;
}

function handleMouseDown(e) {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const clicked = getNodeAtPosition(x, y);
    if (clicked) {
        isDragging = true;
        draggedNode = clicked;
        selectedNode = clicked.id;
        document.getElementById('lbl-selected-node').innerText = selectedNode;
        loadTippingPoint();
        updateNodeInspector(clicked);
    }
}

function handleMouseMove(e) {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    if (isDragging && draggedNode) {
        draggedNode.x = x;
        draggedNode.y = y;
        draggedNode.vx = 0;
        draggedNode.vy = 0;
    } else {
        const hovered = getNodeAtPosition(x, y);
        if (hovered !== hoveredNode) {
            hoveredNode = hovered ? hovered.id : null;
            if (hovered) {
                updateNodeInspector(hovered);
            }
        }
    }
}

function handleMouseUp() {
    isDragging = false;
    draggedNode = null;
}

function updateNodeInspector(node) {
    const inspector = document.getElementById('node-inspector');
    if (!node) {
        inspector.classList.add('hidden');
        return;
    }

    inspector.classList.remove('hidden');
    document.getElementById('inspect-title').innerText = node.label;
    
    const statusBadge = document.getElementById('inspect-status');
    statusBadge.innerText = node.state.toUpperCase();
    statusBadge.className = `badge-status ${node.state}`;

    document.getElementById('inspect-cat').innerText = node.category;
    document.getElementById('inspect-deg').innerText = `${node.degree} (${node.inDegree} in / ${node.outDegree} out)`;

    // Find upstream deps
    const deps = graphData.edges.filter(e => e.target === node.id).map(e => e.source);
    document.getElementById('inspect-deps').innerText = deps.length > 0 ? deps.slice(0, 2).join(', ') + (deps.length > 2 ? '...' : '') : 'None (Root Node)';
}

function selectPreset(nodeId) {
    selectedNode = nodeId;
    document.getElementById('lbl-selected-node').innerText = selectedNode;
    if (nodePositions[nodeId]) {
        updateNodeInspector(nodePositions[nodeId]);
    }
    triggerCascade();
}

async function triggerCascade() {
    resetSimulation();
    try {
        const res = await fetch('/api/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                initialNodes: [selectedNode],
                threshold: currentThreshold,
                type: currentGraphMode
            })
        });

        simulationResult = await res.json();
        applySimulationStep(simulationResult.stepHistory.length - 1);
        populateCausalityLog(simulationResult);
    } catch (err) {
        console.error('Error triggering cascade:', err);
    }
}

function applySimulationStep(stepIdx) {
    if (!simulationResult || !simulationResult.stepHistory) return;

    currentStepIndex = stepIdx;

    const failedSoFar = new Set();
    for (let i = 0; i <= stepIdx; i++) {
        simulationResult.stepHistory[i].newlyFailed.forEach(id => failedSoFar.add(id));
    }

    graphData.nodes.forEach(node => {
        if (nodePositions[node.id]) {
            if (failedSoFar.has(node.id)) {
                nodePositions[node.id].state = 'failed';
            } else {
                nodePositions[node.id].state = 'healthy';
            }
        }
    });

    // Update Live Metrics
    const totalNodes = simulationResult.totalNodes;
    const failedCount = failedSoFar.size;
    const blastPct = ((failedCount / totalNodes) * 100).toFixed(1);
    const healthPct = (100 - blastPct).toFixed(1);

    document.getElementById('metric-health').innerText = `${healthPct}%`;
    document.getElementById('metric-blast').innerText = `${blastPct}%`;
    document.getElementById('metric-blast-nodes').innerText = `${failedCount} / ${totalNodes} Nodes Failed`;
    document.getElementById('metric-depth').innerText = `Step ${stepIdx} of ${simulationResult.totalTimesteps}`;
}

function populateCausalityLog(result) {
    const logContainer = document.getElementById('causalityLog');
    const stepSummary = document.getElementById('lbl-step-summary');
    logContainer.innerHTML = '';

    stepSummary.innerText = `Blast Radius: ${result.blastRadiusPercentage}% (${result.totalFailedNodes}/${result.totalNodes} nodes) in ${result.totalTimesteps} steps`;

    result.stepHistory.forEach(step => {
        const div = document.createElement('div');
        if (step.timestep === 0) {
            div.className = 'log-entry trigger';
            div.innerText = `[t=0] 🚨 TRIGGER INITIALIZED: Primary failure triggered at [${step.newlyFailed.join(', ')}]`;
        } else {
            div.className = 'log-entry collapse';
            div.innerText = `[t=${step.timestep}] 💥 CASCADE STEP: ${step.newlyFailed.length} nodes collapsed [${step.newlyFailed.join(', ')}] (Exceeded threshold θ=${result.thresholdUsed})`;
        }
        logContainer.appendChild(div);
    });

    logContainer.scrollTop = logContainer.scrollHeight;
}

function togglePlayback() {
    if (!simulationResult) {
        triggerCascade().then(() => startPlayback());
    } else if (isPlaying) {
        pausePlayback();
    } else {
        startPlayback();
    }
}

function startPlayback() {
    isPlaying = true;
    document.getElementById('btn-play').innerText = '⏸ Pause';
    if (currentStepIndex >= simulationResult.stepHistory.length - 1) {
        currentStepIndex = 0;
    }
    
    playbackTimer = setInterval(() => {
        if (currentStepIndex < simulationResult.stepHistory.length - 1) {
            applySimulationStep(currentStepIndex + 1);
        } else {
            pausePlayback();
        }
    }, 900);
}

function pausePlayback() {
    isPlaying = false;
    document.getElementById('btn-play').innerText = '▶ Play Step-by-Step';
    if (playbackTimer) clearInterval(playbackTimer);
}

function resetSimulation() {
    pausePlayback();
    simulationResult = null;
    currentStepIndex = 0;
    
    if (graphData.nodes) {
        graphData.nodes.forEach(n => {
            if (nodePositions[n.id]) nodePositions[n.id].state = 'healthy';
        });
    }

    document.getElementById('metric-health').innerText = '100.0%';
    document.getElementById('metric-blast').innerText = '0.0%';
    document.getElementById('metric-blast-nodes').innerText = `0 / ${graphData.nodes.length} Nodes Failed`;
    document.getElementById('metric-depth').innerText = '0 steps';

    document.getElementById('causalityLog').innerHTML = `
        <div class="log-entry info">System initialized in operational equilibrium. Click a node and run cascade to trace step-by-step collapse causality.</div>
    `;
    document.getElementById('lbl-step-summary').innerText = 'Ready for simulation trigger';
}

function updateThreshold(val) {
    currentThreshold = parseFloat(val);
    document.getElementById('val-threshold').innerText = parseFloat(val).toFixed(2);
    loadRiskScores();
}

function filterLeaderboard(searchTerm) {
    const term = searchTerm.toLowerCase();
    const rows = document.querySelectorAll('#tbody-leaderboard tr');
    rows.forEach(row => {
        const text = row.innerText.toLowerCase();
        row.style.display = text.includes(term) ? '' : 'none';
    });
}

async function loadRiskScores() {
    try {
        const res = await fetch(`/api/risk-scores?type=${currentGraphMode}&threshold=${currentThreshold}`);
        const scores = await res.json();
        
        const tbody = document.getElementById('tbody-leaderboard');
        tbody.innerHTML = '';

        scores.forEach((item, index) => {
            const tr = document.createElement('tr');
            const classification = item.isHiddenCriticalNode 
                ? '<span class="badge pink">⚠️ Hidden Single Point</span>' 
                : (item.degree >= 7 ? '<span class="badge red">High Connection Hub</span>' : '<span class="badge gray">Standard Node</span>');

            tr.innerHTML = `
                <td><strong>#${index + 1}</strong></td>
                <td>${item.node}</td>
                <td>${item.degree}</td>
                <td>${item.blastRadiusPercentage}%</td>
                <td><strong class="highlight">${item.cascadeRiskScore}</strong></td>
                <td>${classification}</td>
            `;

            tr.style.cursor = 'pointer';
            tr.onclick = () => {
                selectedNode = item.node;
                document.getElementById('lbl-selected-node').innerText = selectedNode;
                if (nodePositions[item.node]) {
                    updateNodeInspector(nodePositions[item.node]);
                }
                loadTippingPoint();
            };

            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error('Error loading risk scores:', err);
    }
}

async function loadTippingPoint() {
    try {
        const res = await fetch('/api/tipping-point', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                triggerNodes: [selectedNode],
                type: currentGraphMode
            })
        });

        const data = await res.json();
        document.getElementById('badge-tipping').innerText = `Tipping Point: θ = ${data.tippingPointThreshold.toFixed(2)}`;
        renderTippingChart(data.curve, data.tippingPointThreshold);
    } catch (err) {
        console.error('Error loading tipping point:', err);
    }
}

function renderTippingChart(curveData, tippingPointThreshold) {
    const ctxChart = document.getElementById('tippingChart').getContext('2d');
    const labels = curveData.map(d => `θ=${d.threshold}`);
    const values = curveData.map(d => d.systemCollapsePercentage);

    if (tippingChart) tippingChart.destroy();

    tippingChart = new Chart(ctxChart, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'System Collapse %',
                data: values,
                borderColor: '#ef4444',
                backgroundColor: 'rgba(239, 68, 68, 0.15)',
                borderWidth: 3,
                fill: true,
                tension: 0.3,
                pointRadius: 4,
                pointBackgroundColor: '#ef4444'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8', font: { size: 10 } }
                },
                y: {
                    min: 0,
                    max: 100,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8', font: { size: 10 }, callback: v => v + '%' }
                }
            }
        }
    });
}

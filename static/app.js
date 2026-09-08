// CascadeSight Dashboard - Frontend Logic

let currentGraphMode = 'synthetic';
let graphData = { nodes: [], edges: [] };
let selectedNode = 'Internal Config Service';
let currentThreshold = 0.40;

let simulationResult = null;
let currentStepIndex = 0;
let playbackTimer = null;
let isPlaying = false;

// Canvas & Context
let canvas = null;
let ctx = null;
let nodePositions = {}; // id -> {x, y, vx, vy, radius}

// Chart Instance
let tippingChart = null;

document.addEventListener('DOMContentLoaded', () => {
    canvas = document.getElementById('graphCanvas');
    ctx = canvas.getContext('2d');
    resizeCanvas();

    window.addEventListener('resize', resizeCanvas);
    canvas.addEventListener('click', handleCanvasClick);

    // Initial Load
    initDashboard();
});

function resizeCanvas() {
    if (!canvas) return;
    const rect = canvas.parentElement.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;
    if (graphData.nodes.length > 0) {
        drawGraph();
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

    if (mode === 'meta') {
        selectedNode = 'Backbone BGP Router Config';
    } else {
        selectedNode = 'Internal Config Service';
    }
    
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
    const height = canvas.height || 500;
    const centerX = width / 2;
    const centerY = height / 2;
    const numNodes = graphData.nodes.length;
    const radius = Math.min(width, height) * 0.35;

    nodePositions = {};

    graphData.nodes.forEach((node, i) => {
        // Arrange initially in circle layout with slight jitter
        const angle = (i / numNodes) * 2 * Math.PI;
        nodePositions[node.id] = {
            x: centerX + radius * Math.cos(angle),
            y: centerY + radius * Math.sin(angle),
            radius: 14 + (node.degree || 1) * 1.5,
            state: 'healthy' // 'healthy', 'at-risk', 'failed'
        };
    });
}

function drawGraph() {
    if (!ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw Edges (Directed Dependency Arrows)
    graphData.edges.forEach(edge => {
        const src = nodePositions[edge.source];
        const tgt = nodePositions[edge.target];
        if (!src || !tgt) return;

        ctx.beginPath();
        ctx.moveTo(src.x, src.y);
        ctx.lineTo(tgt.x, tgt.y);
        
        let strokeColor = 'rgba(255, 255, 255, 0.15)';
        if (src.state === 'failed' && tgt.state === 'failed') {
            strokeColor = 'rgba(239, 68, 68, 0.6)';
        } else if (src.state === 'failed') {
            strokeColor = 'rgba(245, 158, 11, 0.5)';
        }
        
        ctx.strokeStyle = strokeColor;
        ctx.lineWidth = (src.state === 'failed') ? 2 : 1;
        ctx.stroke();

        // Draw arrow head
        drawArrowHead(src, tgt, strokeColor);
    });

    // Draw Nodes
    graphData.nodes.forEach(node => {
        const pos = nodePositions[node.id];
        if (!pos) return;

        ctx.beginPath();
        ctx.arc(pos.x, pos.y, pos.radius, 0, 2 * Math.PI);

        let fillColor = '#10b981'; // Green
        let glowColor = 'rgba(16, 185, 129, 0.4)';

        if (pos.state === 'failed') {
            fillColor = '#ef4444'; // Red
            glowColor = 'rgba(239, 68, 68, 0.8)';
        } else if (pos.state === 'at-risk') {
            fillColor = '#f59e0b'; // Yellow
            glowColor = 'rgba(245, 158, 11, 0.6)';
        }

        if (node.id === selectedNode) {
            glowColor = 'rgba(59, 130, 246, 1.0)';
        }

        ctx.fillStyle = fillColor;
        ctx.shadowColor = glowColor;
        ctx.shadowBlur = 12;
        ctx.fill();
        ctx.shadowBlur = 0; // reset

        ctx.strokeStyle = (node.id === selectedNode) ? '#ffffff' : 'rgba(255, 255, 255, 0.3)';
        ctx.lineWidth = (node.id === selectedNode) ? 3 : 1.5;
        ctx.stroke();

        // Label
        ctx.fillStyle = '#f3f4f6';
        ctx.font = '11px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(node.label || node.id, pos.x, pos.y + pos.radius + 14);
    });
}

function drawArrowHead(src, tgt, color) {
    const angle = Math.atan2(tgt.y - src.y, tgt.x - src.x);
    const dist = Math.hypot(tgt.x - src.x, tgt.y - src.y);
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

function handleCanvasClick(e) {
    const rect = canvas.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const clickY = e.clientY - rect.top;

    for (let node of graphData.nodes) {
        const pos = nodePositions[node.id];
        if (!pos) continue;
        const dist = Math.hypot(clickX - pos.x, clickY - pos.y);
        if (dist <= pos.radius + 5) {
            selectedNode = node.id;
            document.getElementById('lbl-selected-node').innerText = selectedNode;
            drawGraph();
            loadTippingPoint();
            break;
        }
    }
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
    } catch (err) {
        console.error('Error triggering cascade:', err);
    }
}

function applySimulationStep(stepIdx) {
    if (!simulationResult || !simulationResult.stepHistory) return;

    currentStepIndex = stepIdx;
    const step = simulationResult.stepHistory[stepIdx];

    // Update node states
    const failedSoFar = new Set();
    for (let i = 0; i <= stepIdx; i++) {
        simulationResult.stepHistory[i].newlyFailed.forEach(id => failedSoFar.add(id));
    }

    graphData.nodes.forEach(node => {
        if (failedSoFar.has(node.id)) {
            nodePositions[node.id].state = 'failed';
        } else {
            nodePositions[node.id].state = 'healthy';
        }
    });

    drawGraph();

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
    }, 800);
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

    drawGraph();

    document.getElementById('metric-health').innerText = '100.0%';
    document.getElementById('metric-blast').innerText = '0.0%';
    document.getElementById('metric-blast-nodes').innerText = `0 / ${graphData.nodes.length} Nodes Failed`;
    document.getElementById('metric-depth').innerText = '0 steps';
}

function updateThreshold(val) {
    currentThreshold = parseFloat(val);
    document.getElementById('val-threshold').innerText = parseFloat(val).toFixed(2);
    loadRiskScores();
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
                : (item.degree >= 8 ? '<span class="badge red">High Connection Hub</span>' : '<span class="badge gray">Standard Node</span>');

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
                drawGraph();
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
                    ticks: { color: '#9ca3af', font: { size: 10 } }
                },
                y: {
                    min: 0,
                    max: 100,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#9ca3af', font: { size: 10 }, callback: v => v + '%' }
                }
            }
        }
    });
}

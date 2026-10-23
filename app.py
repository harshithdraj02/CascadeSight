"""
CascadeSight - Web Application Server
Flask REST API and web server delivering interactive graph visualization,
live cascade simulation, risk leaderboards, and tipping point analysis.
"""

from flask import Flask, jsonify, request, send_from_directory
import os
import sys
import webbrowser
import threading
import networkx as nx

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from core.graph_engine import DependencyGraphEngine
from core.cascade_model import CascadeSimulator
from core.risk_scorer import CascadeRiskScorer
from core.tipping_point import TippingPointAnalyzer
from core.case_study import MetaOct2021CaseStudy
from core.remediation import ArchitecturalRemediationEngine
from core.ingestion import InfrastructureIngestionEngine

app = Flask(__name__, static_folder='static', static_url_path='')

graph_engine = DependencyGraphEngine()
synthetic_graph = graph_engine.create_synthetic_infrastructure()
meta_graph = graph_engine.get_meta_october_2021_graph()
custom_graph = None

def get_target_graph(graph_type: str = "synthetic") -> nx.DiGraph:
    if graph_type == "meta":
        return meta_graph
    if graph_type == "custom" and custom_graph is not None:
        return custom_graph
    return synthetic_graph

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/api/graph', methods=['GET'])
def get_graph():
    g_type = request.args.get('type', 'synthetic')
    g = get_target_graph(g_type)
    return jsonify(graph_engine.to_json_dict(g))

@app.route('/api/simulate', methods=['POST'])
def simulate():
    data = request.json or {}
    initial_nodes = data.get('initialNodes', ['Internal Config Service'])
    threshold = float(data.get('threshold', 0.40))
    g_type = data.get('type', 'synthetic')

    g = get_target_graph(g_type)
    simulator = CascadeSimulator(g, default_threshold=threshold)
    result = simulator.simulate_cascade(initial_nodes, threshold=threshold)
    return jsonify(result)

@app.route('/api/risk-scores', methods=['GET'])
def get_risk_scores():
    g_type = request.args.get('type', 'synthetic')
    threshold = float(request.args.get('threshold', 0.40))
    g = get_target_graph(g_type)

    scorer = CascadeRiskScorer(g)
    scores = scorer.calculate_all_scores(threshold=threshold)
    return jsonify(scores)

@app.route('/api/tipping-point', methods=['POST'])
def get_tipping_point():
    data = request.json or {}
    trigger_nodes = data.get('triggerNodes', ['Internal Config Service'])
    g_type = data.get('type', 'synthetic')
    g = get_target_graph(g_type)

    analyzer = TippingPointAnalyzer(g)
    result = analyzer.analyze_threshold_sensitivity(trigger_nodes)
    return jsonify(result)

import threading
import webbrowser

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "CascadeSight", "version": "1.0.0"})

@app.route('/api/case-study', methods=['GET'])
def get_case_study():
    cs = MetaOct2021CaseStudy()
    return jsonify(cs.run_post_mortem_analysis())

@app.route('/api/remediation', methods=['POST'])
def run_remediation():
    data = request.json or {}
    target_node = data.get('targetNode', 'Internal Config Service')
    threshold = float(data.get('threshold', 0.40))
    g_type = data.get('type', 'synthetic')
    g = get_target_graph(g_type)

    engine = ArchitecturalRemediationEngine(g)
    result = engine.evaluate_mitigation(target_node, threshold=threshold)
    return jsonify(result)

@app.route('/api/import-architecture', methods=['POST'])
def import_architecture():
    global custom_graph
    data = request.json or {}
    content = data.get('content', '')
    format_type = data.get('format', 'docker-compose') # 'docker-compose' or 'json'

    try:
        if format_type == 'json':
            custom_graph = InfrastructureIngestionEngine.parse_architecture_json(content)
        else:
            custom_graph = InfrastructureIngestionEngine.parse_docker_compose(content)

        node_count = custom_graph.number_of_nodes()
        edge_count = custom_graph.number_of_edges()

        if node_count == 0:
            return jsonify({"success": False, "error": "Imported architecture has 0 services."}), 400

        return jsonify({
            "success": True,
            "message": f"Successfully parsed {node_count} microservices and {edge_count} dependency edges.",
            "totalNodes": node_count,
            "totalEdges": edge_count,
            "graph": graph_engine.to_json_dict(custom_graph)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/audit-report', methods=['GET'])
def get_audit_report():
    g_type = request.args.get('type', 'synthetic')
    threshold = float(request.args.get('threshold', 0.40))
    g = get_target_graph(g_type)

    scorer = CascadeRiskScorer(g)
    scores = scorer.calculate_all_scores(threshold=threshold)
    hspof_nodes = [s for s in scores if s.get('isHiddenCriticalNode', False)]

    # Calculate System Fragility Index
    avg_blast = sum(s['blastRadiusPercentage'] for s in scores) / max(len(scores), 1)
    max_crs = scores[0]['cascadeRiskScore'] if scores else 0
    fragility_grade = "CRITICAL (A+ Risk)" if max_crs > 8.0 else ("HIGH (B Risk)" if max_crs > 4.0 else "RESILIENT (Low Risk)")

    report = {
        "reportId": f"DORA-AUDIT-2026-X{len(scores)}",
        "timestamp": "2026-10-23T21:30:00Z",
        "architectureType": g_type.upper(),
        "totalMicroservices": g.number_of_nodes(),
        "totalDependencyEdges": g.number_of_edges(),
        "systemFragilityGrade": fragility_grade,
        "averageBlastRadius": round(avg_blast, 1),
        "totalHSPOFsIdentified": len(hspof_nodes),
        "topSystemicThreat": scores[0] if scores else {},
        "regulatoryCompliance": {
            "doraArticle11_ICTConcentration": "NON-COMPLIANT" if len(hspof_nodes) > 0 else "COMPLIANT",
            "iso22301_BusinessContinuity": "ACTION_REQUIRED" if max_crs > 5.0 else "VERIFIED"
        },
        "recommendedArchitecturalPatches": [
            f"Deploy Circuit Breaker Pattern on '{scores[0]['node']}' to isolate downstream blast wave.",
            "Implement async message queue decoupling for high-blast choke points.",
            "Enforce local stale-while-revalidate caching layers for all single-upstream consumers."
        ]
    }
    return jsonify(report)

def open_browser(port):
    try:
        webbrowser.open(f'http://localhost:{port}')
    except Exception as e:
        print(f"Could not open browser automatically: {e}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n========================================================")
    print(f"[+] CascadeSight Web Dashboard Server Started!")
    print(f"[+] Access Dashboard locally at: http://localhost:{port}")
    print(f"========================================================\n")

    # Auto-open browser in non-reloader thread
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        threading.Timer(1.2, open_browser, args=[port]).start()

    app.run(host='0.0.0.0', port=port, debug=True)

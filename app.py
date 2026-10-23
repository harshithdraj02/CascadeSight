"""
CascadeSight - Web Application Server
Flask REST API and web server delivering interactive graph visualization,
live cascade simulation, risk leaderboards, and tipping point analysis.
"""

from flask import Flask, jsonify, request, send_from_directory
import os
import sys
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

app = Flask(__name__, static_folder='static', static_url_path='')

graph_engine = DependencyGraphEngine()
synthetic_graph = graph_engine.create_synthetic_infrastructure()
meta_graph = graph_engine.get_meta_october_2021_graph()

def get_target_graph(graph_type: str = "synthetic") -> nx.DiGraph:
    if graph_type == "meta":
        return meta_graph
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


"""
CascadeSight - CLI Terminal Demo Application
Runs interactive terminal demonstration of graph cascades, CRS rankings, 
tipping point analysis, and Meta case study validation.
"""

import sys
import time

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

def print_header(title: str):
    print("\n" + "=" * 70)
    print(f"   {title.upper()}")
    print("=" * 70)

def run_synthetic_demo():
    print_header("CascadeSight — Synthetic Infrastructure Demo")
    engine = DependencyGraphEngine()
    graph = engine.create_synthetic_infrastructure()
    
    print(f"[+] Loaded Graph: {graph.number_of_nodes()} Nodes | {graph.number_of_edges()} Directed Dependency Edges")
    
    # 1. Risk Scoring
    print("\n[*] Calculating Cascade Risk Scores (CRS) across all nodes...")
    scorer = CascadeRiskScorer(graph)
    scores = scorer.calculate_all_scores(threshold=0.40)
    
    print("\n--- TOP SYSTEMIC RISK RANKINGS ---")
    print(f"{'Rank':<5} | {'Node Name':<30} | {'Deg':<4} | {'Blast %':<8} | {'CRS':<6} | {'Hidden Danger'}")
    print("-" * 75)
    
    for rank, item in enumerate(scores[:7], 1):
        danger_flag = "⚠️  YES (HSPOF)" if item["isHiddenCriticalNode"] else "   No"
        print(f"{rank:<5} | {item['node'][:30]:<30} | {item['degree']:<4} | {item['blastRadiusPercentage']:<8.1f} | {item['cascadeRiskScore']:<6.2f} | {danger_flag}")

    # 2. Triggering Cascade on Top Hidden Danger Node
    top_node = scores[0]["node"]
    print(f"\n[*] Demonstrating Live Cascade starting from: [{top_node}]")
    simulator = CascadeSimulator(graph, default_threshold=0.40)
    result = simulator.simulate_cascade([top_node])
    
    print("\n--- TIMESTEP CASCADE EVOLUTION ---")
    for step in result["stepHistory"]:
        ts = step["timestep"]
        health = step["systemHealthPercentage"]
        failed = step["totalFailedCount"]
        newly = ", ".join(step["newlyFailed"])
        print(f"Timestep t={ts:<2} | System Health: {health:>5.1f}% | Total Failed: {failed:>2}/{graph.number_of_nodes()} | Newly Failed: [{newly}]")

    print(f"\n[✓] Final Blast Radius: {result['blastRadiusPercentage']}% collapse across {result['totalFailedNodes']} nodes in {result['totalTimesteps']} steps.")

    # 3. Tipping Point Analysis
    print_header("Tipping Point (Percolation Threshold) Analysis")
    analyzer = TippingPointAnalyzer(graph)
    tp_res = analyzer.analyze_threshold_sensitivity([top_node])
    
    print(f"Trigger Node: [{top_node}]")
    if tp_res.get('tippingPointDetected') and tp_res.get('tippingPointThreshold') is not None:
        tp_th = tp_res['tippingPointThreshold']
        print(f"Identified Percolation Tipping Point: Threshold = {tp_th:.2f}")
    else:
        tp_th = None
        print("Percolation Sensitivity: Stable curve (no single sharp phase cliff detected)")

    print("\n--- NON-LINEAR DEGRADATION CURVE ---")
    print(f"{'Threshold (θ)':<15} | {'Collapse %':<12} | {'Visual Bar'}")
    print("-" * 50)
    for pt in tp_res["curve"]:
        th_val = pt["threshold"]
        coll = pt["systemCollapsePercentage"]
        bar = "█" * int(coll / 5)
        marker = " 👈 TIPPING POINT" if (tp_th is not None and abs(th_val - tp_th) < 0.01) else ""
        print(f"θ = {th_val:<11.2f} | {coll:>5.1f}%      | {bar}{marker}")

def run_meta_case_study():
    print_header("Case Study: Meta (Facebook) Outage — Oct 4, 2021")
    cs = MetaOct2021CaseStudy()
    res = cs.run_post_mortem_analysis()
    
    print(f"Case Study: {res['caseStudyName']}")
    print(f"Incident Origin Node  : [{res['incidentOriginNode']}]")
    print(f"Top CRS Scoring Node  : [{res['topScoringNode']}]")
    print(f"Model Outcome         : {'[MATCH] Incident Root Ranks #1 in Post-Mortem Model' if res['originRanksFirst'] else '[MISMATCH]'}")
    print(f"Methodology Note      : {res['methodologyNote']}")
    
    print("\n--- META GRAPH RANKINGS ---")
    for r, item in enumerate(res["rankedRiskScores"][:5], 1):
        print(f"Rank {r}: {item['node']} (Degree: {item['degree']}, Blast: {item['blastRadiusPercentage']}%, CRS: {item['cascadeRiskScore']})")

def main():
    print_header("CascadeSight — Technical Prototype Initialized")
    run_synthetic_demo()
    run_meta_case_study()
    print("\n[+] Prototype run completed successfully.")
    print("[+] To start the Web Dashboard, run: python app.py\n")

if __name__ == "__main__":
    main()

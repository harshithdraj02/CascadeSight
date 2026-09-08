"""
CascadeSight - Tipping Point Analyzer Module
Computes non-linear degradation curves and percolation tipping points.
"""

import networkx as nx
from typing import Dict, List, Any
from core.cascade_model import CascadeSimulator

class TippingPointAnalyzer:
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph

    def analyze_threshold_sensitivity(self, trigger_nodes: List[str]) -> Dict[str, Any]:
        """
        Varies the dependency cascade threshold theta from 0.10 to 0.90 in increments of 0.05.
        Generates a non-linear tipping point degradation curve.
        """
        simulator = CascadeSimulator(self.graph)
        thresholds = [round(t * 0.05, 2) for t in range(2, 19)]  # 0.10 to 0.90
        
        curve_data = []
        max_jump = 0.0
        tipping_point_threshold = 0.40

        prev_collapse = 0.0

        for th in thresholds:
            sim_res = simulator.simulate_cascade(trigger_nodes, threshold=th)
            collapse_pct = sim_res["blastRadiusPercentage"]
            
            jump = collapse_pct - prev_collapse
            if jump > max_jump:
                max_jump = jump
                tipping_point_threshold = th
                
            curve_data.append({
                "threshold": th,
                "sensitivityPercentage": round(th * 100, 1),
                "systemCollapsePercentage": collapse_pct,
                "systemHealthPercentage": round(100 - collapse_pct, 1),
                "totalFailedNodes": sim_res["totalFailedNodes"]
            })
            
            prev_collapse = collapse_pct

        return {
            "triggerNodes": trigger_nodes,
            "tippingPointThreshold": tipping_point_threshold,
            "maxCollapseDelta": max_jump,
            "curve": curve_data
        }

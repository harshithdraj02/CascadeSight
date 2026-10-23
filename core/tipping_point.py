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
        Generates a non-linear tipping point degradation curve and identifies the percolation
        cliff where system survival drops most sharply.
        """
        simulator = CascadeSimulator(self.graph)
        thresholds = [round(t * 0.05, 2) for t in range(2, 19)]  # 0.10 to 0.90
        
        curve_data = []

        # 1. Collect collapse percentage across all thresholds
        for th in thresholds:
            sim_res = simulator.simulate_cascade(trigger_nodes, threshold=th)
            collapse_pct = sim_res["blastRadiusPercentage"]
            curve_data.append({
                "threshold": th,
                "sensitivityPercentage": round(th * 100, 1),
                "systemCollapsePercentage": collapse_pct,
                "systemHealthPercentage": round(100.0 - collapse_pct, 1),
                "totalFailedNodes": sim_res["totalFailedNodes"]
            })

        # 2. Compute forward difference: Delta_i = Collapse(th_i) - Collapse(th_i+1)
        # As tolerance threshold increases, failure is non-increasing.
        # The tipping point theta_c is the threshold immediately preceding the largest drop.
        max_drop = 0.0
        tipping_point_threshold = thresholds[0]
        tipping_point_detected = False

        for i in range(len(curve_data) - 1):
            drop = curve_data[i]["systemCollapsePercentage"] - curve_data[i + 1]["systemCollapsePercentage"]
            if drop > max_drop and drop > 0.0:
                max_drop = round(drop, 2)
                tipping_point_threshold = thresholds[i]
                tipping_point_detected = True

        return {
            "triggerNodes": trigger_nodes,
            "tippingPointThreshold": tipping_point_threshold if tipping_point_detected else None,
            "tippingPointDetected": tipping_point_detected,
            "maxCollapseDelta": max_drop,
            "curve": curve_data
        }

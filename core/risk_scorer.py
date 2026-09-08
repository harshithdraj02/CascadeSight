"""
CascadeSight - Risk Scorer Module
Computes Cascade Risk Score (CRS) across all nodes to identify non-obvious,
hidden critical single points of failure.
"""

import networkx as nx
from typing import Dict, List, Any
from core.cascade_model import CascadeSimulator

class CascadeRiskScorer:
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph

    def calculate_all_scores(self, threshold: float = 0.40) -> List[Dict[str, Any]]:
        """
        Computes CRS for every node in the graph and ranks them.
        Formula:
            CRS = (Blast Radius %)^2 / (100 * Degree Centrality)
            
        This quadratic scaling ensures that low-impact isolated nodes are not falsely 
        flagged as high risk, while non-obvious nodes with moderate degree but massive 
        downstream blast radius emerge as the top systemic hazards.
        """
        simulator = CascadeSimulator(self.graph, default_threshold=threshold)
        results = []

        for node in self.graph.nodes():
            sim_res = simulator.simulate_cascade([node], threshold=threshold)
            blast_radius_pct = sim_res["blastRadiusPercentage"]
            total_failed_count = sim_res["totalFailedNodes"]
            cascade_depth = sim_res["totalTimesteps"]
            
            in_deg = self.graph.in_degree(node)
            out_deg = self.graph.out_degree(node)
            total_deg = in_deg + out_deg
            effective_deg = max(total_deg, 1)
            
            # Refined Cascade Risk Score (CRS) Formula
            raw_crs = (blast_radius_pct ** 2) / (100.0 * effective_deg)
            crs = round(raw_crs, 2)
            
            # Is this a Hidden Critical Single Point of Failure?
            # Criteria: Degree <= 8 AND Blast Radius >= 50%
            is_hidden_danger = (total_deg <= 8) and (blast_radius_pct >= 50.0)

            results.append({
                "node": node,
                "label": self.graph.nodes[node].get("label", node),
                "category": self.graph.nodes[node].get("category", "default"),
                "degree": total_deg,
                "inDegree": in_deg,
                "outDegree": out_deg,
                "blastRadiusPercentage": blast_radius_pct,
                "totalFailedNodes": total_failed_count,
                "cascadeDepth": cascade_depth,
                "cascadeRiskScore": crs,
                "isHiddenCriticalNode": is_hidden_danger
            })

        # Sort descending by Cascade Risk Score (CRS)
        results.sort(key=lambda x: x["cascadeRiskScore"], reverse=True)
        return results

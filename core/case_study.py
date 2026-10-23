"""
CascadeSight - Case Study Module
Explanatory Post-Mortem Modeling of Meta's October 4, 2021 global outage topology.
Illustrates how published post-mortem incident dependencies can be formalized and analyzed
via discrete-time threshold percolation modeling.
"""

from core.graph_engine import DependencyGraphEngine
from core.risk_scorer import CascadeRiskScorer
from core.cascade_model import CascadeSimulator
from typing import Dict, Any

class MetaOct2021CaseStudy:
    def __init__(self):
        engine = DependencyGraphEngine()
        self.graph = engine.get_meta_october_2021_graph()

    def run_post_mortem_analysis(self) -> Dict[str, Any]:
        """
        Executes cascade simulation and risk scoring on the formalized post-mortem topology.
        Demonstrates that formalizing the published failure chain places the BGP router configuration
        at the top of the Cascade Risk Score hierarchy.
        """
        scorer = CascadeRiskScorer(self.graph)
        scores = scorer.calculate_all_scores(threshold=0.30)
        
        # Trigger cascade from the documented incident origin node
        simulator = CascadeSimulator(self.graph, default_threshold=0.30)
        origin_node = "Backbone BGP Router Config"
        cascade_result = simulator.simulate_cascade([origin_node], threshold=0.30)
        
        top_risk_node = scores[0]["node"] if scores else None
        origin_ranks_first = (top_risk_node == origin_node)

        return {
            "caseStudyName": "Meta Global Outage (October 4, 2021) — Post-Mortem Model",
            "incidentOriginNode": origin_node,
            "topScoringNode": top_risk_node,
            "originRanksFirst": origin_ranks_first,
            "totalNodesInGraph": self.graph.number_of_nodes(),
            "cascadeResult": cascade_result,
            "rankedRiskScores": scores,
            "methodologyNote": "Constructed from Meta's published post-mortem report to illustrate threshold percolation dynamics on multi-tier lockout loops."
        }

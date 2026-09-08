"""
CascadeSight - Case Study Module
Validates CascadeSight risk scoring methodology against Meta's October 4, 2021 outage.
"""

from core.graph_engine import DependencyGraphEngine
from core.risk_scorer import CascadeRiskScorer
from core.cascade_model import CascadeSimulator
from typing import Dict, Any

class MetaOct2021CaseStudy:
    def __init__(self):
        engine = DependencyGraphEngine()
        self.graph = engine.get_meta_october_2021_graph()

    def run_validation(self) -> Dict[str, Any]:
        """
        Executes cascade simulation and risk scoring on the Meta outage graph.
        """
        scorer = CascadeRiskScorer(self.graph)
        scores = scorer.calculate_all_scores(threshold=0.30)
        
        # Trigger cascade from the historical origin node
        simulator = CascadeSimulator(self.graph, default_threshold=0.30)
        origin_node = "Backbone BGP Router Config"
        cascade_result = simulator.simulate_cascade([origin_node], threshold=0.30)
        
        top_risk_node = scores[0]["node"] if scores else None
        matches_historical_truth = (top_risk_node == origin_node)

        return {
            "caseStudyName": "Meta Global Outage (October 4, 2021)",
            "historicalOriginNode": origin_node,
            "topScoringNode": top_risk_node,
            "matchesHistoricalTruth": matches_historical_truth,
            "totalNodesInGraph": self.graph.number_of_nodes(),
            "cascadeResult": cascade_result,
            "rankedRiskScores": scores
        }

"""
Tests for core.risk_scorer.CascadeRiskScorer
Verifies exact numerical reconciliation, baseline comparative scoring,
and behavior across canonical structural topologies.
"""

import pytest
import networkx as nx
from core.graph_engine import DependencyGraphEngine
from core.risk_scorer import CascadeRiskScorer

def test_reconciled_synthetic_infrastructure_scores():
    """
    CRITICAL REQUIREMENT: Verify that the 20-node synthetic graph at threshold 0.40
    produces the exact figures cited across documentation:
    - Internal Config Service: Degree 7, Blast 80.0%, CRS 9.14, HSPOF = True.
    - Rank 1 on leaderboard.
    """
    engine = DependencyGraphEngine()
    graph = engine.create_synthetic_infrastructure()
    assert graph.number_of_nodes() == 20

    scorer = CascadeRiskScorer(graph)
    scores = scorer.calculate_all_scores(threshold=0.40)

    top_node = scores[0]
    assert top_node["node"] == "Internal Config Service"
    assert top_node["degree"] == 7
    assert top_node["inDegree"] == 0
    assert top_node["outDegree"] == 7
    assert top_node["blastRadiusPercentage"] == 80.0
    assert top_node["totalFailedNodes"] == 16
    assert top_node["cascadeRiskScore"] == 9.14
    assert top_node["isHiddenCriticalNode"] is True

def test_canonical_star_topology():
    """
    On a canonical star graph where center 'hub' has 5 outgoing dependencies to leaves:
    - Hub degree: 5, blast radius: 100.0%, CRS: (100^2)/(100*5) = 20.0
    - Leaves: degree 1, blast radius: 1/6 (16.67%), CRS: (16.67^2)/(100*1) = 2.78
    Both degree centrality and CRS must agree that the hub is the top risk.
    """
    graph = nx.DiGraph()
    hub = "hub"
    leaves = [f"leaf_{i}" for i in range(5)]
    for l in leaves:
        graph.add_edge(hub, l)

    scorer = CascadeRiskScorer(graph)
    scores = scorer.calculate_all_scores(threshold=0.40)

    assert scores[0]["node"] == hub
    assert scores[0]["cascadeRiskScore"] == 20.0
    assert scores[0]["blastRadiusPercentage"] == 100.0
    for leaf_score in scores[1:]:
        assert leaf_score["cascadeRiskScore"] < 5.0

def test_canonical_choke_point_bridge():
    """
    On an asymmetric choke-point bridge topology:
    Dense cluster A (root) -> Bridge node B (low degree: in=1, out=3) -> Cluster C (3 nodes).
    A high-degree leaf in Cluster C has degree 4 but low cascade blast.
    Bridge node B triggers collapse of Cluster C (blast >= 50%), so CRS elevates it.
    """
    graph = nx.DiGraph()
    graph.add_edge("root", "bridge")
    for i in range(3):
        graph.add_edge("bridge", f"worker_{i}")

    scorer = CascadeRiskScorer(graph)
    scores = scorer.calculate_all_scores(threshold=0.40)

    # Root triggers 100% collapse (5/5 nodes)
    # Bridge triggers 4/5 nodes (80.0% blast), degree=4, CRS=(80^2)/(400) = 16.0
    bridge_score = next(s for s in scores if s["node"] == "bridge")
    assert bridge_score["blastRadiusPercentage"] == 80.0
    assert bridge_score["degree"] == 4
    assert bridge_score["cascadeRiskScore"] == 16.0
    assert bridge_score["isHiddenCriticalNode"] is True

def test_isolated_node_zero_degree_boundary():
    """
    Edge case: Isolated node with degree 0 must use effective_degree = 1
    without raising ZeroDivisionError.
    """
    graph = nx.DiGraph()
    graph.add_node("isolated")

    scorer = CascadeRiskScorer(graph)
    scores = scorer.calculate_all_scores(threshold=0.40)

    assert len(scores) == 1
    assert scores[0]["degree"] == 0
    assert scores[0]["blastRadiusPercentage"] == 100.0  # 1/1 node failed
    assert scores[0]["cascadeRiskScore"] == 100.0

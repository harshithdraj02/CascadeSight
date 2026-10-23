"""
Tests for core.tipping_point.TippingPointAnalyzer
Verifies forward-difference tipping point calculation, phase-change detection,
and flat curve invariant handling.
"""

import pytest
import networkx as nx
from core.tipping_point import TippingPointAnalyzer

def test_step_function_tipping_point_detection():
    """
    Construct a graph with a sharp percolation cliff:
    Node 'child' has 2 upstream dependencies: p1 and p2.
    Triggering p1 produces a failed ratio of 1/2 = 0.50.
    - For theta <= 0.50: child collapses (blast = 2/3 = 66.7%).
    - For theta >= 0.55: child survives (blast = 1/3 = 33.3%).
    The largest forward drop occurs between theta=0.50 and theta=0.55.
    The tipping point threshold must be identified as 0.50.
    """
    graph = nx.DiGraph()
    graph.add_edge("p1", "child")
    graph.add_edge("p2", "child")

    analyzer = TippingPointAnalyzer(graph)
    result = analyzer.analyze_threshold_sensitivity(["p1"])

    assert result["tippingPointDetected"] is True
    assert result["tippingPointThreshold"] == 0.50
    assert result["maxCollapseDelta"] > 30.0

def test_flat_curve_invariant_handling():
    """
    In a graph where triggering an isolated node causes zero downstream propagation
    across all thresholds (e.g., leaf node with out_degree=0),
    the degradation curve is completely flat (blast = 1/N for all theta).
    The analyzer must report tippingPointDetected = False without locking onto theta=0.10.
    """
    graph = nx.DiGraph()
    graph.add_edge("root", "leaf")

    analyzer = TippingPointAnalyzer(graph)
    # Trigger leaf (has no downstream dependents)
    result = analyzer.analyze_threshold_sensitivity(["leaf"])

    assert result["tippingPointDetected"] is False
    assert result["tippingPointThreshold"] is None
    assert result["maxCollapseDelta"] == 0.0

def test_curve_monotonicity_with_increasing_threshold():
    """
    Invariant: As threshold theta increases (system becomes more tolerant),
    simulated collapse percentage must be monotonically non-increasing.
    Collapse(theta_i) >= Collapse(theta_{i+1}) for all i.
    """
    from core.graph_engine import DependencyGraphEngine
    engine = DependencyGraphEngine()
    graph = engine.create_synthetic_infrastructure()

    analyzer = TippingPointAnalyzer(graph)
    result = analyzer.analyze_threshold_sensitivity(["Internal Config Service"])

    curve = result["curve"]
    for i in range(len(curve) - 1):
        th_current = curve[i]["threshold"]
        th_next = curve[i + 1]["threshold"]
        assert th_current < th_next
        assert curve[i]["systemCollapsePercentage"] >= curve[i + 1]["systemCollapsePercentage"], (
            f"Violation of percolation monotonicity: {curve[i]} vs {curve[i+1]}"
        )

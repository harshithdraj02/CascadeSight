"""
Tests for core.cascade_model.CascadeSimulator
Verifies dynamic equilibrium termination without arbitrary timestep truncation,
cycle handling, boundary thresholds, and simulation invariants.
"""

import pytest
import networkx as nx
from core.cascade_model import CascadeSimulator

def test_long_dependency_chain_exceeding_50_nodes():
    """
    CRITICAL REQUIREMENT 1: Test a cascade on a dependency chain longer than 50 nodes.
    Verifies that the simulator reaches full equilibrium rather than silently
    truncating at the previous 50-step cap.
    """
    chain_length = 60
    graph = nx.DiGraph()
    for i in range(chain_length):
        graph.add_node(f"node_{i}")
    for i in range(chain_length - 1):
        # Edge (node_i, node_{i+1}) means node_{i+1} depends on node_i
        graph.add_edge(f"node_{i}", f"node_{i+1}")

    simulator = CascadeSimulator(graph, default_threshold=0.50)
    result = simulator.simulate_cascade(["node_0"], threshold=0.50)

    # Must reach all 60 nodes across 59 propagation steps + step 0
    assert result["totalNodes"] == 60
    assert result["totalFailedNodes"] == 60
    assert result["blastRadiusPercentage"] == 100.0
    assert result["totalTimesteps"] == 59
    assert result["equilibriumReached"] is True
    assert result["simulationHaltedEarly"] is False
    assert result["failureTimesteps"]["node_59"] == 59

def test_cascade_monotonicity_invariant():
    """
    Invariant: The failed set must be monotonically non-decreasing over timesteps.
    Once a node fails, it must remain in the failed set for all subsequent steps.
    """
    graph = nx.DiGraph()
    graph.add_edges_from([
        ("root", "a"), ("root", "b"),
        ("a", "c"), ("b", "c"),
        ("c", "d")
    ])

    simulator = CascadeSimulator(graph, default_threshold=0.40)
    result = simulator.simulate_cascade(["root"])

    history = result["stepHistory"]
    accumulated_failed = set()
    for step in history:
        for node in step["newlyFailed"]:
            assert node not in accumulated_failed, f"Node {node} failed multiple times"
            accumulated_failed.add(node)
        assert step["totalFailedCount"] == len(accumulated_failed)

def test_directed_cycle_reaches_equilibrium_without_looping():
    """
    Invariant: A graph with a directed cycle (A -> B -> C -> A) must reach equilibrium
    without entering an infinite loop because failed states are monotonically frozen.
    """
    graph = nx.DiGraph()
    graph.add_edges_from([
        ("A", "B"),
        ("B", "C"),
        ("C", "A"),
        ("C", "D")
    ])

    simulator = CascadeSimulator(graph, default_threshold=0.50)
    result = simulator.simulate_cascade(["A"])

    assert result["equilibriumReached"] is True
    assert result["simulationHaltedEarly"] is False
    assert set(result["failedNodesList"]) == {"A", "B", "C", "D"}
    assert result["totalTimesteps"] <= 4

def test_boundary_thresholds():
    """
    Threshold theta = 0.0 means any upstream failure causes collapse immediately.
    Threshold theta = 1.0 means 100% of upstream dependencies must fail.
    """
    graph = nx.DiGraph()
    # node 'child' depends on two parents: p1 and p2
    graph.add_edge("p1", "child")
    graph.add_edge("p2", "child")

    simulator = CascadeSimulator(graph)

    # Fail p1 with theta = 0.40: failed ratio is 1/2 = 0.50 >= 0.40 -> child fails
    res_low = simulator.simulate_cascade(["p1"], threshold=0.40)
    assert "child" in res_low["failedNodesList"]

    # Fail p1 with theta = 0.60: failed ratio is 1/2 = 0.50 < 0.60 -> child survives
    res_high = simulator.simulate_cascade(["p1"], threshold=0.60)
    assert "child" not in res_high["failedNodesList"]
    assert res_high["survivedNodesCount"] == 2  # p2 and child survive

def test_empty_graph_and_nonexistent_nodes():
    """
    Edge case: Empty graph or trigger nodes not in graph must not crash.
    """
    empty_graph = nx.DiGraph()
    sim = CascadeSimulator(empty_graph)
    res = sim.simulate_cascade(["non_existent"])
    assert res["totalNodes"] == 0
    assert res["blastRadiusPercentage"] == 0.0
    assert res["equilibriumReached"] is True

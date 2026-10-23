import pytest
from core.graph_engine import DependencyGraphEngine
from core.remediation import ArchitecturalRemediationEngine

def test_circuit_breaker_isolation_reduces_blast_radius():
    engine = DependencyGraphEngine()
    g = engine.create_synthetic_infrastructure()
    remediation_engine = ArchitecturalRemediationEngine(g)

    # Evaluate circuit breaker on Internal Config Service (Rank 1 HSPOF)
    result = remediation_engine.evaluate_mitigation("Internal Config Service", threshold=0.40)

    pre = result["preMitigation"]
    post = result["postMitigation"]

    # Pre-mitigation causes 80% collapse
    assert pre["blastRadiusPercentage"] == 80.0
    assert pre["totalFailedNodes"] == 16
    assert pre["status"] == "VULNERABLE"

    # Post-mitigation isolates the failure to only the target node itself
    assert post["blastRadiusPercentage"] == 5.0
    assert post["totalFailedNodes"] == 1
    assert post["status"] == "RESILIENT"

    # Measurable honest risk reduction
    assert result["riskReductionPercentage"] > 90.0

def test_remediation_on_leaf_node_reports_zero_downstream_impact():
    engine = DependencyGraphEngine()
    g = engine.create_synthetic_infrastructure()
    remediation_engine = ArchitecturalRemediationEngine(g)

    # Web Client Portal is a frontend leaf with no outgoing dependencies
    result = remediation_engine.evaluate_mitigation("Web Client Portal", threshold=0.40)

    pre = result["preMitigation"]
    post = result["postMitigation"]

    assert pre["blastRadiusPercentage"] == post["blastRadiusPercentage"]
    assert result["riskReductionPercentage"] == 0.0

import json
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_api_ui_smoke(client):
    res = client.get('/')
    assert res.status_code == 200
    content = res.data.decode('utf-8')
    assert "CascadeSight" in content
    assert "btn-prev" in content
    assert "btn-next" in content

def test_api_graph_smoke(client):
    res = client.get('/api/graph?type=synthetic')
    assert res.status_code == 200
    data = res.get_json()
    assert data["totalNodes"] == 20
    assert data["totalEdges"] == 29

def test_api_risk_scores_smoke(client):
    res = client.get('/api/risk-scores?type=synthetic&threshold=0.40')
    assert res.status_code == 200
    scores = res.get_json()
    assert len(scores) == 20
    assert scores[0]["node"] == "Internal Config Service"
    assert scores[0]["cascadeRiskScore"] == 9.14

def test_api_simulate_smoke(client):
    payload = {
        "initialNodes": ["Internal Config Service"],
        "threshold": 0.40,
        "type": "synthetic"
    }
    res = client.post('/api/simulate', json=payload)
    assert res.status_code == 200
    sim = res.get_json()
    assert sim["blastRadiusPercentage"] == 80.0
    assert sim["totalFailedNodes"] == 16
    assert sim["equilibriumReached"] is True

def test_api_tipping_point_smoke(client):
    payload = {
        "triggerNodes": ["Internal Config Service"],
        "type": "synthetic"
    }
    res = client.post('/api/tipping-point', json=payload)
    assert res.status_code == 200
    tp = res.get_json()
    assert tp["tippingPointDetected"] is True
    assert tp["tippingPointThreshold"] == 0.65

def test_api_case_study_smoke(client):
    res = client.get('/api/case-study')
    assert res.status_code == 200
    cs = res.get_json()
    assert cs["originRanksFirst"] is True
    assert cs["incidentOriginNode"] == "Backbone BGP Router Config"

def test_api_remediation_smoke(client):
    payload = {
        "targetNode": "Internal Config Service",
        "threshold": 0.40,
        "type": "synthetic"
    }
    res = client.post('/api/remediation', json=payload)
    assert res.status_code == 200
    rem = res.get_json()
    assert rem["preMitigation"]["blastRadiusPercentage"] == 80.0
    assert rem["postMitigation"]["blastRadiusPercentage"] == 5.0
    assert rem["riskReductionPercentage"] > 90.0

def test_api_import_json_smoke(client):
    json_manifest = json.dumps({
        "services": [
            {"name": "svc-1", "category": "service"},
            {"name": "svc-2", "category": "network"}
        ],
        "dependencies": [
            {"from": "svc-2", "to": "svc-1"}
        ]
    })
    payload = {
        "content": json_manifest,
        "format": "json"
    }
    res = client.post('/api/import-architecture', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["totalNodes"] == 2
    assert data["totalEdges"] == 1

def test_api_audit_report_smoke(client):
    res = client.get('/api/audit-report?type=synthetic&threshold=0.40')
    assert res.status_code == 200
    audit = res.get_json()
    assert audit["totalMicroservices"] == 20
    assert audit["totalHSPOFsIdentified"] >= 1

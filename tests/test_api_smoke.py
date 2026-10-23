import urllib.request
import json
import pytest

BASE_URL = "http://127.0.0.1:5000"

def test_api_ui_smoke():
    res = urllib.request.urlopen(f"{BASE_URL}/")
    assert res.status == 200
    content = res.read().decode('utf-8')
    assert "CascadeSight" in content
    assert "btn-prev" in content
    assert "btn-next" in content

def test_api_graph_smoke():
    res = urllib.request.urlopen(f"{BASE_URL}/api/graph?type=synthetic")
    assert res.status == 200
    data = json.loads(res.read().decode('utf-8'))
    assert data["totalNodes"] == 20
    assert data["totalEdges"] == 29

def test_api_risk_scores_smoke():
    res = urllib.request.urlopen(f"{BASE_URL}/api/risk-scores?type=synthetic&threshold=0.40")
    assert res.status == 200
    scores = json.loads(res.read().decode('utf-8'))
    assert len(scores) == 20
    assert scores[0]["node"] == "Internal Config Service"
    assert scores[0]["cascadeRiskScore"] == 9.14

def test_api_simulate_smoke():
    payload = json.dumps({
        "initialNodes": ["Internal Config Service"],
        "threshold": 0.40,
        "type": "synthetic"
    }).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/api/simulate", data=payload, headers={"Content-Type": "application/json"})
    res = urllib.request.urlopen(req)
    assert res.status == 200
    sim = json.loads(res.read().decode('utf-8'))
    assert sim["blastRadiusPercentage"] == 80.0
    assert sim["totalFailedNodes"] == 16
    assert sim["equilibriumReached"] is True

def test_api_tipping_point_smoke():
    payload = json.dumps({
        "triggerNodes": ["Internal Config Service"],
        "type": "synthetic"
    }).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/api/tipping-point", data=payload, headers={"Content-Type": "application/json"})
    res = urllib.request.urlopen(req)
    assert res.status == 200
    tp = json.loads(res.read().decode('utf-8'))
    assert tp["tippingPointDetected"] is True
    assert tp["tippingPointThreshold"] == 0.65

def test_api_case_study_smoke():
    res = urllib.request.urlopen(f"{BASE_URL}/api/case-study")
    assert res.status == 200
    cs = json.loads(res.read().decode('utf-8'))
    assert cs["originRanksFirst"] is True
    assert cs["incidentOriginNode"] == "Backbone BGP Router Config"

def test_api_remediation_smoke():
    payload = json.dumps({
        "targetNode": "Internal Config Service",
        "threshold": 0.40,
        "type": "synthetic"
    }).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/api/remediation", data=payload, headers={"Content-Type": "application/json"})
    res = urllib.request.urlopen(req)
    assert res.status == 200
    rem = json.loads(res.read().decode('utf-8'))
    assert rem["preMitigation"]["blastRadiusPercentage"] == 80.0
    assert rem["postMitigation"]["blastRadiusPercentage"] == 5.0
    assert rem["riskReductionPercentage"] > 90.0

def test_api_import_json_smoke():
    json_manifest = json.dumps({
        "services": [
            {"name": "svc-1", "category": "service"},
            {"name": "svc-2", "category": "network"}
        ],
        "dependencies": [
            {"from": "svc-2", "to": "svc-1"}
        ]
    })
    payload = json.dumps({
        "content": json_manifest,
        "format": "json"
    }).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/api/import-architecture", data=payload, headers={"Content-Type": "application/json"})
    res = urllib.request.urlopen(req)
    assert res.status == 200
    data = json.loads(res.read().decode('utf-8'))
    assert data["success"] is True
    assert data["totalNodes"] == 2
    assert data["totalEdges"] == 1

def test_api_audit_report_smoke():
    res = urllib.request.urlopen(f"{BASE_URL}/api/audit-report?type=synthetic&threshold=0.40")
    assert res.status == 200
    audit = json.loads(res.read().decode('utf-8'))
    assert audit["totalMicroservices"] == 20
    assert audit["totalHSPOFsIdentified"] >= 1

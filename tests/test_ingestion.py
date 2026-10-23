import pytest
import json
from core.ingestion import InfrastructureIngestionEngine

def test_parse_architecture_json_standard():
    payload = json.dumps({
        "services": [
            {"name": "web", "category": "service"},
            {"name": "api", "category": "network"},
            {"name": "db", "category": "storage"}
        ],
        "dependencies": [
            {"from": "api", "to": "web"},
            {"from": "db", "to": "api"}
        ]
    })
    graph = InfrastructureIngestionEngine.parse_architecture_json(payload)
    assert graph.number_of_nodes() == 3
    assert graph.number_of_edges() == 2
    assert graph.has_edge("api", "web")
    assert graph.has_edge("db", "api")

def test_parse_architecture_json_with_undeclared_edge_nodes():
    payload = json.dumps({
        "nodes": [
            {"id": "service-a"}
        ],
        "edges": [
            {"source": "service-a", "target": "service-b"}
        ]
    })
    graph = InfrastructureIngestionEngine.parse_architecture_json(payload)
    assert graph.number_of_nodes() == 2
    assert "service-b" in graph
    assert graph.has_edge("service-a", "service-b")

def test_parse_docker_compose_valid():
    yaml_content = """
version: '3.8'
services:
  frontend:
    image: nginx
    depends_on:
      - backend
  backend:
    image: node
    depends_on:
      - postgres
  postgres:
    image: postgres:14
"""
    graph = InfrastructureIngestionEngine.parse_docker_compose(yaml_content)
    assert graph.number_of_nodes() == 3
    assert graph.number_of_edges() == 2
    assert graph.has_edge("backend", "frontend")
    assert graph.has_edge("postgres", "backend")

def test_parse_invalid_payload_raises():
    with pytest.raises(Exception):
        InfrastructureIngestionEngine.parse_architecture_json("INVALID NOT JSON")

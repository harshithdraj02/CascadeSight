"""
CascadeSight - Dynamic Infrastructure Ingestion Engine
Parses real-world architecture manifests (Docker Compose YAML, Kubernetes Services, 
and OpenTelemetry JSON dependency graphs) directly into NetworkX DiGraphs.
"""

import networkx as nx
import json
import yaml
from typing import Dict, Any, Tuple

class InfrastructureIngestionEngine:
    @staticmethod
    def parse_docker_compose(yaml_content: str) -> nx.DiGraph:
        """
        Parses docker-compose.yml content and extracts services and their 
        directed dependencies (depends_on, links, network links).
        """
        data = yaml.safe_load(yaml_content)
        if not data or not isinstance(data, dict):
            raise ValueError("Invalid YAML: Root must be a dictionary.")

        services = data.get('services', {})
        if not services and 'version' not in data:
            # Fallback if services is at root
            services = data

        graph = nx.DiGraph()
        
        # Categorization heuristic based on service names
        def guess_category(name: str) -> str:
            name_lower = name.lower()
            if any(k in name_lower for k in ['db', 'database', 'postgres', 'mysql', 'mongo', 'redis', 'sql']):
                return 'storage'
            if any(k in name_lower for k in ['auth', 'security', 'identity', 'keycloak']):
                return 'security'
            if any(k in name_lower for k in ['gateway', 'proxy', 'nginx', 'traefik', 'ingress']):
                return 'network'
            if any(k in name_lower for k in ['worker', 'job', 'queue', 'kafka', 'celery']):
                return 'compute'
            return 'service'

        for svc_name, svc_conf in services.items():
            cat = guess_category(svc_name)
            graph.add_node(svc_name, label=svc_name, category=cat)

        for svc_name, svc_conf in services.items():
            if not isinstance(svc_conf, dict):
                continue
                
            # Extract depends_on
            deps = svc_conf.get('depends_on', [])
            if isinstance(deps, dict):
                deps = list(deps.keys())
            elif isinstance(deps, str):
                deps = [deps]

            for dep in deps:
                if dep in graph:
                    # svc_name depends on dep -> directed edge (dep -> svc_name)
                    # When dep fails, svc_name is impacted
                    graph.add_edge(dep, svc_name)

            # Extract links
            links = svc_conf.get('links', [])
            for link in links:
                target = link.split(':')[0]
                if target in graph and target != svc_name:
                    graph.add_edge(target, svc_name)

        return graph

    @staticmethod
    def parse_architecture_json(json_content: str) -> nx.DiGraph:
        """
        Parses OpenTelemetry / Cloud Architecture JSON:
        Format: {"services": [{"name": "auth", "category": "security"}], "dependencies": [{"from": "auth", "to": "gateway"}]}
        or standard nodes/edges JSON.
        """
        data = json.loads(json_content)
        graph = nx.DiGraph()

        if "nodes" in data and "edges" in data:
            for n in data["nodes"]:
                nid = n.get("id") or n.get("name")
                graph.add_node(nid, label=n.get("label", nid), category=n.get("category", "service"))
            for e in data["edges"]:
                src = e.get("source") or e.get("from")
                tgt = e.get("target") or e.get("to")
                if src and tgt:
                    if src not in graph:
                        graph.add_node(src, label=src, category="service")
                    if tgt not in graph:
                        graph.add_node(tgt, label=tgt, category="service")
                    graph.add_edge(src, tgt)
            return graph

        if "services" in data and "dependencies" in data:
            for s in data["services"]:
                sname = s.get("name") or s.get("id")
                graph.add_node(sname, label=s.get("label", sname), category=s.get("category", "service"))
            for d in data["dependencies"]:
                src = d.get("from") or d.get("source") or d.get("upstream")
                tgt = d.get("to") or d.get("target") or d.get("downstream")
                if src and tgt:
                    if src not in graph:
                        graph.add_node(src, label=src, category="service")
                    if tgt not in graph:
                        graph.add_node(tgt, label=tgt, category="service")
                    graph.add_edge(src, tgt)
            return graph

        raise ValueError("Unrecognized architecture JSON schema. Provide {nodes, edges} or {services, dependencies}.")

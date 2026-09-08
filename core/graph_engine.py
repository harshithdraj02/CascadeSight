"""
CascadeSight - Graph Engine Module
Handles directed dependency graph creation, synthetic system generation, 
and historical post-mortem topology reconstruction.
"""

import networkx as nx
import json
from typing import Dict, List, Any, Tuple

class DependencyGraphEngine:
    def __init__(self):
        self.graph = nx.DiGraph()

    def create_synthetic_infrastructure(self) -> nx.DiGraph:
        """
        Creates a realistic microservices/smart-city digital infrastructure graph.
        Designed specifically with a 'hidden single point of failure':
        A node with low degree centrality (few connections) but high systemic risk (CRS).
        """
        G = nx.DiGraph()
        
        # Define nodes with categories
        nodes = [
            ("Core Network Gateway", {"category": "network", "label": "Network Gateway", "weight": 1.0}),
            ("Internal Config Service", {"category": "config", "label": "Config Service", "weight": 1.0}), # HIDDEN CRITICAL NODE
            ("Auth Service", {"category": "security", "label": "Auth Service", "weight": 0.9}),
            ("API Gateway", {"category": "routing", "label": "API Gateway", "weight": 0.9}),
            ("User DB Cluster", {"category": "database", "label": "User DB Cluster", "weight": 0.8}),
            ("Payment Gateway", {"category": "finance", "label": "Payment Gateway", "weight": 0.8}),
            ("Notification Service", {"category": "messaging", "label": "Notification Svc", "weight": 0.5}),
            ("Analytics Engine", {"category": "data", "label": "Analytics Engine", "weight": 0.4}),
            ("Search Indexer", {"category": "data", "label": "Search Indexer", "weight": 0.4}),
            ("Storage Bucket Manager", {"category": "storage", "label": "Storage Manager", "weight": 0.7}),
            ("Cache Cluster (Redis)", {"category": "cache", "label": "Redis Cache", "weight": 0.6}),
            ("Audit Logging Service", {"category": "logging", "label": "Audit Logger", "weight": 0.3}),
            ("Mobile Client API", {"category": "frontend", "label": "Mobile API", "weight": 0.7}),
            ("Web Client Portal", {"category": "frontend", "label": "Web Portal", "weight": 0.7}),
            ("Third-Party Webhook Dispatcher", {"category": "messaging", "label": "Webhook Dispatcher", "weight": 0.4}),
            ("Background Job Worker 1", {"category": "worker", "label": "Worker 1", "weight": 0.3}),
            ("Background Job Worker 2", {"category": "worker", "label": "Worker 2", "weight": 0.3}),
            ("Monitoring & Alerting Agent", {"category": "monitoring", "label": "Monitoring Agent", "weight": 0.5}),
            ("Metrics Aggregator", {"category": "monitoring", "label": "Metrics Aggregator", "weight": 0.4}),
            ("Report Generator", {"category": "reporting", "label": "Report Generator", "weight": 0.3})
        ]

        for node_id, attrs in nodes:
            G.add_node(node_id, **attrs)

        # Directed Edges: (A, B) means B DEPENDS ON A.
        # So if A fails, B loses a critical upstream dependency!
        dependencies = [
            # Config Service dependencies - it underpins almost everything downstream!
            ("Internal Config Service", "Auth Service"),
            ("Internal Config Service", "API Gateway"),
            ("Internal Config Service", "User DB Cluster"),
            ("Internal Config Service", "Payment Gateway"),
            ("Internal Config Service", "Notification Service"),
            ("Internal Config Service", "Storage Bucket Manager"),
            ("Internal Config Service", "Cache Cluster (Redis)"),
            
            # Network Gateway dependencies
            ("Core Network Gateway", "API Gateway"),
            ("Core Network Gateway", "Mobile Client API"),
            ("Core Network Gateway", "Web Client Portal"),
            
            # Auth & Gateway dependencies
            ("Auth Service", "API Gateway"),
            ("Auth Service", "Mobile Client API"),
            ("Auth Service", "Web Client Portal"),
            ("API Gateway", "Mobile Client API"),
            ("API Gateway", "Web Client Portal"),
            ("API Gateway", "Third-Party Webhook Dispatcher"),
            
            # Database & Storage dependencies
            ("User DB Cluster", "Payment Gateway"),
            ("User DB Cluster", "Analytics Engine"),
            ("User DB Cluster", "Search Indexer"),
            ("Storage Bucket Manager", "Report Generator"),
            ("Storage Bucket Manager", "Analytics Engine"),
            
            # Cache dependencies
            ("Cache Cluster (Redis)", "API Gateway"),
            ("Cache Cluster (Redis)", "Search Indexer"),
            
            # Messaging & Workers dependencies
            ("Notification Service", "Third-Party Webhook Dispatcher"),
            ("Notification Service", "Background Job Worker 1"),
            ("Notification Service", "Background Job Worker 2"),
            
            # Monitoring dependencies
            ("Audit Logging Service", "Metrics Aggregator"),
            ("Monitoring & Alerting Agent", "Metrics Aggregator"),
            ("Metrics Aggregator", "Report Generator")
        ]

        for src, tgt in dependencies:
            G.add_edge(src, tgt)

        self.graph = G
        return G

    def get_meta_october_2021_graph(self) -> nx.DiGraph:
        """
        Reconstructable topology based on Meta's publicly available engineering postmortem 
        of the October 4, 2021 outage.
        """
        G = nx.DiGraph()

        nodes = [
            ("Backbone BGP Router Config", {"category": "network", "label": "BGP Config Service", "weight": 1.0}),
            ("Internal DNS Infrastructure", {"category": "dns", "label": "Internal DNS", "weight": 1.0}),
            ("Authoritative Edge DNS", {"category": "dns", "label": "Edge DNS", "weight": 0.9}),
            ("Identity & Auth Server", {"category": "auth", "label": "Auth Infrastructure", "weight": 0.9}),
            ("Facebook Web Application", {"category": "app", "label": "Facebook App", "weight": 0.8}),
            ("Instagram Application", {"category": "app", "label": "Instagram App", "weight": 0.8}),
            ("WhatsApp Messaging Gateway", {"category": "app", "label": "WhatsApp Gateway", "weight": 0.8}),
            ("Oculus VR Cloud Auth", {"category": "app", "label": "Oculus Auth", "weight": 0.7}),
            ("Data Center Physical Access Control", {"category": "internal", "label": "Physical Security System", "weight": 0.9}),
            ("Internal Incident Management Tooling", {"category": "internal", "label": "Internal Tools & IRC", "weight": 0.9}),
            ("Remote Server Console Access", {"category": "internal", "label": "Out-of-Band Management", "weight": 1.0})
        ]

        for node_id, attrs in nodes:
            G.add_node(node_id, **attrs)

        dependencies = [
            ("Backbone BGP Router Config", "Internal DNS Infrastructure"),
            ("Backbone BGP Router Config", "Authoritative Edge DNS"),
            ("Internal DNS Infrastructure", "Identity & Auth Server"),
            ("Authoritative Edge DNS", "Facebook Web Application"),
            ("Authoritative Edge DNS", "Instagram Application"),
            ("Authoritative Edge DNS", "WhatsApp Messaging Gateway"),
            ("Identity & Auth Server", "Facebook Web Application"),
            ("Identity & Auth Server", "Instagram Application"),
            ("Identity & Auth Server", "WhatsApp Messaging Gateway"),
            ("Identity & Auth Server", "Oculus VR Cloud Auth"),
            ("Internal DNS Infrastructure", "Internal Incident Management Tooling"),
            ("Internal DNS Infrastructure", "Data Center Physical Access Control"),
            ("Internal DNS Infrastructure", "Remote Server Console Access")
        ]

        for src, tgt in dependencies:
            G.add_edge(src, tgt)

        return G

    def to_json_dict(self, graph: nx.DiGraph = None) -> Dict[str, Any]:
        """Converts NetworkX DiGraph into UI-friendly node/edge dict."""
        g = graph if graph is not None else self.graph
        
        nodes_list = []
        for n, data in g.nodes(data=True):
            in_degree = g.in_degree(n)
            out_degree = g.out_degree(n)
            nodes_list.append({
                "id": n,
                "label": data.get("label", n),
                "category": data.get("category", "default"),
                "weight": data.get("weight", 1.0),
                "inDegree": in_degree,
                "outDegree": out_degree,
                "degree": in_degree + out_degree
            })
            
        edges_list = []
        for u, v in g.edges():
            edges_list.append({
                "source": u,
                "target": v
            })

        return {
            "nodes": nodes_list,
            "edges": edges_list,
            "totalNodes": g.number_of_nodes(),
            "totalEdges": g.number_of_edges()
        }

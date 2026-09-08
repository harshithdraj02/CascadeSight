"""
CascadeSight - Cascade Simulator Module
Simulates discrete-time threshold cascade propagation across directed dependency graphs.
"""

import networkx as nx
from typing import Dict, List, Set, Any, Tuple

class CascadeSimulator:
    def __init__(self, graph: nx.DiGraph, default_threshold: float = 0.40):
        self.graph = graph
        self.default_threshold = default_threshold

    def simulate_cascade(self, initial_failed_nodes: List[str], threshold: float = None) -> Dict[str, Any]:
        """
        Runs a discrete-time cascade simulation starting from initial_failed_nodes.
        Returns detailed step-by-step collapse trace and causality.
        """
        th = threshold if threshold is not None else self.default_threshold
        
        # State tracking
        failed_set: Set[str] = set(initial_failed_nodes)
        failure_timesteps: Dict[str, int] = {node: 0 for node in initial_failed_nodes}
        causality_triggers: Dict[str, List[str]] = {node: ["INITIAL_FAILURE"] for node in initial_failed_nodes}
        
        history: List[Dict[str, Any]] = []
        
        # Record Initial State (t=0)
        history.append({
            "timestep": 0,
            "newlyFailed": list(initial_failed_nodes),
            "totalFailedCount": len(failed_set),
            "systemHealthPercentage": round((1.0 - (len(failed_set) / self.graph.number_of_nodes())) * 100, 2)
        })

        timestep = 1
        max_timesteps = 50  # prevent infinite loops
        
        while timestep <= max_timesteps:
            newly_failed_in_step: Set[str] = set()
            step_causality: Dict[str, List[str]] = {}

            for node in self.graph.nodes():
                if node in failed_set:
                    continue
                
                # Upstream dependencies of 'node' (nodes that 'node' depends on)
                upstream_deps = list(self.graph.predecessors(node))
                
                if not upstream_deps:
                    # Root node with no upstream dependencies - fails only if explicitly triggered
                    continue
                
                # Count how many upstream dependencies are currently failed
                failed_upstream = [dep for dep in upstream_deps if dep in failed_set]
                failed_ratio = len(failed_upstream) / len(upstream_deps)
                
                # If failed ratio meets or exceeds threshold, this node collapses at this step!
                if failed_ratio >= th:
                    newly_failed_in_step.add(node)
                    step_causality[node] = failed_upstream

            if not newly_failed_in_step:
                # Equilibrium reached! No more nodes failing.
                break

            for node in newly_failed_in_step:
                failed_set.add(node)
                failure_timesteps[node] = timestep
                causality_triggers[node] = step_causality[node]

            history.append({
                "timestep": timestep,
                "newlyFailed": list(newly_failed_in_step),
                "totalFailedCount": len(failed_set),
                "systemHealthPercentage": round((1.0 - (len(failed_set) / self.graph.number_of_nodes())) * 100, 2)
            })

            timestep += 1

        total_nodes = self.graph.number_of_nodes()
        total_failed = len(failed_set)
        blast_radius_pct = round((total_failed / total_nodes) * 100, 2)

        return {
            "initialFailed": initial_failed_nodes,
            "thresholdUsed": th,
            "totalTimesteps": len(history) - 1,
            "totalFailedNodes": total_failed,
            "totalNodes": total_nodes,
            "blastRadiusPercentage": blast_radius_pct,
            "survivedNodesCount": total_nodes - total_failed,
            "failureTimesteps": failure_timesteps,
            "causalityTriggers": causality_triggers,
            "stepHistory": history,
            "failedNodesList": list(failed_set)
        }

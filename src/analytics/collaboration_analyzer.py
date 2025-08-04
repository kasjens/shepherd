"""
Collaboration Analyzer - Agent Interaction Pattern Analysis

This module analyzes agent collaboration patterns to provide insights into:
- Communication flow efficiency
- Task delegation patterns
- Memory sharing effectiveness
- Agent specialization trends
- Collaboration success metrics
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


class CollaborationPattern(Enum):
    """Types of collaboration patterns detected"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HIERARCHICAL = "hierarchical"
    PEER_TO_PEER = "peer_to_peer"
    HUB_AND_SPOKE = "hub_and_spoke"
    MESH = "mesh"


@dataclass
class AgentInteraction:
    """Represents a single interaction between agents"""
    sender_id: str
    receiver_id: str
    interaction_type: str  # message, memory_share, tool_request, etc.
    timestamp: datetime
    duration_ms: float
    success: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CollaborationMetrics:
    """Metrics for agent collaboration analysis"""
    total_interactions: int
    unique_agent_pairs: int
    avg_response_time: float
    success_rate: float
    most_active_agents: List[Tuple[str, int]]
    communication_density: float
    pattern_distribution: Dict[str, float]
    efficiency_score: float


@dataclass
class NetworkAnalysis:
    """Network analysis of agent interactions"""
    centrality_scores: Dict[str, float]
    clustering_coefficient: float
    network_diameter: int
    connected_components: int
    bottleneck_agents: List[str]
    bridge_agents: List[str]


class CollaborationAnalyzer:
    """
    Analyzes agent collaboration patterns and provides insights
    for workflow optimization and performance improvement.
    """
    
    def __init__(self, shared_context, communication_manager):
        self.shared_context = shared_context
        self.communication_manager = communication_manager
        self.interaction_history: List[AgentInteraction] = []
        self.pattern_cache: Dict[str, Any] = {}
        self.analysis_cache_ttl = 300  # 5 minutes
        
    async def record_interaction(self, interaction: AgentInteraction) -> None:
        """Record a new agent interaction for analysis"""
        self.interaction_history.append(interaction)
        
        # Store in shared context for persistence
        await self.shared_context.store(
            f"interaction_{interaction.timestamp.isoformat()}",
            {
                'sender': interaction.sender_id,
                'receiver': interaction.receiver_id,
                'type': interaction.interaction_type,
                'timestamp': interaction.timestamp.isoformat(),
                'duration_ms': interaction.duration_ms,
                'success': interaction.success,
                'metadata': interaction.metadata
            }
        )
        
        # Clear relevant caches
        self._clear_pattern_cache()
    
    async def analyze_collaboration_patterns(self, 
                                           time_window: Optional[timedelta] = None) -> CollaborationMetrics:
        """
        Analyze collaboration patterns within a time window
        
        Args:
            time_window: Time window to analyze (default: last 24 hours)
            
        Returns:
            CollaborationMetrics with analysis results
        """
        if time_window is None:
            time_window = timedelta(hours=24)
            
        cache_key = f"collaboration_patterns_{time_window.total_seconds()}"
        
        # Check cache first
        if cache_key in self.pattern_cache:
            cache_time, cached_result = self.pattern_cache[cache_key]
            if (datetime.now() - cache_time).seconds < self.analysis_cache_ttl:
                return cached_result
        
        # Filter interactions by time window
        cutoff_time = datetime.now() - time_window
        recent_interactions = [
            interaction for interaction in self.interaction_history
            if interaction.timestamp >= cutoff_time
        ]
        
        if not recent_interactions:
            return CollaborationMetrics(
                total_interactions=0,
                unique_agent_pairs=0,
                avg_response_time=0,
                success_rate=0,
                most_active_agents=[],
                communication_density=0,
                pattern_distribution={},
                efficiency_score=0
            )
        
        # Calculate metrics
        metrics = await self._calculate_collaboration_metrics(recent_interactions)
        
        # Cache result
        self.pattern_cache[cache_key] = (datetime.now(), metrics)
        
        return metrics
    
    async def _calculate_collaboration_metrics(self, 
                                             interactions: List[AgentInteraction]) -> CollaborationMetrics:
        """Calculate detailed collaboration metrics"""
        
        # Basic counts
        total_interactions = len(interactions)
        successful_interactions = len([i for i in interactions if i.success])
        success_rate = successful_interactions / total_interactions if total_interactions > 0 else 0
        
        # Agent pairs
        agent_pairs = set()
        agent_activity = Counter()
        
        for interaction in interactions:
            agent_pairs.add((interaction.sender_id, interaction.receiver_id))
            agent_activity[interaction.sender_id] += 1
            agent_activity[interaction.receiver_id] += 1
        
        unique_agent_pairs = len(agent_pairs)
        most_active_agents = agent_activity.most_common(5)
        
        # Response times
        response_times = [i.duration_ms for i in interactions if i.duration_ms > 0]
        avg_response_time = np.mean(response_times) if response_times else 0
        
        # Communication density (interactions per unique agent pair)
        unique_agents = len(set(agent_activity.keys()))
        max_possible_pairs = unique_agents * (unique_agents - 1) if unique_agents > 1 else 1
        communication_density = len(agent_pairs) / max_possible_pairs if max_possible_pairs > 0 else 0
        
        # Pattern distribution
        pattern_distribution = await self._analyze_pattern_distribution(interactions)
        
        # Efficiency score (composite metric)
        efficiency_score = self._calculate_efficiency_score(
            success_rate, avg_response_time, communication_density
        )
        
        return CollaborationMetrics(
            total_interactions=total_interactions,
            unique_agent_pairs=unique_agent_pairs,
            avg_response_time=avg_response_time,
            success_rate=success_rate,
            most_active_agents=most_active_agents,
            communication_density=communication_density,
            pattern_distribution=pattern_distribution,
            efficiency_score=efficiency_score
        )
    
    async def _analyze_pattern_distribution(self, 
                                          interactions: List[AgentInteraction]) -> Dict[str, float]:
        """Analyze the distribution of collaboration patterns"""
        pattern_counts = Counter()
        
        # Group interactions by time windows to identify patterns
        time_groups = self._group_interactions_by_time(interactions, window_minutes=5)
        
        for group in time_groups:
            pattern = self._identify_collaboration_pattern(group)
            pattern_counts[pattern.value] += 1
        
        total_patterns = sum(pattern_counts.values())
        if total_patterns == 0:
            return {}
        
        return {
            pattern: count / total_patterns 
            for pattern, count in pattern_counts.items()
        }
    
    def _group_interactions_by_time(self, 
                                   interactions: List[AgentInteraction], 
                                   window_minutes: int = 5) -> List[List[AgentInteraction]]:
        """Group interactions into time windows"""
        if not interactions:
            return []
        
        # Sort by timestamp
        sorted_interactions = sorted(interactions, key=lambda x: x.timestamp)
        
        groups = []
        current_group = []
        current_window_start = sorted_interactions[0].timestamp
        window_delta = timedelta(minutes=window_minutes)
        
        for interaction in sorted_interactions:
            if interaction.timestamp - current_window_start <= window_delta:
                current_group.append(interaction)
            else:
                if current_group:
                    groups.append(current_group)
                current_group = [interaction]
                current_window_start = interaction.timestamp
        
        if current_group:
            groups.append(current_group)
        
        return groups
    
    def _identify_collaboration_pattern(self, 
                                      interactions: List[AgentInteraction]) -> CollaborationPattern:
        """Identify the collaboration pattern for a group of interactions"""
        if len(interactions) <= 1:
            return CollaborationPattern.SEQUENTIAL
        
        # Build interaction graph
        agents = set()
        edges = []
        
        for interaction in interactions:
            agents.add(interaction.sender_id)
            agents.add(interaction.receiver_id)
            edges.append((interaction.sender_id, interaction.receiver_id))
        
        # Analyze graph structure
        unique_edges = set(edges)
        agent_count = len(agents)
        edge_count = len(unique_edges)
        
        if agent_count <= 2:
            return CollaborationPattern.SEQUENTIAL
        
        # Check for hub-and-spoke (one agent connects to many)
        agent_connections = Counter()
        for sender, receiver in edges:
            agent_connections[sender] += 1
            agent_connections[receiver] += 1
        
        max_connections = max(agent_connections.values()) if agent_connections else 0
        avg_connections = np.mean(list(agent_connections.values())) if agent_connections else 0
        
        if max_connections >= agent_count * 0.7:
            return CollaborationPattern.HUB_AND_SPOKE
        
        # Check for mesh (high connectivity)
        max_possible_edges = agent_count * (agent_count - 1) / 2
        connectivity_ratio = edge_count / max_possible_edges if max_possible_edges > 0 else 0
        
        if connectivity_ratio > 0.7:
            return CollaborationPattern.MESH
        elif connectivity_ratio > 0.3:
            return CollaborationPattern.PEER_TO_PEER
        
        # Check for hierarchical (directed chains)
        if self._has_hierarchical_structure(edges):
            return CollaborationPattern.HIERARCHICAL
        
        # Check for parallel (multiple independent chains)
        if self._has_parallel_structure(edges, agents):
            return CollaborationPattern.PARALLEL
        
        return CollaborationPattern.SEQUENTIAL
    
    def _has_hierarchical_structure(self, edges: List[Tuple[str, str]]) -> bool:
        """Check if edges form a hierarchical structure"""
        # Count in-degree and out-degree for each agent
        in_degree = Counter()
        out_degree = Counter()
        
        for sender, receiver in edges:
            out_degree[sender] += 1
            in_degree[receiver] += 1
        
        # Hierarchical pattern: some agents have only out-edges (managers),
        # some have only in-edges (workers), some have both (middle management)
        only_out = len([agent for agent in out_degree if in_degree[agent] == 0])
        only_in = len([agent for agent in in_degree if out_degree[agent] == 0])
        
        return only_out > 0 and only_in > 0
    
    def _has_parallel_structure(self, edges: List[Tuple[str, str]], agents: set) -> bool:
        """Check if edges form parallel independent chains"""
        # Build adjacency list
        adj_list = defaultdict(list)
        for sender, receiver in edges:
            adj_list[sender].append(receiver)
        
        # Find connected components
        visited = set()
        components = []
        
        for agent in agents:
            if agent not in visited:
                component = []
                self._dfs_component(agent, adj_list, visited, component)
                if len(component) > 1:
                    components.append(component)
        
        # Parallel structure: multiple disconnected components
        return len(components) > 1
    
    def _dfs_component(self, agent: str, adj_list: Dict, visited: set, component: List):
        """Depth-first search to find connected component"""
        visited.add(agent)
        component.append(agent)
        
        for neighbor in adj_list.get(agent, []):
            if neighbor not in visited:
                self._dfs_component(neighbor, adj_list, visited, component)
    
    def _calculate_efficiency_score(self, 
                                   success_rate: float, 
                                   avg_response_time: float, 
                                   communication_density: float) -> float:
        """Calculate composite efficiency score (0-1)"""
        # Normalize response time (assume 1000ms is baseline, lower is better)
        response_score = max(0, 1 - (avg_response_time / 1000))
        
        # Weight the factors
        efficiency = (
            success_rate * 0.5 +           # 50% weight on success
            response_score * 0.3 +         # 30% weight on speed
            communication_density * 0.2    # 20% weight on connectivity
        )
        
        return min(1.0, max(0.0, efficiency))
    
    async def analyze_network_structure(self, 
                                      time_window: Optional[timedelta] = None) -> NetworkAnalysis:
        """
        Perform network analysis on agent collaboration structure
        
        Args:
            time_window: Time window to analyze
            
        Returns:
            NetworkAnalysis with graph metrics
        """
        if time_window is None:
            time_window = timedelta(hours=24)
        
        # Get recent interactions
        cutoff_time = datetime.now() - time_window
        recent_interactions = [
            interaction for interaction in self.interaction_history
            if interaction.timestamp >= cutoff_time
        ]
        
        if not recent_interactions:
            return NetworkAnalysis(
                centrality_scores={},
                clustering_coefficient=0,
                network_diameter=0,
                connected_components=0,
                bottleneck_agents=[],
                bridge_agents=[]
            )
        
        # Build graph representation
        graph = self._build_interaction_graph(recent_interactions)
        
        # Calculate network metrics
        centrality_scores = self._calculate_centrality(graph)
        clustering_coefficient = self._calculate_clustering_coefficient(graph)
        network_diameter = self._calculate_network_diameter(graph)
        connected_components = self._count_connected_components(graph)
        bottleneck_agents = self._identify_bottleneck_agents(graph, centrality_scores)
        bridge_agents = self._identify_bridge_agents(graph)
        
        return NetworkAnalysis(
            centrality_scores=centrality_scores,
            clustering_coefficient=clustering_coefficient,
            network_diameter=network_diameter,
            connected_components=connected_components,
            bottleneck_agents=bottleneck_agents,
            bridge_agents=bridge_agents
        )
    
    def _build_interaction_graph(self, interactions: List[AgentInteraction]) -> Dict[str, Dict[str, int]]:
        """Build weighted graph from interactions"""
        graph = defaultdict(lambda: defaultdict(int))
        
        for interaction in interactions:
            # Add weight based on interaction success and frequency
            weight = 1 if interaction.success else 0.5
            graph[interaction.sender_id][interaction.receiver_id] += weight
            # Make undirected for network analysis
            graph[interaction.receiver_id][interaction.sender_id] += weight
        
        return dict(graph)
    
    def _calculate_centrality(self, graph: Dict[str, Dict[str, int]]) -> Dict[str, float]:
        """Calculate betweenness centrality for each agent"""
        agents = list(graph.keys())
        centrality = {}
        
        for agent in agents:
            # Simple degree centrality (connections count)
            degree = len(graph.get(agent, {}))
            total_possible = len(agents) - 1 if len(agents) > 1 else 1
            centrality[agent] = degree / total_possible
        
        return centrality
    
    def _calculate_clustering_coefficient(self, graph: Dict[str, Dict[str, int]]) -> float:
        """Calculate average clustering coefficient"""
        agents = list(graph.keys())
        if len(agents) < 3:
            return 0.0
        
        clustering_scores = []
        
        for agent in agents:
            neighbors = list(graph.get(agent, {}).keys())
            if len(neighbors) < 2:
                clustering_scores.append(0.0)
                continue
            
            # Count edges between neighbors
            neighbor_edges = 0
            for i, neighbor1 in enumerate(neighbors):
                for neighbor2 in neighbors[i+1:]:
                    if neighbor2 in graph.get(neighbor1, {}):
                        neighbor_edges += 1
            
            # Maximum possible edges between neighbors
            max_edges = len(neighbors) * (len(neighbors) - 1) / 2
            clustering = neighbor_edges / max_edges if max_edges > 0 else 0
            clustering_scores.append(clustering)
        
        return np.mean(clustering_scores) if clustering_scores else 0.0
    
    def _calculate_network_diameter(self, graph: Dict[str, Dict[str, int]]) -> int:
        """Calculate network diameter (longest shortest path)"""
        agents = list(graph.keys())
        if len(agents) <= 1:
            return 0
        
        max_distance = 0
        
        # Simple BFS to find shortest paths
        for start_agent in agents:
            distances = {start_agent: 0}
            queue = [start_agent]
            
            while queue:
                current = queue.pop(0)
                current_distance = distances[current]
                
                for neighbor in graph.get(current, {}):
                    if neighbor not in distances:
                        distances[neighbor] = current_distance + 1
                        queue.append(neighbor)
            
            # Find max distance from this agent
            if distances:
                agent_max_distance = max(distances.values())
                max_distance = max(max_distance, agent_max_distance)
        
        return max_distance
    
    def _count_connected_components(self, graph: Dict[str, Dict[str, int]]) -> int:
        """Count number of connected components"""
        agents = set(graph.keys())
        visited = set()
        components = 0
        
        for agent in agents:
            if agent not in visited:
                # DFS to mark all connected agents
                stack = [agent]
                while stack:
                    current = stack.pop()
                    if current not in visited:
                        visited.add(current)
                        stack.extend(graph.get(current, {}).keys())
                components += 1
        
        return components
    
    def _identify_bottleneck_agents(self, 
                                   graph: Dict[str, Dict[str, int]], 
                                   centrality_scores: Dict[str, float]) -> List[str]:
        """Identify agents that are potential bottlenecks"""
        # Agents with high centrality are potential bottlenecks
        threshold = 0.7
        bottlenecks = [
            agent for agent, score in centrality_scores.items()
            if score > threshold
        ]
        
        return sorted(bottlenecks, key=lambda x: centrality_scores[x], reverse=True)
    
    def _identify_bridge_agents(self, graph: Dict[str, Dict[str, int]]) -> List[str]:
        """Identify agents that bridge different parts of the network"""
        # Simplified: agents that connect to multiple clusters
        bridge_agents = []
        
        for agent in graph:
            neighbors = list(graph[agent].keys())
            if len(neighbors) >= 3:  # Must connect to at least 3 others
                # Check if neighbors are well-connected to each other
                neighbor_connections = 0
                total_possible = len(neighbors) * (len(neighbors) - 1) / 2
                
                for i, n1 in enumerate(neighbors):
                    for n2 in neighbors[i+1:]:
                        if n2 in graph.get(n1, {}):
                            neighbor_connections += 1
                
                connectivity_ratio = neighbor_connections / total_possible if total_possible > 0 else 0
                
                # If neighbors are poorly connected, this agent might be a bridge
                if connectivity_ratio < 0.3:
                    bridge_agents.append(agent)
        
        return bridge_agents
    
    def _clear_pattern_cache(self) -> None:
        """Clear the pattern analysis cache"""
        current_time = datetime.now()
        expired_keys = []
        
        for key, (cache_time, _) in self.pattern_cache.items():
            if (current_time - cache_time).seconds > self.analysis_cache_ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.pattern_cache[key]
    
    async def get_collaboration_insights(self, 
                                       time_window: Optional[timedelta] = None) -> Dict[str, Any]:
        """
        Get high-level insights about agent collaboration
        
        Returns:
            Dictionary with insights and recommendations
        """
        metrics = await self.analyze_collaboration_patterns(time_window)
        network_analysis = await self.analyze_network_structure(time_window)
        
        insights = {
            'overall_health': self._assess_collaboration_health(metrics, network_analysis),
            'top_patterns': self._get_top_patterns(metrics.pattern_distribution),
            'performance_trends': await self._analyze_performance_trends(time_window),
            'recommendations': self._generate_recommendations(metrics, network_analysis),
            'key_metrics': {
                'efficiency_score': metrics.efficiency_score,
                'success_rate': metrics.success_rate,
                'avg_response_time': metrics.avg_response_time,
                'communication_density': metrics.communication_density
            }
        }
        
        return insights
    
    def _assess_collaboration_health(self, 
                                   metrics: CollaborationMetrics, 
                                   network_analysis: NetworkAnalysis) -> str:
        """Assess overall collaboration health"""
        score = metrics.efficiency_score
        
        if score >= 0.8:
            return "Excellent"
        elif score >= 0.6:
            return "Good"
        elif score >= 0.4:
            return "Fair"
        else:
            return "Needs Improvement"
    
    def _get_top_patterns(self, pattern_distribution: Dict[str, float]) -> List[Tuple[str, float]]:
        """Get top 3 collaboration patterns by frequency"""
        return sorted(
            pattern_distribution.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:3]
    
    async def _analyze_performance_trends(self, time_window: Optional[timedelta]) -> Dict[str, str]:
        """Analyze performance trends over time"""
        # This would compare current metrics to historical averages
        # For now, return placeholder trends
        return {
            'efficiency': 'Improving',
            'response_time': 'Stable',
            'success_rate': 'Improving',
            'collaboration_frequency': 'Increasing'
        }
    
    def _generate_recommendations(self, 
                                metrics: CollaborationMetrics, 
                                network_analysis: NetworkAnalysis) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if metrics.success_rate < 0.8:
            recommendations.append(
                "Consider reviewing agent communication protocols to improve success rate"
            )
        
        if metrics.avg_response_time > 1000:
            recommendations.append(
                "Optimize agent response times through better task distribution"
            )
        
        if network_analysis.bottleneck_agents:
            recommendations.append(
                f"Address bottlenecks: agents {', '.join(network_analysis.bottleneck_agents)} "
                f"are handling too much traffic"
            )
        
        if metrics.communication_density < 0.3:
            recommendations.append(
                "Increase collaboration between agents to improve workflow efficiency"
            )
        
        if network_analysis.connected_components > 1:
            recommendations.append(
                "Some agents are isolated - consider improving connectivity"
            )
        
        return recommendations
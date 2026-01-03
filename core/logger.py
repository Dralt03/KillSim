"""Logging system for KillSim simulation tracking and analysis."""

import json
import csv
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from datetime import datetime
from core import actions


@dataclass
class AgentState:
    """Snapshot of an agent's state at a specific timestep."""
    id: int
    location: int
    hunger: float
    alive: bool
    trust: Dict[int, float]


@dataclass
class RoomState:
    """Snapshot of a room's state at a specific timestep."""
    id: int
    food: float
    agent_count: int
    agents: List[int]


@dataclass
class ActionRecord:
    """Record of an action taken by an agent."""
    agent_id: int
    action: str
    target: Optional[int]


@dataclass
class StepLog:
    """Complete log of a single simulation step."""
    timestep: int
    agents: List[AgentState]
    rooms: List[RoomState]
    actions: List[ActionRecord]


@dataclass
class SimulationMetadata:
    """Metadata about the simulation run."""
    timestamp: str
    total_steps: int
    num_agents: int
    num_rooms: int
    seed: Optional[int] = None


class SimulationLogger:
    """Tracks and exports simulation data for analysis."""
    
    def __init__(self, output_dir: str = "logs", enabled: bool = True, log_interval: int = 1):
        """
        Initialize the simulation logger.
        
        Args:
            output_dir: Directory to save log files
            enabled: Whether logging is enabled
            log_interval: Log every N steps (1 = every step)
        """
        self.enabled = enabled
        self.log_interval = log_interval
        self.output_dir = Path(output_dir)
        self.steps: List[StepLog] = []
        self.metadata: Optional[SimulationMetadata] = None
        
        if self.enabled:
            self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def set_metadata(self, total_steps: int, num_agents: int, num_rooms: int, seed: Optional[int] = None):
        """Set simulation metadata."""
        self.metadata = SimulationMetadata(
            timestamp=datetime.now().isoformat(),
            total_steps=total_steps,
            num_agents=num_agents,
            num_rooms=num_rooms,
            seed=seed
        )
    
    def log_step(self, timestep: int, agents: List[Any], rooms: Dict[int, Any], 
                 action_decisions: Dict[int, tuple]):
        """
        Log data for a single simulation step.
        
        Args:
            timestep: Current simulation timestep
            agents: List of Agent objects
            rooms: Dictionary of Room objects
            action_decisions: Dictionary mapping agent_id to (action, target) tuples
        """
        if not self.enabled or timestep % self.log_interval != 0:
            return
        
        # Log agent states
        agent_states = [
            AgentState(
                id=agent.id,
                location=agent.location,
                hunger=round(agent.hunger, 3),
                alive=agent.alive,
                trust={k: round(v, 3) for k, v in agent.trust.items()}
            )
            for agent in agents
        ]
        
        # Log room states
        room_states = [
            RoomState(
                id=room_id,
                food=round(room.food, 3),
                agent_count=len(room.agents),
                agents=list(room.agents)
            )
            for room_id, room in rooms.items()
        ]
        
        # Log actions
        action_records = [
            ActionRecord(
                agent_id=agent_id,
                action=action.name,
                target=target
            )
            for agent_id, (action, target) in action_decisions.items()
        ]
        
        # Create step log
        step_log = StepLog(
            timestep=timestep,
            agents=agent_states,
            rooms=room_states,
            actions=action_records
        )
        
        self.steps.append(step_log)
    
    def export_json(self, filename: Optional[str] = None) -> Path:
        """
        Export complete log to JSON file.
        
        Args:
            filename: Optional custom filename (default: simulation_TIMESTAMP.json)
            
        Returns:
            Path to the created JSON file
        """
        if not self.enabled:
            raise RuntimeError("Logger is disabled, cannot export")
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"simulation_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        # Convert to dictionary
        data = {
            "metadata": asdict(self.metadata) if self.metadata else None,
            "steps": [asdict(step) for step in self.steps]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return filepath
    
    def export_csv(self, prefix: Optional[str] = None) -> Dict[str, Path]:
        """
        Export logs to CSV files (separate files for agents and rooms).
        
        Args:
            prefix: Optional prefix for filenames (default: simulation_TIMESTAMP)
            
        Returns:
            Dictionary mapping file type to filepath
        """
        if not self.enabled:
            raise RuntimeError("Logger is disabled, cannot export")
        
        if prefix is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prefix = f"simulation_{timestamp}"
        
        files = {}
        
        # Export agent states
        agent_file = self.output_dir / f"{prefix}_agents.csv"
        with open(agent_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestep', 'agent_id', 'location', 'hunger', 'alive', 'trust_relationships'])
            
            for step in self.steps:
                for agent in step.agents:
                    trust_str = ';'.join([f"{k}:{v}" for k, v in agent.trust.items()])
                    writer.writerow([
                        step.timestep,
                        agent.id,
                        agent.location,
                        agent.hunger,
                        agent.alive,
                        trust_str
                    ])
        
        files['agents'] = agent_file
        
        # Export room states
        room_file = self.output_dir / f"{prefix}_rooms.csv"
        with open(room_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestep', 'room_id', 'food', 'agent_count', 'agents'])
            
            for step in self.steps:
                for room in step.rooms:
                    agents_str = ';'.join(map(str, room.agents))
                    writer.writerow([
                        step.timestep,
                        room.id,
                        room.food,
                        room.agent_count,
                        agents_str
                    ])
        
        files['rooms'] = room_file
        
        # Export actions
        action_file = self.output_dir / f"{prefix}_actions.csv"
        with open(action_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestep', 'agent_id', 'action', 'target'])
            
            for step in self.steps:
                for action in step.actions:
                    writer.writerow([
                        step.timestep,
                        action.agent_id,
                        action.action,
                        action.target if action.target is not None else ''
                    ])
        
        files['actions'] = action_file
        
        return files
    
    def generate_summary(self) -> Dict[str, Any]:
        """
        Generate summary statistics from logged data.
        
        Returns:
            Dictionary containing summary statistics
        """
        if not self.steps:
            return {}
        
        # Calculate average hunger over time
        avg_hunger_per_step = []
        for step in self.steps:
            alive_agents = [a for a in step.agents if a.alive]
            if alive_agents:
                avg_hunger = sum(a.hunger for a in alive_agents) / len(alive_agents)
                avg_hunger_per_step.append(avg_hunger)
        
        # Calculate average food per room over time
        avg_food_per_step = []
        for step in self.steps:
            avg_food = sum(r.food for r in step.rooms) / len(step.rooms)
            avg_food_per_step.append(avg_food)
        
        # Count action types
        action_counts = {}
        for step in self.steps:
            for action in step.actions:
                action_counts[action.action] = action_counts.get(action.action, 0) + 1
        
        # Calculate survival rate
        final_step = self.steps[-1]
        alive_count = sum(1 for a in final_step.agents if a.alive)
        total_agents = len(final_step.agents)
        
        return {
            "total_steps_logged": len(self.steps),
            "avg_hunger": {
                "mean": sum(avg_hunger_per_step) / len(avg_hunger_per_step),
                "min": min(avg_hunger_per_step),
                "max": max(avg_hunger_per_step),
                "final": avg_hunger_per_step[-1]
            },
            "avg_food": {
                "mean": sum(avg_food_per_step) / len(avg_food_per_step),
                "min": min(avg_food_per_step),
                "max": max(avg_food_per_step),
                "final": avg_food_per_step[-1]
            },
            "action_distribution": action_counts,
            "survival": {
                "alive": alive_count,
                "total": total_agents,
                "rate": alive_count / total_agents
            }
        }
    
    def print_summary(self):
        """Print summary statistics to console."""
        summary = self.generate_summary()
        
        if not summary:
            print("No data logged")
            return
        
        print("SIMULATION SUMMARY")
        
        print(f"\nSteps Logged: {summary['total_steps_logged']}")
        
        print("\nHunger Statistics:")
        print(f"  Mean: {summary['avg_hunger']['mean']:.3f}")
        print(f"  Min:  {summary['avg_hunger']['min']:.3f}")
        print(f"  Max:  {summary['avg_hunger']['max']:.3f}")
        print(f"  Final: {summary['avg_hunger']['final']:.3f}")
        
        print("\nFood Statistics:")
        print(f"  Mean: {summary['avg_food']['mean']:.3f}")
        print(f"  Min:  {summary['avg_food']['min']:.3f}")
        print(f"  Max:  {summary['avg_food']['max']:.3f}")
        print(f"  Final: {summary['avg_food']['final']:.3f}")
        
        print("\nAction Distribution:")
        for action, count in sorted(summary['action_distribution'].items()):
            print(f"  {action}: {count}")
        
        print("\nSurvival:")
        print(f"  Alive: {summary['survival']['alive']}/{summary['survival']['total']}")
        print(f"  Rate:  {summary['survival']['rate']:.1%}")
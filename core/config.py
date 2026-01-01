import yaml
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class SimulationConfig:
    """Configuration for simulation runtime."""
    steps: int = 50
    seed: Optional[int] = None


@dataclass
class EnvironmentConfig:
    """Configuration for environment parameters."""
    food_regen_rate: float = 0.05
    hunger_increase_rate: float = 0.05
    eat_amount: float = 0.3
    trust_increase: float = 0.05


@dataclass
class RoomConfig:
    """Configuration for a single room."""
    id: int
    capacity: int
    connected_to: List[int]
    initial_food: float = 1.0


@dataclass
class AgentConfig:
    """Configuration for a single agent."""
    id: int
    location: int
    initial_hunger: float = 0.0


@dataclass
class Config:
    """Complete simulation configuration."""
    simulation: SimulationConfig
    environment: EnvironmentConfig
    rooms: List[RoomConfig]
    agents: List[AgentConfig]


def load_config(config_path: str = "config/parameters.yaml") -> Config:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to the YAML configuration file
        
    Returns:
        Config object with all simulation parameters
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config file is invalid
    """
    path = Path(config_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(path, 'r') as f:
        data = yaml.safe_load(f)
    
    if not data:
        raise ValueError(f"Empty or invalid configuration file: {config_path}")
    
    # Parse simulation config
    sim_data = data.get('simulation', {})
    simulation = SimulationConfig(
        steps=sim_data.get('steps', 50),
        seed=sim_data.get('seed')
    )
    
    # Parse environment config
    env_data = data.get('environment', {})
    environment = EnvironmentConfig(
        food_regen_rate=env_data.get('food_regen_rate', 0.05),
        hunger_increase_rate=env_data.get('hunger_increase_rate', 0.05),
        eat_amount=env_data.get('eat_amount', 0.3),
        trust_increase=env_data.get('trust_increase', 0.05)
    )
    
    # Parse rooms
    rooms_data = data.get('rooms', [])
    rooms = [
        RoomConfig(
            id=room['id'],
            capacity=room['capacity'],
            connected_to=room['connected_to'],
            initial_food=room.get('initial_food', 1.0)
        )
        for room in rooms_data
    ]
    
    # Parse agents
    agents_data = data.get('agents', [])
    agents = [
        AgentConfig(
            id=agent['id'],
            location=agent['location'],
            initial_hunger=agent.get('initial_hunger', 0.0)
        )
        for agent in agents_data
    ]
    
    return Config(
        simulation=simulation,
        environment=environment,
        rooms=rooms,
        agents=agents
    )


def validate_config(config: Config) -> List[str]:
    """
    Validate configuration for logical consistency.
    
    Args:
        config: Configuration to validate
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    # Check room IDs are unique and sequential
    room_ids = [r.id for r in config.rooms]
    if len(room_ids) != len(set(room_ids)):
        errors.append("Room IDs must be unique")
    
    for room in config.rooms:
        for connected_id in room.connected_to:
            if connected_id not in room_ids:
                errors.append(f"Room {room.id} connects to non-existent room {connected_id}")
    
    # Check agent IDs are unique
    agent_ids = [a.id for a in config.agents]
    if len(agent_ids) != len(set(agent_ids)):
        errors.append("Agent IDs must be unique")
    
    for agent in config.agents:
        if agent.location not in room_ids:
            errors.append(f"Agent {agent.id} starts in non-existent room {agent.location}")
    
    if config.environment.food_regen_rate < 0:
        errors.append("Food regeneration rate must be non-negative")
    
    if config.environment.hunger_increase_rate < 0:
        errors.append("Hunger increase rate must be non-negative")
    
    if config.environment.eat_amount <= 0:
        errors.append("Eat amount must be positive")
    
    if config.simulation.steps <= 0:
        errors.append("Number of simulation steps must be positive")
    
    return errors

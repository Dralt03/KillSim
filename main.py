"""KillSim - Social Ecosystem Simulation"""

from core import Room, Agent, Environment
from core.config import load_config, validate_config
import random


def main():
    # Load configuration from YAML
    print("Loading configuration from config/parameters.yaml...")
    config = load_config("config/parameters.yaml")
    
    # Validate configuration
    errors = validate_config(config)
    if errors:
        print("Configuration validation errors:")
        for error in errors:
            print(f"  - {error}")
        return
    
    print(f"Configuration loaded successfully!")
    print(f"  Rooms: {len(config.rooms)}")
    print(f"  Agents: {len(config.agents)}")
    print(f"  Steps: {config.simulation.steps}")
    print()
    
    # Set random seed if specified
    if config.simulation.seed is not None:
        random.seed(config.simulation.seed)
        print(f"Random seed set to: {config.simulation.seed}\n")
    
    # Create rooms from configuration
    rooms = {}
    for room_config in config.rooms:
        rooms[room_config.id] = Room(
            id=room_config.id,
            capacity=room_config.capacity,
            connectedRooms=room_config.connected_to,
            food=room_config.initial_food
        )
    
    # Create agents from configuration
    agents = []
    for agent_config in config.agents:
        agent = Agent(
            id=agent_config.id,
            location=agent_config.location,
            hunger=agent_config.initial_hunger
        )
        agents.append(agent)
    
    # Create environment
    env = Environment(rooms, agents)
    
    # Run simulation
    print("Starting simulation...\n")
    for t in range(config.simulation.steps):
        print(f"\n{'='*60}")
        print(f"Time step {t}")
        print('='*60)
        
        actions = env.step()
        
        # Display actions taken
        print("\nActions:")
        for agent_id, (action, target) in actions.items():
            action_str = f"Agent {agent_id}: {action.name}"
            if target is not None:
                action_str += f" -> {target}"
            print(f"  {action_str}")
        
        # Display agent states
        print("\nAgent States:")
        for agent in agents:
            trust_str = ", ".join([f"{k}:{v:.2f}" for k, v in agent.trust.items()])
            if not trust_str:
                trust_str = "none"
            
            print(
                f"  Agent {agent.id}: "
                f"room={agent.location}, "
                f"hunger={agent.hunger:.2f}, "
                f"trust=[{trust_str}]"
            )
        
        # Display room states
        print("\nRoom States:")
        for room_id, room in rooms.items():
            agents_in_room = [a.id for a in agents if a.location == room_id]
            print(
                f"  Room {room_id}: "
                f"food={room.food:.2f}, "
                f"agents={agents_in_room} "
                f"({len(agents_in_room)}/{room.capacity})"
            )
    
    print(f"\n{'='*60}")
    print("Simulation complete!")
    print('='*60)


if __name__ == "__main__":
    main()
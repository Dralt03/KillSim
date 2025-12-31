from core import room, agent, actions 
from typing import Dict, List

class Environment:
    """Manages the simulation environment with rooms and agents."""
    
    def __init__(self, rooms: Dict[int, room.Room], agents: List[agent.Agent]):
        self.rooms = rooms
        self.agents = agents
        self._update_room_agents()
    
    def _update_room_agents(self):
        """Update which agents are in which rooms."""
        # Clear all room agent lists
        for room in self.rooms.values():
            room.agents.clear()
        
        # Add agents to their current rooms
        for agent in self.agents:
            if agent.alive:
                self.rooms[agent.location].agents.append(agent.id)
    
    def step(self):
        """Execute one simulation step."""
        action_decisions = {}

        # Collect actions from all agents
        for agent in self.agents:
            if not agent.alive:
                continue
            current_room = self.rooms[agent.location]
            action = agent.decide(current_room)
            action_decisions[agent.id] = action

        # Resolve actions
        for agent in self.agents:
            if not agent.alive:
                continue
                
            action, params = action_decisions[agent.id]
            current_room = self.rooms[agent.location]
            
            if action == actions.Action.EAT:
                eaten = min(0.3, current_room.food)
                current_room.food -= eaten
                agent.hunger = max(0.0, agent.hunger - eaten)  # Reduce hunger
            
            elif action == actions.Action.MOVE and params is not None:
                if params in current_room.connectedRooms:
                    agent.location = params
            
            elif action == actions.Action.TALK and params is not None:
                agent.trust[params] = agent.trust.get(params, 0.0) + 0.05

        print(action_decisions)
        self._update_room_agents()

        # Regenerate food in all rooms
        for room in self.rooms.values():
            room.food = min(1.0, room.food + 0.05)
        
        for agent in self.agents:
            if agent.alive:
                agent.hunger = min(1.0, agent.hunger + 0.05)
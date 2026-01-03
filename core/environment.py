from core import room, agent, actions
from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.logger import SimulationLogger

class Environment:
    """Manages the simulation environment with rooms and agents."""
    
    def __init__(self, rooms: Dict[int, room.Room], agents: List[agent.Agent], 
                 logger: Optional['SimulationLogger'] = None):
        self.rooms = rooms
        self.agents = agents
        self.logger = logger
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
                    target_room = self.rooms[params]
                    if len(target_room.agents) < target_room.capacity:
                        agent.location = params
                    
            
            elif action == actions.Action.TALK and params is not None:
                agent.trust[params] = round(agent.trust.get(params, 0.0) + 0.05, 2)
                agent.trust[params] = min(1.0, agent.trust[params])

        self._update_room_agents()

        # Regenerate food in all rooms
        for room in self.rooms.values():
            room.food = min(1.0, room.food + 0.05)
        
        for agent in self.agents:
            if agent.alive:
                current_room = self.rooms[agent.location]
                occupancy_ratio = len(current_room.agents) / current_room.capacity
                
                hunger_increase = 0.05
                
                if occupancy_ratio > 0.75: 
                    overcrowding_penalty = (occupancy_ratio - 0.75) * 0.1  
                    hunger_increase += overcrowding_penalty
                
                agent.hunger = min(1.0, agent.hunger + hunger_increase)

        # Log this step if logger is enabled
        if self.logger:
            self.logger.log_step(
                timestep=getattr(self, '_current_step', 0),
                agents=self.agents,
                rooms=self.rooms,
                action_decisions=action_decisions
            )
        
        return action_decisions
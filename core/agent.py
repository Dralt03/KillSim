from dataclasses import dataclass, field
from core import room, actions
import random

@dataclass
class Agent:
    """Represents an agent in the simulation with hunger, trust, and decision-making."""
    
    id: int
    location: int
    hunger: float = 0.0
    alive: bool = True
    trust: dict[int, float] = field(default_factory=dict)

    def decide(self, room: room.Room) -> tuple[actions.Action, int | None]:
        """Decide what action to take based on current state and room."""
        # 1st Priority: Eat if hungry and sufficient food available
        if self.hunger > 0.4 and room.food > 0.1:
            return actions.Action.EAT, None
        
        # 2nd Priority: Move to find food if very hungry and current room has little/no food
        if self.hunger > 0.6 and room.food < 0.2:
            if room.connectedRooms:
                target = random.choice(room.connectedRooms)
                return actions.Action.MOVE, target
        
        # 3rd Priority: Talk to other agents (build trust)
        other_agents = [agent_id for agent_id in room.agents if agent_id != self.id]
        if other_agents:
            target = random.choice(other_agents)
            return actions.Action.TALK, target

        if room.connectedRooms:
            target = random.choice(room.connectedRooms)
            return actions.Action.MOVE, target
        
        # Default: Eat whatever is available
        if room.food > 0.0:
            return actions.Action.EAT, None
        
        return actions.Action.TALK, None  # Do nothing
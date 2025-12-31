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
        # 1st Priority: Eat if hungry and food available
        if self.hunger > 0.6 and room.food > 0.1:
            return actions.Action.EAT, None

        # 2nd Priority: Talk to other agents (not self)
        other_agents = [agent_id for agent_id in room.agents if agent_id != self.id]
        if other_agents:
            target = random.choice(other_agents)
            return actions.Action.TALK, target

        # 3rd Priority: Move to connected room
        if room.connectedRooms:
            target = random.choice(room.connectedRooms)
            return actions.Action.MOVE, target
        
        # Default: Wait (eat a little if food available)
        if room.food > 0.0:
            return actions.Action.EAT, None
        
        return actions.Action.TALK, None  # Do nothing
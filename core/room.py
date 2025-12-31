class Room:
    """Represents a room in the simulation with food and connections to other rooms."""
    
    def __init__(self, id: int, capacity: int, connectedRooms: list[int], food: float = 1.0):
        self.id = id
        self.capacity = capacity
        self.food = food
        self.agents: list[int] = []  # Track agents currently in this room
        self.connectedRooms = connectedRooms
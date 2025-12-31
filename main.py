from core import *

def main():
    rooms = {
        0: Room(id=0, capacity=2, connectedRooms=[1]),
        1: Room(id=1, capacity=4, connectedRooms=[0, 2]),
        2: Room(id=2, capacity=1, connectedRooms=[1])
    }

    agents = [
        Agent(id=0, location=0),
        Agent(id=1, location=1),
        Agent(id=2, location=2)
    ]

    env = Environment(rooms, agents)

    for t in range(20):
        print(f"Time step {t}")
        env.step()
        for a in agents:
            print(f"Agent {a.id}: room={a.location}, hunger={a.hunger:.2f}, trust={a.trust}")
        print()

if __name__ == "__main__":
    main()
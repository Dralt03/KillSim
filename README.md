# Social Ecosystem Simulation (Python)

A **minimal agent-based simulation** that models how individuals behave inside a closed environment.  
Agents can **move**, **eat**, and **talk**, allowing us to study **emergent social behavior** under simple constraints.

This project is inspired by ecosystem simulations and social-deduction-style environments.

---

## Project Objectives

- Build a clean **agent-based simulation** from scratch
- Model **local perception** and **simple decision-making**
- Observe emergent behavior from minimal rules
- Create a solid base for future extensions (trust, suspicion, incentives)

This is designed as a **research / simulation framework**, not a game.

---

## Current Features (Phase 0)

- Discrete-time simulation loop
- Graph-based environment (rooms + connections)
- Agents with:
  - Hunger
  - Location
  - Trust toward other agents
- Actions:
  - Move between rooms
  - Eat food
  - Talk to other agents
- Food regeneration in rooms
- Local observation (agents only see others in the same room)

---

## Core Concepts

### Agents
- Independent decision-makers
- Limited perception
- Simple rule-based policy
- No global knowledge

### Environment
- Controls all state updates
- Resolves agent actions
- Enforces rules (agents cannot directly mutate the world)

### Emergence
Complex group behavior arises from:
- Hunger pressure
- Random movement
- Social interaction

---

## Requirements

- Python **3.10+**

---

## How to Run

1. Clone or download the project
2. Ensure all files are in the same directory
3. Run:

```bash
python main.py
```

## Configuration

The config/parameters.yaml file can be used to define the simulation parameters.

```yaml
agents: 6
rooms:
  - id: 0
    neighbors: [1]
    food: 1.0
  - id: 1
    neighbors: [0, 2]
    food: 0.5

hunger:
  increase_rate: 0.05
  eat_amount: 0.3
```
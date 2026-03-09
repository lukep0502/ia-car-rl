# IA-CAR Roadmap 🚗🤖

This roadmap describes the development stages of the IA-CAR project,
from a simple 2D simulator to an AI capable of optimizing lap times
for a future 3D Roblox racing environment.

---

# Phase 1 — Playable Prototype ✅

Goal: Build a basic playable racing simulator.

Features implemented:

- Circular track
- Basic car physics
- Lap counting
- Timer system
- Direction enforcement
- Restart system

This phase validated the core gameplay loop.

---

# Phase 2 — Track System Architecture ✅

Goal: Create a scalable and modular track system.

Features:

- Image-based tracks
- Mask-based collision detection
- Finish line detection
- Checkpoint validation
- Track boundaries
- Custom track support
- New imported track
- Major project structure reorganization

This phase transformed the project into a **flexible racing simulation engine**.

---

# Phase 3 — Sensor System

Goal: Provide perception data for the AI agent.

Planned features:

- Raycasting sensors
- Distance to track edges
- Multi-angle detection
- Collision awareness
- Sensor visualization tools

These sensors will form the **observation space for the AI**.

---

# Phase 4 — AI Environment

Goal: Transform the simulator into a Reinforcement Learning environment.

Planned features:

- Observation space definition
- Action space (steering / throttle / brake)
- Reward function
- Episode management
- Reset logic
- Performance metrics

Possible integration with:

- Gymnasium
- Stable-Baselines3

---

# Phase 5 — Reinforcement Learning Training

Goal: Train agents capable of completing laps efficiently.

Planned algorithms:

- PPO
- DQN
- SAC (possible future)

Training objectives:

- Complete laps consistently
- Minimize lap time
- Learn optimal racing lines

Evaluation metrics:

- Average lap time
- Stability
- Track completion rate

---

# Phase 6 — Advanced Simulation

Goal: Improve realism and training quality.

Possible features:

- Multiple track layouts
- Randomized spawn positions
- Dynamic track variations
- Performance telemetry
- Ghost car comparison

---

# Phase 7 — Roblox AI Adaptation (Long-Term Goal)

Goal: Apply learned strategies to a **3D Roblox racing game**.

Possible approaches:

- Recreate sensors in Roblox
- Transfer driving logic
- Record and replay optimal paths
- Train models externally and deploy behavior logic

Final objective:

An AI capable of **finding and executing the fastest lap possible in a Roblox racing environment**.
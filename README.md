# IA-CAR 🚗🤖

Top-down racing simulator built with Pygame.

This project is designed as a **training environment for reinforcement learning agents**
that will eventually be used to optimize lap times in a **3D Roblox racing game**.

The current phase focuses on building a **2D simulation environment** where AI agents can
learn driving behavior, track navigation and time optimization.

---

# Project Vision

The final goal of this project is to develop an **AI agent capable of achieving optimal lap times in a Roblox racing game**.

To achieve this, the development process is divided into stages:

1. Build a **2D simulation environment**
2. Train and evaluate AI driving agents
3. Develop sensor systems and reward functions
4. Transition concepts to a **3D Roblox environment**

The 2D simulator acts as a **controlled laboratory for experimentation** before moving to a full 3D environment.

---

# Current Features

## Core Engine

- Car physics
- Lap counting system
- Direction validation
- Timer system
- Restart system

## Track System

- Image-based tracks
- Mask-based track boundaries
- Finish line detection
- Checkpoint system

## Visual

- Top-down racing interface
- Lap progress bar
- Clean track visualization

---

# Track Technology

Tracks are processed using **pygame masks**, allowing accurate detection of:

- track limits
- finish line
- checkpoints

Example:

```python
# track mask
self.track_mask = pygame.mask.from_threshold(
    self.image,
    (255,255,255),
    (1,1,1)
)

# finish line mask
self.finish_mask = pygame.mask.from_threshold(
    self.image,
    (255,0,0),
    (1,1,1)
)
# IA-CAR Roadmap

This roadmap tracks the simulator from playable prototype to a robust RL driving platform.

## Phase 1 - Playable Prototype

Status: complete

Delivered:

- Top-down car movement
- Basic lap flow
- Timer system
- Manual restart loop

## Phase 2 - Track Architecture

Status: complete

Delivered:

- Image-based track support
- Mask-based collision checks
- Start line and checkpoint logic
- Base track abstraction

## Phase 3 - Sensor System

Status: complete

Delivered:

- Raycast-based distance sensing
- Multi-angle perception
- Sensor visualization in debug mode
- Headless-compatible sensor updates

## Phase 4 - Reinforcement Learning Environment

Status: complete

Delivered:

- Resettable training environment
- Track-independent progress/alignment features
- Normalized state representation
- Reward shaping around progress, alignment, speed, and danger
- Episode termination for collision, timeout, and stuck behavior

## Phase 5 - Q-Learning Training Stack

Status: in progress

Delivered:

- Q-table agent
- Experience replay
- n-step updates
- TD-error-based replay prioritization
- Weighted exploration actions
- Headless training flow
- Diagnostic dashboard
- Saved-model metrics snapshots

Current bottleneck:

- The agent advances consistently on `Track1` but still struggles to convert early progress into full lap completion.

## Phase 6 - Multi-Track Generalization

Status: partially implemented

Delivered:

- Circular track
- Oval track
- Complex procedural track
- Unified track progress interface

Next work:

- Stronger evaluation protocol across tracks
- Better generalization benchmarks
- Cleaner model selection between `Track1` and procedural pools

## Phase 7 - Policy Quality Upgrades

Status: future

Possible directions:

- Better action-space design
- More robust lap completion rewards
- Improved steering stability
- Transition from Q-table to function approximation if state complexity grows further

## Long-Term Goal

Transfer the useful driving behavior, trajectory logic, and racing-line optimization concepts
from the 2D simulator into a future 3D Roblox racing system.

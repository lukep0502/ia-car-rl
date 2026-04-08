# AI Car RL Roadmap

This roadmap tracks the simulator from playable prototype to a more structured RL driving platform.

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

Status: complete as the final Q-table version

Delivered:

- Q-table agent
- Experience replay
- n-step updates
- TD-error-based replay prioritization
- Weighted exploration actions
- Headless training flow
- Diagnostic dashboard
- Saved-model metrics snapshots

Conclusion:

- The Q-table stack was valuable for learning and experimentation.
- It is no longer the preferred direction for future scaling.
- This repository now serves as the final Q-table baseline.

## Phase 6 - Multi-Track Expansion

Status: implemented for the current repository scope

Delivered:

- Circular track
- Oval track
- Complex procedural track
- Unified track progress interface
- Startup track-selection flow
- Best trained models for `circular-track`, `oval-track`, and `track1`

Current note:

- Multi-track support now exists, but the Q-table approach does not scale well enough to remain the long-term solution.

## Phase 7 - Post Q-Table Future

Status: future

Possible directions:

- More scalable learning approaches
- Better generalization benchmarks
- Improved evaluation workflows
- Stronger policy learning beyond Q-table methods

## Project Standardization

Status: complete

Delivered:

- English-standardized code comments
- English prompts and runtime output
- English project documentation

## Long-Term Goal

Transfer the useful driving behavior, trajectory logic, and racing-line optimization concepts
from the 2D simulator into a future 3D Roblox racing system.

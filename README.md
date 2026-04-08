# AI Car RL

Top-down racing simulator built with Pygame for reinforcement learning experiments.

This project started as a simple AI car prototype and evolved into a multi-track reinforcement learning sandbox with saved models, training diagnostics, debug overlays, and a startup flow for selecting tracks and model behavior. The current repository represents the final Q-table-based version of the project.

## Project Overview

The goal of the project is to train a car to drive around 2D racing tracks using reinforcement learning concepts such as:

- sensor-based perception
- checkpoint and lap progression
- reward shaping
- iterative training with saved models

What began as a single-track experiment now supports multiple tracks, multiple saved models, and a more organized structure for training and evaluation.

## Current State

The repository currently includes:

- manual driving mode
- AI mode with training and evaluation flow
- image-based and procedural tracks
- circular, oval, and `Track1` support
- best trained models for each main track
- debug overlays and terminal training metrics
- English-standardized code, comments, prompts, and documentation

## New Implementations

### Best Trained Models

The project now ships with best trained models for the three main tracks:

| Track | Model File | Main Path |
| --- | --- | --- |
| Circular Track | `ia_car_vBestVersionCircular.pkl` | `src/models/best-models/q table/circular-track/` |
| Oval Track | `ia_car_vBestVersionOval.pkl` | `src/models/best-models/q table/oval-track/` |
| Track1 | `ia_car_vBestVersionTrack1.pkl` | `src/models/best-models/q table/track1/` |

The same best-model files are also available in `src/models/` for direct loading from the application.

### Startup Menu and Selection Flow

A simple startup selection flow was added to make testing and evaluation easier.

It now allows you to:

- choose the track at startup
- choose whether to run in AI mode
- choose whether to use the best trained model for the selected track
- choose whether to load another saved model
- train from scratch if no model is selected

This makes the project much easier to explore than the earlier single-track training flow.

## Q-Table Deprecation

> This is the final version of the project that uses a Q-table approach.

The Q-table approach has now been discontinued as the long-term direction for the project.

Why:

- it is too limited for scaling across multiple tracks and richer state spaces
- it works better in simpler or more isolated environments
- it becomes harder to maintain and generalize as the project grows

The Q-table implementation remains in this repository as an important learning milestone and as the final reference version of this phase of the project.

## Why This Repository Matters

Even as a final Q-table version, the project already includes several meaningful improvements over the earlier prototype:

- unified track progress features
- saved model statistics
- stronger reward shaping
- weighted exploration and replay improvements
- multiple track support
- curated best-model checkpoints
- better startup UX through the menu and model-selection flow

## Language Standardization

The project has been standardized to English.

This includes:

- source code prompts and printed output
- code comments
- README and project documentation

The goal was to make the repository more accessible, easier to share, and easier to maintain.

## Installation

### Requirements

- Python 3.12+
- `pygame`
- `tqdm`

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the project with:

```bash
python src/main.py
```

### Startup Flow

When the application starts, the current flow is:

1. Choose a track.
2. Choose whether to use AI mode.
3. If AI mode is enabled, choose whether to use the best trained model for that track.
4. Optionally load another saved model or train from scratch.

### Manual Controls

- `W`: accelerate
- `S`: brake
- `A`: steer left
- `D`: steer right
- `R`: restart
- `ESC`: quit

### AI Debug Controls

- `Q`: toggle debug information during AI runs

## Project Structure

```text
src/
  ai/          agent, reward system, normalization, trainer
  core/        car and environment logic
  menu/        startup track-selection menu
  models/      saved checkpoints and best trained models
  rendering/   game renderer and overlays
  sensors/     raycasting and sensor orchestration
  tracks/      image-based and procedural tracks
docs/
  roadmap.md
  training-metrics.md
```

## Documentation

Additional documentation is available in:

- [Roadmap](docs/roadmap.md)
- [Training Metrics](docs/training-metrics.md)

## Notes About the Current Version

- the repository includes best trained models for `oval-track`, `circular-track`, and `track1`
- the current codebase is the final Q-table branch of the project
- future improvements will likely come from new learning approaches rather than extending the Q-table further

## Project Reflection

This was my first AI project, and it represents a lot of learning, experimentation, and persistence.

Reaching this stage brings a real sense of accomplishment. It was a fun project to build, and it taught me a lot about reinforcement learning, debugging, iteration, and how quickly simple ideas become more complex in practice.

Even though the Q-table approach has reached its limit here, the project was absolutely worth it, and it opened the door for future versions built on stronger learning methods.

## Future Direction

Possible future improvements include:

- replacing the Q-table with a more scalable learning approach
- improving generalization across tracks
- expanding evaluation and benchmarking
- transferring useful driving concepts into future game projects

## Acknowledgements

Special thanks to:

- ChatGPT, especially Codex, for development help, iteration support, and documentation assistance
- GitHub Copilot for coding support during implementation
- general research, tutorials, documentation, and online learning resources that helped shape the project

## License

No license file is currently included in the repository.

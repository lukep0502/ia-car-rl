# IA-CAR

Top-down racing simulator built with Pygame for reinforcement learning experiments.

The current project focus is a **Q-learning driving agent** that learns on a 2D track using
raycast sensors, checkpoint-based progress, lap timing, and diagnostic telemetry. The long-term
goal remains transfer of the driving logic and racing-line concepts into a future 3D Roblox game.

## Current Status

The simulator is no longer just a playable prototype. It now includes:

- Manual driving mode
- AI mode with headless training
- Sensor-based state representation
- Unified cross-track progress/alignment features
- Q-learning with n-step updates and prioritized replay
- Track diagnostics and debug overlays
- Model persistence with training metrics snapshots

## Main Features

### Simulation Core

- Top-down car physics with throttle, brake, and steering
- Lap timing and multi-lap race flow
- Collision detection against image masks and procedural geometry
- Episode reset logic for training and gameplay

### Track System

- Image-based track support (`Track1`)
- Procedural track support
- Circular, oval, and complex procedural layouts
- Unified progress interface across track types
- Checkpoint and finish-line validation

### AI Training Stack

- Raycast sensor system
- Normalized state representation
- Reward system aligned with forward progress and safe speed
- Experience replay buffer
- n-step Q-learning updates
- Weighted exploration for more useful action sampling
- Diagnostic metrics for forward progress, wall proximity, exploration diversity, stuck rate, track progress, survival time, and progress efficiency

### Tooling and Debug

- Headless training path for better performance
- In-game debug mode (`Q`) with runtime and saved-training metrics
- Saved models now include a metrics snapshot for later inspection
- Neutral HUD styling for readability on both dark and light tracks

## Project Structure

```text
src/
  ai/          agent, reward, normalization, trainer
  core/        car and environment
  rendering/   game renderer and overlays
  sensors/     raycasting and sensor orchestration
  tracks/      image-based and procedural tracks
docs/
  roadmap.md
  training-metrics.md
```

## Running

### Requirements

- Python 3.12+
- `pygame`
- `tqdm`

Install dependencies:

```bash
pip install pygame tqdm
```

Start the application:

```bash
python src/main.py
```

## Modes

### Manual Mode

- Drive with `W`, `A`, `S`, `D`
- Restart with `R`
- Exit with `ESC`

### AI Mode

- Train from scratch or load a saved model
- Headless training is used before opening the visual result
- Toggle debug overlay with `Q`
- Saved models restore both Q-table parameters and training metrics

## Notes About Training

- Current training entry point uses `Track1` by default in `src/main.py`
- Procedural multi-track support exists in the trainer and track system
- Diagnostic metrics are visible in terminal during training and in-game through debug mode
- Old saved models created before metrics persistence will load without historical stats

## Documentation

- [Roadmap](docs/roadmap.md)
- [Training Metrics](docs/training-metrics.md)

## Near-Term Priorities

- Improve lap completion consistency on `Track1`
- Reduce collisions after the first quarter of the track
- Expand evaluation across procedural tracks
- Keep the debug and model-inspection workflow practical for iteration

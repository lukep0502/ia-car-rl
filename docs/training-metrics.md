# Training Metrics

This document defines the diagnostic metrics used by the IA-CAR training loop and debug overlay.

## Forward Progress Rate

How often the car produces positive track progress during training.

- `0.00 - 0.10`: very poor
- `0.10 - 0.30`: learning started
- `0.30 - 0.50`: solid
- `0.50+`: strong

## Wall Proximity Rate

How often the car is detected close to a wall.

Interpret carefully on narrow tracks: high values can still happen even when the line is valid.

- `0.70 - 1.00`: usually too close
- `0.40 - 0.70`: moderate
- `0.10 - 0.40`: good
- `0.00 - 0.10`: excellent

## Exploration Diversity

How many different actions the agent is using.

- `0.00 - 0.20`: repetitive
- `0.20 - 0.50`: limited
- `0.50 - 0.80`: healthy
- `0.80+`: broad exploration

## Stuck Rate

How often episodes end because the car fails to build useful motion.

- `0.70 - 1.00`: very poor
- `0.40 - 0.70`: poor
- `0.10 - 0.40`: acceptable
- `0.00 - 0.10`: good

## Track Completion Progress

Best normalized progress reached on the track.

- `0.00 - 0.20`: early track
- `0.20 - 0.50`: moderate progress
- `0.50 - 0.80`: close to completion
- `0.80 - 1.00`: strong
- `1.00`: lap completed

## Episode Survival Time

Average number of steps an episode survives before termination.

- `< 30`: very poor
- `30 - 100`: learning
- `100 - 300`: solid
- `300+`: very strong

## Progress Efficiency

How much movement is converted into real track progress.

- `0.00 - 0.02`: poor
- `0.02 - 0.05`: moderate
- `0.05 - 0.15`: good
- `0.15+`: strong

## Debug Overlay Notes

- The in-game debug overlay shows current-run data and saved training snapshots.
- Models saved before metrics persistence was added do not contain historical overlay stats.
- The terminal dashboard remains the authoritative 5000-episode summary during headless training.

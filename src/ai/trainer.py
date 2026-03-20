try:
    from tqdm import tqdm
except ImportError:
    # Fallback if tqdm is not installed
    def tqdm(iterable, **kwargs):
        return iterable

import os
import random
from collections import deque
from core.environment import Environment
from tracks.circular_track import CircularTrack
from tracks.oval_track import OvalTrack
from tracks.complex_track import ComplexTrack
from tracks.track1 import Track1

class Trainer:

    def __init__(self, env, agent):
        self.base_env = env
        self.env = env
        self.agent = agent
        self.width = env.track.width
        self.height = env.track.height
        if env.track.type == "image-based":
            self.track_factories = [Track1]
        else:
            self.track_factories = [
                CircularTrack,
                OvalTrack,
                ComplexTrack,
            ]

        # Global training stats
        self.best_reward_ever = float('-inf')
        self.best_lap_time_ever = None
        self.longest_distance = 0
        self.total_laps_completed = 0
        self.max_progress_ever = 0
        self.track_length = getattr(self.env.track, "progress_target", 360)

        # Adaptive exploration
        self.episodes_since_best_reward = 0
        self.epsilon_min = 0.10
        self.epsilon_max = 1.0
        self.epsilon_decay = 0.99955
        self.epsilon_boost = 0.04
        self.epsilon_boost_threshold = 900
        self.epsilon_boost_cap = 0.22

        # Wall proximity threshold (pixels) used for metrics and penalties
        self.wall_proximity_threshold = 50

        # Running diagnostic metrics for real-time display
        self.running_forward_steps = 0
        self.running_wall_steps = 0
        self.running_unique_actions = 0
        self.running_stuck = 0
        self.running_progress_delta = 0
        self.running_steps = 0
        self.running_episodes = 0

        # Benchmark history (periodic snapshots)
        self.benchmark_history = []
        self.recent_rewards = deque(maxlen=200)
        self.easy_track = CircularTrack
        self.medium_tracks = [CircularTrack, OvalTrack]
        self.all_tracks = [CircularTrack, OvalTrack, ComplexTrack]

        # Expose some stats to the environment for optional overlays
        self.agent.epsilon = self.epsilon_max
        self._sync_env_stats()

    def _sync_env_stats(self):
        self.env.best_reward_ever = self.best_reward_ever
        self.env.best_lap_time_ever = self.best_lap_time_ever
        self.env.longest_distance = self.longest_distance
        self.env.benchmark_history = self.benchmark_history

    def reset_env(self, episode):
        if self.track_factories == [Track1]:
            track_cls = Track1
        elif episode < 5000:
            track_cls = self.easy_track
        elif episode < 15000:
            track_cls = random.choice(self.medium_tracks)
        else:
            track_cls = random.choice(self.all_tracks)

        track = track_cls(self.width, self.height)
        self.env = Environment(self.width, self.height, track)
        self.env.reset()
        self.track_length = getattr(track, "progress_target", 360)
        self._sync_env_stats()

    def export_stats(self):
        return {
            "best_reward_ever": self.best_reward_ever,
            "best_lap_time_ever": self.best_lap_time_ever,
            "longest_distance": self.longest_distance,
            "benchmark_history": list(self.benchmark_history),
            "forward_progress_rate": self.running_forward_steps / self.running_steps if self.running_steps else 0.0,
            "wall_proximity_rate": self.running_wall_steps / self.running_steps if self.running_steps else 0.0,
            "exploration_diversity": (self.running_unique_actions / self.running_episodes / 9) if self.running_episodes else 0.0,
            "stuck_rate": self.running_stuck / self.running_episodes if self.running_episodes else 0.0,
            "track_completion_progress": self.max_progress_ever / self.track_length if self.track_length else 0.0,
            "episode_survival_time": self.running_steps / self.running_episodes if self.running_episodes else 0.0,
            "progress_efficiency": self.running_progress_delta / self.running_steps if self.running_steps else 0.0,
        }

    def train(self, episodes):

        pbar = tqdm(range(episodes), desc="Training")

        # Stats tracking
        rewards_window = []
        distances_window = []
        steps_window = []
        collisions_window = []
        lap_times_window = []
        laps_window = []
        best_reward = float('-inf')

        # New diagnostic metrics windows
        forward_progress_steps_window = []
        wall_proximity_steps_window = []
        unique_actions_window = []
        stuck_events_window = []
        progress_delta_window = []
        total_steps_window = []

        for episode in pbar:
            self.reset_env(episode)
            self.env.current_episode = episode + 1
            self.env.current_episode_reward = 0
            self.env.current_distance = 0
            if episode > 0:
                self.agent.epsilon = max(
                    self.epsilon_min,
                    self.agent.epsilon * self.epsilon_decay
                )

            done = False
            total_reward = 0
            steps = 0
            self.env.collision = False
            state = self.env.get_state()

            # Episode-level tracking for new metrics
            episode_actions = set()
            episode_forward_steps = 0
            episode_wall_steps = 0
            episode_progress_delta = 0
            episode_steps = 0

            while not done:
                action_index = self.agent.act(state)
                action = self.agent.action_to_dict(action_index)
                next_state, reward, done = self.env.step(action)
                total_reward += reward

                progress_delta = self.env.progress_delta

                # Track per-episode metrics for debugging/overlay
                self.env.current_episode_reward += reward
                self.env.current_distance = self.env.progress_state.get(
                    "max_progress",
                    self.env.progress_state.get("total_progress", 0)
                )

                self.agent.learn(state, action_index, reward, next_state, done)
                state = next_state
                steps += 1

                # Update episode tracking
                episode_steps += 1
                if progress_delta > 0:
                    episode_forward_steps += 1
                if self.env.sensor_values and min(self.env.sensor_values) < self.wall_proximity_threshold:  # Close to wall threshold
                    episode_wall_steps += 1
                episode_actions.add(action_index)
                episode_progress_delta += progress_delta

            # Collect stats
            rewards_window.append(total_reward)
            distances_window.append(
                self.env.progress_state.get(
                    "max_progress",
                    self.env.progress_state.get("total_progress", 0)
                )
            )
            steps_window.append(steps)
            collisions_window.append(1 if self.env.collision else 0)

            best_reward = max(best_reward, total_reward)

            # Fix: Only append lap time if a lap was completed
            if self.env.best_lap_time is not None:
                lap_times_window.append(self.env.best_lap_time)
            laps_window.append(self.env.laps)

            # Update global stats
            self.total_laps_completed += self.env.laps
            self.longest_distance = max(self.longest_distance, self.env.progress_state.get("total_progress", 0))
            self.max_progress_ever = max(self.max_progress_ever, self.env.progress_state.get("max_progress", self.env.progress_state.get("total_progress", 0)))

            if total_reward > self.best_reward_ever:
                self.best_reward_ever = total_reward
                self.episodes_since_best_reward = 0
            else:
                self.episodes_since_best_reward += 1

            if self.env.best_lap_time is not None:
                if self.best_lap_time_ever is None or self.env.best_lap_time < self.best_lap_time_ever:
                    self.best_lap_time_ever = self.env.best_lap_time

            # Append to new metrics windows
            forward_progress_steps_window.append(episode_forward_steps)
            wall_proximity_steps_window.append(episode_wall_steps)
            unique_actions_window.append(len(episode_actions))
            stuck_events_window.append(1 if self.env.stuck else 0)
            progress_delta_window.append(episode_progress_delta)
            total_steps_window.append(episode_steps)

            # Update running diagnostics for real-time overlay
            self.running_forward_steps += episode_forward_steps
            self.running_wall_steps += episode_wall_steps
            self.running_unique_actions += len(episode_actions)
            self.running_stuck += 1 if self.env.stuck else 0
            self.running_progress_delta += episode_progress_delta
            self.running_steps += episode_steps
            self.running_episodes += 1

            # Compute and set on env for overlay
            self.env.forward_progress_rate = self.running_forward_steps / self.running_steps if self.running_steps else 0
            self.env.wall_proximity_rate = self.running_wall_steps / self.running_steps if self.running_steps else 0
            self.env.exploration_diversity = (self.running_unique_actions / self.running_episodes / 9) if self.running_episodes else 0  # normalized 0-1 for 9 actions
            self.env.stuck_rate = self.running_stuck / self.running_episodes if self.running_episodes else 0
            self.env.track_completion_progress = self.max_progress_ever / self.track_length
            self.env.episode_survival_time = self.running_steps / self.running_episodes if self.running_episodes else 0
            self.env.progress_efficiency = self.running_progress_delta / self.running_steps if self.running_steps else 0

            # Make some stats accessible for rendering/overlay
            self._sync_env_stats()

            best_lap_str = f"{self.env.best_lap_time:.2f}s" if self.env.best_lap_time is not None else "N/A"

            if hasattr(pbar, 'set_postfix'):
                pbar.set_postfix({
                    "R": f"{total_reward:.1f}",
                    "L": self.env.laps,
                    "BL": best_lap_str,
                    "E": f"{self.agent.epsilon:.4f}"
                })

            # Dashboard update every 5000 episodes
            if (episode + 1) % 5000 == 0:
                avg_reward = sum(rewards_window) / len(rewards_window) if rewards_window else 0
                avg_distance = sum(distances_window) / len(distances_window) if distances_window else 0
                avg_steps = sum(steps_window) / len(steps_window) if steps_window else 0
                collision_rate = sum(collisions_window) / len(collisions_window) if collisions_window else 0
                avg_lap_time = sum(lap_times_window) / len(lap_times_window) if lap_times_window else float('inf')
                avg_laps = sum(laps_window) / len(laps_window) if laps_window else 0

                # New diagnostic metrics
                total_steps_sum = sum(total_steps_window) if total_steps_window else 1  # avoid div0
                forward_progress_rate = sum(forward_progress_steps_window) / total_steps_sum
                wall_proximity_rate = sum(wall_proximity_steps_window) / total_steps_sum
                exploration_diversity = (sum(unique_actions_window) / len(unique_actions_window) / 9) if unique_actions_window else 0  # normalized 0-1
                stuck_rate = sum(stuck_events_window) / len(stuck_events_window) if stuck_events_window else 0
                track_completion_progress = self.max_progress_ever / self.track_length
                episode_survival_time = sum(total_steps_window) / len(total_steps_window) if total_steps_window else 0
                progress_efficiency = sum(progress_delta_window) / total_steps_sum

                # Record benchmark history
                self.benchmark_history.append({
                    "episode": episode + 1,
                    "best_reward": self.best_reward_ever,
                    "best_lap_time": self.best_lap_time_ever,
                    "total_laps": self.total_laps_completed,
                    "avg_distance": avg_distance,
                    "avg_lap_time": avg_lap_time,
                    "avg_laps": avg_laps,
                })

                # Clear screen and print dashboard
                os.system('cls' if os.name == 'nt' else 'clear')
                print("================================")
                print(f"Episode: {episode + 1}")
                print(f"Epsilon: {self.agent.epsilon:.3f}")
                print(f"Avg Reward (5000): {avg_reward:.1f}")
                print(f"Best Reward: {best_reward:.1f}")
                print(f"Best Lap Time (ever): {self.best_lap_time_ever if self.best_lap_time_ever is not None else 'N/A'}")
                print(f"Avg Distance: {avg_distance:.1f}")
                print(f"Avg Lap Time: {avg_lap_time:.3f}s" if avg_lap_time != float('inf') else "Avg Lap Time: N/A")
                print(f"Avg Laps: {avg_laps:.1f}")
                print(f"Collision Rate: {collision_rate:.2f}")
                print("--- Diagnostic Metrics ---")
                print(f"Forward Progress Rate: {forward_progress_rate:.2f}")
                print(f"Wall Proximity Rate: {wall_proximity_rate:.2f}")
                print(f"Exploration Diversity: {exploration_diversity:.2f}")
                print(f"Stuck Rate: {stuck_rate:.2f}")
                print(f"Track Completion Progress: {track_completion_progress:.2f}")
                print(f"Episode Survival Time: {episode_survival_time:.1f}")
                print(f"Progress Efficiency: {progress_efficiency:.4f}")
                print("================================")

                # Reset windows
                rewards_window = []
                distances_window = []
                steps_window = []
                collisions_window = []
                lap_times_window = []
                laps_window = []
                forward_progress_steps_window = []
                wall_proximity_steps_window = []
                unique_actions_window = []
                stuck_events_window = []
                progress_delta_window = []
                total_steps_window = []
            replay_times = 4 + (4 if self.env.collision else 0) + (2 if self.env.stuck else 0)
            for _ in range(replay_times):
                self.agent.replay(64)

            if (
                episode > 1200
                and self.env.stuck
                and self.episodes_since_best_reward >= self.epsilon_boost_threshold
            ):
                self.agent.epsilon = min(
                    self.epsilon_boost_cap,
                    self.agent.epsilon + self.epsilon_boost
                )
                self.episodes_since_best_reward = 0

            self.recent_rewards.append(total_reward)

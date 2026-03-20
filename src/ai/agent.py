import random
import pickle
import os
from collections import deque

class Agent:

    def __init__(self):

        # ações possíveis
        self.actions = [

            {"accelerate": True, "brake": False, "left": False, "right": False},  # accelerate

            {"accelerate": True, "brake": False, "left": True, "right": False},   # accelerate + left

            {"accelerate": True, "brake": False, "left": False, "right": True},  # accelerate + right

            {"accelerate": False, "brake": False, "left": False, "right": False}, # coast

            {"accelerate": False, "brake": True, "left": False, "right": False},  # brake

            {"accelerate": False, "brake": True, "left": True, "right": False},   # brake + left

            {"accelerate": False, "brake": True, "left": False, "right": True},  # brake + right

            {"accelerate": False, "brake": False, "left": True, "right": False},  # coast + left

            {"accelerate": False, "brake": False, "left": False, "right": True},  # coast + right
        ]

        self.q_table = {}

        self.alpha = 0.1
        self.lr = self.alpha
        self.gamma = 0.95
        self.epsilon = 1.0

        self.epsilon_decay = 0.9997
        self.epsilon_min = 0.05

        self.memory = deque(maxlen=50000)
        self.n_step = 3
        self.n_step_buffer = deque(maxlen=self.n_step)

        self.update_scale = 0.5
        self.priority_eps = 1e-3
        self.exploration_weights = [
            0.24,  # accelerate
            0.18,  # accelerate + left
            0.18,  # accelerate + right
            0.08,  # coast
            0.05,  # brake
            0.03,  # brake + left
            0.03,  # brake + right
            0.10,  # coast + left
            0.11,  # coast + right
        ]
        self.model_stats = {}

    def get_state_key(self, state):
        state_key = []
        for i, value in enumerate(state):
            if i == len(state) - 1:
                normalized = (max(-1.0, min(1.0, value)) + 1.0) / 2.0
            else:
                normalized = max(0.0, min(1.0, value))
            state_key.append(int(normalized * 20))
        return tuple(state_key)

    def _ensure_state(self, state_key):
        if state_key not in self.q_table:
            # Mild priors help the agent prefer moving forward over freezing
            # when the table is still sparse and most rewards are negative.
            self.q_table[state_key] = [
                0.35,   # accelerate
                0.20,   # accelerate + left
                0.20,   # accelerate + right
                -0.05,  # coast
                -0.30,  # brake
                -0.35,  # brake + left
                -0.35,  # brake + right
                -0.10,  # coast + left
                -0.10,  # coast + right
            ]

    def _compute_n_step_reward(self, transitions):
        total = 0.0
        for i, (_, _, reward, _, _) in enumerate(transitions):
            total += (self.gamma ** i) * reward
        return total

    def _remember_transition(self, state_key, action, reward, next_key, done, steps):
        td_error = self._estimate_td_error(state_key, action, reward, next_key, done, steps)
        priority = abs(td_error) + self.priority_eps
        self.memory.append((priority, state_key, action, reward, next_key, done, steps))

    def _estimate_td_error(self, state_key, action, reward, next_key, done, steps):
        self._ensure_state(state_key)
        self._ensure_state(next_key)

        target = reward
        if not done:
            target += (self.gamma ** steps) * max(self.q_table[next_key])

        return target - self.q_table[state_key][action]

    def _update_q(self, state_key, action, reward, next_key, done, steps=1):
        td_error = self._estimate_td_error(state_key, action, reward, next_key, done, steps)

        self.q_table[state_key][action] += self.lr * td_error * self.update_scale
        self.q_table[state_key][action] = max(
            -100.0,
            min(100.0, self.q_table[state_key][action])
        )
        return td_error

    def act(self, state):

        state_key = self.get_state_key(state)

        # exploração
        if random.random() < self.epsilon:
            return random.choices(
                range(len(self.actions)),
                weights=self.exploration_weights,
                k=1
            )[0]

        # exploração inicial
        if state_key not in self.q_table:
            self._ensure_state(state_key)

        return self.q_table[state_key].index(max(self.q_table[state_key]))

    def learn(self, state, action, reward, next_state, done=False):
        state_key = self.get_state_key(state)
        next_key = self.get_state_key(next_state)
        self.n_step_buffer.append((state_key, action, reward, next_key, done))

        if len(self.n_step_buffer) >= self.n_step:
            self._commit_n_step_transition()

        if done:
            while self.n_step_buffer:
                self._commit_n_step_transition()

    def _commit_n_step_transition(self):
        if not self.n_step_buffer:
            return

        transitions = list(self.n_step_buffer)
        effective = []
        for transition in transitions:
            effective.append(transition)
            if transition[4]:
                break

        start_state, start_action, _, _, _ = effective[0]
        _, _, _, end_next_key, end_done = effective[-1]
        n_step_reward = self._compute_n_step_reward(effective)
        transition_steps = len(effective)

        self._remember_transition(
            start_state,
            start_action,
            n_step_reward,
            end_next_key,
            end_done,
            transition_steps
        )
        self._update_q(
            start_state,
            start_action,
            n_step_reward,
            end_next_key,
            end_done,
            transition_steps
        )
        self.n_step_buffer.popleft()

    def replay(self, batch_size=64):
        if len(self.memory) < batch_size:
            return

        batch = random.choices(
            list(self.memory),
            weights=[priority for (priority, *_rest) in self.memory],
            k=batch_size
        )

        for _, state_key, action, reward, next_key, done, steps in batch:
            self._update_q(state_key, action, reward, next_key, done, steps)

    def action_to_dict(self, action_index):
        return self.actions[action_index]

    def set_model_stats(self, stats):
        self.model_stats = dict(stats or {})

    def apply_model_stats(self, env):
        stats = self.model_stats or {}
        defaults = {
            "best_reward_ever": float("-inf"),
            "best_lap_time_ever": None,
            "longest_distance": 0,
            "benchmark_history": [],
            "forward_progress_rate": 0.0,
            "wall_proximity_rate": 0.0,
            "exploration_diversity": 0.0,
            "stuck_rate": 0.0,
            "track_completion_progress": 0.0,
            "episode_survival_time": 0.0,
            "progress_efficiency": 0.0,
        }
        for key, default in defaults.items():
            setattr(env, key, stats.get(key, default))
    
    def save(self, version="v1"):

        os.makedirs("models", exist_ok=True)

        filename = f"models/ia_car_{version}.pkl"

        data = {
            "q_table": self.q_table,
            "epsilon": self.epsilon,
            "alpha": self.lr,
            "gamma": self.gamma,
            "model_stats": self.model_stats,
        }

        with open(filename, "wb") as f:
            pickle.dump(data, f)

        print(f"Modelo salvo em: {filename}")
    
    def load(self, version):

        filename = f"models/ia_car_{version}.pkl"

        if not os.path.exists(filename):
            print("Modelo não encontrado.")
            return

        with open(filename, "rb") as f:
            data = pickle.load(f)

        self.q_table = data["q_table"]
        self.epsilon = data["epsilon"]
        self.alpha = data["alpha"]
        self.lr = self.alpha
        self.gamma = data["gamma"]
        self.model_stats = data.get("model_stats", {})

        print(f"Modelo carregado: {filename}")

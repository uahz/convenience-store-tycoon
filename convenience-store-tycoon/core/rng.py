"""可播种、可序列化的随机源。核心逻辑的一切随机必须经由此类，
以便存档恢复随机序列（回放/复现）并保证测试确定性。"""

import math
import random


class GameRNG:

    def __init__(self, seed=None):
        self._r = random.Random(seed)

    def random(self) -> float:
        return self._r.random()

    def randint(self, a: int, b: int) -> int:
        return self._r.randint(a, b)

    def uniform(self, a: float, b: float) -> float:
        return self._r.uniform(a, b)

    def choice(self, seq):
        return self._r.choice(seq)

    def weighted(self, pairs):
        """pairs: [(value, weight), ...] → 按权重抽取一个 value。"""
        values = [v for v, _ in pairs]
        weights = [w for _, w in pairs]
        return self._r.choices(values, weights=weights, k=1)[0]

    def poisson(self, lam: float) -> int:
        """Knuth 泊松采样，适用于本项目的 λ（<500）量级。"""
        threshold = math.exp(-lam)
        k, p = 0, 1.0
        while True:
            p *= self._r.random()
            if p <= threshold:
                return k
            k += 1

    # ---------- 序列化 ----------
    def to_save(self) -> dict:
        version, state, gauss = self._r.getstate()
        return {"version": version, "state": list(state), "gauss": gauss}

    @classmethod
    def from_save(cls, data: dict) -> "GameRNG":
        rng = cls.__new__(cls)
        rng._r = random.Random()
        rng._r.setstate((int(data["version"]),
                         tuple(int(x) for x in data["state"]),
                         data["gauss"]))
        return rng

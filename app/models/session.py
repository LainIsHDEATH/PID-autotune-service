import time
from typing import List, Optional
import pandas as pd
from app.utils.tune_fopdt import identify_fopdt, cohen_coon
from app.config import DELTA_PC, PERIOD_S, DT_S, STORE_API
import requests

class Session:
    def __init__(self, room_id: int, iterations: int, timestepSeconds: int = DT_S, deltaPc: float = DELTA_PC, periodSeconds: int = PERIOD_S):
        self.id = str(0)
        self.room_id = room_id
        self.N = iterations
        self.timestepSeconds = timestepSeconds
        self.deltaPc = deltaPc
        self.periodSeconds = periodSeconds
        self.log: List[tuple] = []
        self.start_ts = time.time()
        self.done = False
        self.kp = self.ki = self.kd = None

    def relay_power(self) -> float:
        sign = 1 if int((time.time()-self.start_ts)//self.periodSeconds) % 2 == 0 else -1
        return sign * self.deltaPc

    def append(self, p, T):
        self.log.append((time.time()-self.start_ts, p, T))

    def finished(self) -> bool:
        return len(self.log) >= self.N

    def compute_and_store(self):
        if self.done:
            return
        df = pd.DataFrame(self.log, columns=["timestamp", "power", "temp"])
        K, tau, theta = identify_fopdt(df)
        self.kp, self.ki, self.kd = cohen_coon(K, tau, theta)
        self.done = True

        dto = {
            "kp": self.kp, "ki": self.ki, "kd": self.kd,
            "tunedMethod": "CohenCoon",
            "active": True
        }
        url = f"{STORE_API}/pid-configs/room-configs/{self.room_id}"
        try:
            requests.post(url, json=dto, timeout=5)
        except Exception as exc:
            print("STORE POST failed:", exc)

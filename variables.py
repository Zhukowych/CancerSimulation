"""Variables"""
import numpy as np

class Variables:
    """Variables"""

    def __init__(self) -> None:
        self.p0 = 0.7
        self.ap = 0.42
        self.bn = 0.53

        self.Rt = 0
        self.Kc = 10
        self.Rmax = 100

        self.pdT = 0.5
        self.pdI = 0.5

        self.max_energy_level = 30
        self.necrotic_energy_level = 2
        self.quiescent_energy_level = 5

        self.treatment_start_time = 10
        self.injection_interval = 10
        self.time_constant = 3

        self.time_delta = 5

        self.time = 0

    @property
    def Wp(self) -> float:
        return self.ap * self.Rt ** (2/3)

    @property
    def Rn(self) -> float:
        return self.Rt - self.bn * self.Rt ** (2/3)
    
    @property
    def days_elapsed(self) -> int:
        return self.time // 24

    def time_step(self):
        self.time += self.time_delta


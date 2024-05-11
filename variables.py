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


        self.yPC = 0.55
        self.yQ = 0.4
        self.yI = 0.7
        self.kPC = 0.8
        self.kQ = 0.4
        self.kI = 0.6
        self.ci = 0.5
        self.PK = 1

        self.max_energy_level = 30
        self.necrotic_energy_level = 2
        self.quiescent_energy_level = 5

        self.treatment_start_time = 10
        self.injection_interval = 10
        self.time_constant = 3

        self.drug_concentration = 10

        self.injection_number = 0
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

    @property
    def is_treatment(self) -> bool:
        """Return true if chemotherapy injection is in process"""

        # Treatment has not started yet
        if self.days_elapsed < self.treatment_start_time:
            return False

        days_from_start = self.days_elapsed - self.treatment_start_time

        # No drug in blood
        if days_from_start % self.injection_interval > self.time_constant:
            return False

        return True

    @property
    def is_injection_start(self) -> bool:
        """Return true if it is a day of injection"""

        if not self.is_treatment:
            return False

        days_from_start = self.days_elapsed - self.treatment_start_time

        if days_from_start % self.injection_interval == 0:
            return True
        return False

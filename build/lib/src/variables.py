"""Variables"""
import yaml

class Variables:
    """Variables"""

    def __init__(self,
                 name=None,
                 p0=0.7, pA=0, pS=0.1, ap=0.42, bn=0.53,
                 Kc=10, Rmax=100, pdT=0.5, pdI=0.5,
                 yPC=0.55, yQ=0.4, yI=0.7, kPC=0.8, mu=0.4, ics=0.4,
                 max_immune_cell_count=2000,
                 kQ=0.4, kI=0.6, ci=0.5, PK=1, max_energy_level=30,
                 necrotic_distance=30, quiescent_distance=30,
                 treatment_start_time=10, injection_interval=10,
                 time_constant=3, drug_concentration=0.1
                 ) -> None:
        self.name = name

        # Static variables
        self.p0 = p0
        self.pA = pA
        self.pS = pS
        self.mu = mu

        self.ics = ics
        self.max_immune_cell_count = max_immune_cell_count

        self.ap = ap
        self.bn = bn

        self.Kc = Kc
        self.Rmax = Rmax

        self.pdT = pdT
        self.pdI = pdI

        self.yPC = yPC
        self.yQ = yQ
        self.yI = yI
        self.kPC = kPC
        self.kQ = kQ
        self.kI = kI
        self.ci = ci
        self.PK = PK

        self.max_energy_level = max_energy_level
        self.necrotic_distance = necrotic_distance
        self.quiescent_distance = quiescent_distance

        self.treatment_start_time = treatment_start_time
        self.injection_interval = injection_interval
        self.time_constant = time_constant
        self.drug_concentration = drug_concentration

        # Dynamic variables
        self.Rt = 0
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

        if days_from_start % self.injection_interval == 0 and self.time % 24 == 0:
            return True
        return False


class ConfigFileException(Exception):
    """Exception for incorrect config file"""


def read_variables(filepath: str) -> list[Variables]:
    """
    Read configuration file and return list of Variables for
    each proposed simulation 
    """

    config = {}
    with open(filepath, 'r', encoding="utf8") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError:
            raise ValueError("You passed incorrect yaml file")

        variables = []

        global_variables = config.get('global')
        if not global_variables:
            raise ConfigFileException("You must define `global` section in you config file")

        simulation_list = config.get("simulations")
        if not simulation_list:
            raise ConfigFileException("You must define `simulations` section in you config file")

        for simulation_identifier, simulation_config in simulation_list.items():
            simulation_name = simulation_config.get('name')

            if not simulation_name:
                raise ConfigFileException(f"You must define `name` in simulation\
                                           {simulation_identifier}")

            simulation_variables = global_variables | simulation_config

            if len(variables) != 4:
                variables.append(Variables(**simulation_variables))
            else:
                raise ConfigFileException("You can set 4 simulations at most")

    return variables

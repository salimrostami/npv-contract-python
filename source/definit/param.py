from dataclasses import dataclass


@dataclass
class Params:
    dist: str = "uni"
    simRounds: int = 100000
    isSim: bool = False
    isFullSearch: bool = False
    isOptSearch: bool = True
    isDebug: bool = False
    ePrecision: float = 0.00001
    roundPrecision: int = 5
    minSafeSalary: int = 12


params = Params()

# dist="uni",
# simRounds=100000,
# isSim=False,
# isFullSearch=False,
# isOptSearch=True,
# isDebug=False,
# ePrecision=0.00001,
# roundPrecision=5,
# minSafeSalary=12,

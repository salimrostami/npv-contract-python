from dataclasses import dataclass


@dataclass
class Params:
    dist: str = "uni"
    simRounds: int = 100000
    isOptSearch: bool = True
    isFullSearch: bool = True
    isTmSense: bool = True
    isSim: bool = True
    isDebug: bool = False
    ePrecision: float = 0.00000001
    roundPrecision: int = 8
    minSafeSalary: int = 50


params = Params()

# dist="uni",
# simRounds=100000,
# isSim=False,
# isFullSearch=False,
# isOptSearch=True,
# isDebug=False,
# isTmSense=True,
# ePrecision=0.0000001,
# roundPrecision=7,
# minSafeSalary=12,

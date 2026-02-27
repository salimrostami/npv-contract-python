from dataclasses import dataclass


@dataclass
class Params:
    dist: str = "uni"
    simRounds: int = 100000
    isOptSearch: bool = False
    isFullSearch: bool = True
    isTmSense: bool = False
    isSim: bool = False
    isDebug: bool = False
    ePrecision: float = 0.00000001
    roundPrecision: int = 8
    minSafeSalary: int = 50
    enpvs_factor: int = 1
    "o_enpv = enpvs_factor * b_enpv --- when enpvs_factor = 0, then o_enpv independent of b_enpv"


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

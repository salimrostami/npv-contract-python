# Description: This file contains the Project class which is used to store
# the project details. The Project class has the following attributes:
from dataclasses import dataclass, field


@dataclass
class Result:
    enpv: float = None
    risk: float = None
    var: float = None


@dataclass
class ExactResults:
    builder: Result = field(default_factory=Result)
    owner: Result = field(default_factory=Result)


@dataclass
class SimResults:
    builder: Result = field(default_factory=Result)
    owner: Result = field(default_factory=Result)


@dataclass
class Project:
    proj_id: int
    c_down_pay: float
    c_uni_low_b: float
    c_uni_high_a: float
    d_expo_lambda: float
    d_uni_low_l: float
    d_uni_high_h: float
    discount_rate: float
    builder_target_enpv: float
    owner_income: float
    owner_threshold: float = None
    exact_results: ExactResults = field(default_factory=ExactResults)
    sim_results: SimResults = field(default_factory=SimResults)
    min_total_VaR: float = -1000000
    max_total_VaR: float = 0


projects = []

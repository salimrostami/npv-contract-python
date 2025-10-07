# Description: This file contains the Project class which is used to store
# the project details. The Project class has the following attributes:
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    # Only imported for type checking to avoid runtime circular imports
    from source.definit.contract import Contract


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
class bestContract:
    contract: Optional["Contract"] = None
    tvar: float = None
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
    owner_target_enpv: float = None
    owner_threshold: float = None
    exact_results: ExactResults = field(default_factory=ExactResults)
    sim_results: SimResults = field(default_factory=SimResults)
    min_total_VaR: float = -1000000
    max_total_VaR: float = 0
    lsOpt: bestContract = field(default_factory=bestContract)
    lhOpt: bestContract = field(default_factory=bestContract)
    cpOpt: bestContract = field(default_factory=bestContract)
    tmOpt: bestContract = field(default_factory=bestContract)


projects = []


def all_projects():
    try:
        projects.extend(
            [
                # c_down_pay
                Project("001", -5000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 100000),
                Project("002", -1000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 100000),
                Project("003", -2500, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 100000),
                Project("004", -7500, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 100000),
                Project("005", -15000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 100000),
                Project("006", -30000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 100000),
                # c_uni_low_b
                Project("007", -5000, -10000, -1000, 0.1, 1, 10, 0.1, 5000, 100000),
                Project("008", -5000, -20000, -1000, 0.1, 1, 10, 0.1, 5000, 100000),
                Project("009", -5000, -60000, -1000, 0.1, 1, 10, 0.1, 5000, 100000),
                Project("010", -5000, -80000, -1000, 0.1, 1, 10, 0.1, 5000, 100000),
                Project("011", -5000, -100000, -1000, 0.1, 1, 10, 0.1, 5000, 100000),
                # d_uni_high_h
                Project("012", -5000, -40000, -1000, 0.1, 1, 3, 0.1, 5000, 100000),
                Project("013", -5000, -40000, -1000, 0.1, 1, 6, 0.1, 5000, 100000),
                Project("014", -5000, -40000, -1000, 0.1, 1, 15, 0.1, 5000, 100000),
                Project("015", -5000, -40000, -1000, 0.1, 1, 30, 0.1, 5000, 100000),
                Project("016", -5000, -40000, -1000, 0.1, 1, 60, 0.1, 5000, 100000),
                # discount_rate
                Project("017", -5000, -40000, -1000, 0.1, 1, 10, 0.025, 5000, 100000),
                Project("018", -5000, -40000, -1000, 0.1, 1, 10, 0.05, 5000, 100000),
                Project("019", -5000, -40000, -1000, 0.1, 1, 10, 0.15, 5000, 100000),
                Project("020", -5000, -40000, -1000, 0.1, 1, 10, 0.25, 5000, 100000),
                Project("021", -5000, -40000, -1000, 0.1, 1, 10, 0.4, 5000, 100000),
                #
                Project("022", -5000, -40000, -1000, 0.1, 1, 10, 0.3, 5000, 50000),
                Project("023", -5000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 75000),
                Project("024", -5000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 150000),
                Project("025", -5000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 300000),
                Project("026", -5000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 500000),
            ]
        )
    except ValueError as e:
        print(e)

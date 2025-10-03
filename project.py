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
class bestLS:
    contract: any = None
    tvar: float = None
    builder: Result = field(default_factory=Result)
    owner: Result = field(default_factory=Result)


@dataclass
class bestLH:
    contract: any = None
    tvar: float = None
    builder: Result = field(default_factory=Result)
    owner: Result = field(default_factory=Result)


@dataclass
class bestCP:
    contract: any = None
    tvar: float = None
    builder: Result = field(default_factory=Result)
    owner: Result = field(default_factory=Result)


@dataclass
class bestTM:
    contract: any = None
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
    lsOpt: bestLS = field(default_factory=bestLS)
    lhOpt: bestLH = field(default_factory=bestLH)
    cpOpt: bestCP = field(default_factory=bestCP)
    tmOpt: bestTM = field(default_factory=bestTM)


projects = []


def all_projects():
    try:
        projects.extend(
            [
                # Project("001", -2000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 100000),
                Project("002", -5000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 100000),
                # Project("003", -10000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 100000),
                # Project("004", -15000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 100000),
                # Project("005", -5000, -20000, -1000, 0.1, 1, 10, 0.1, 5000, 100000),
                # Project("006", -5000, -80000, -1000, 0.1, 1, 10, 0.1, 5000, 100000),
                # Project("007", -5000, -40000, -1000, 0.1, 1, 5, 0.1, 5000, 100000),
                # Project("008", -5000, -40000, -1000, 0.1, 1, 15, 0.1, 5000, 100000),
                # Project("009", -5000, -40000, -1000, 0.1, 1, 30, 0.1, 5000, 100000),
                # Project("010", -5000, -40000, -1000, 0.1, 1, 10, 0.05, 5000, 100000),
                # Project("011", -5000, -40000, -1000, 0.1, 1, 10, 0.25, 5000, 100000),
                # Project("012", -5000, -40000, -1000, 0.1, 1, 10, 0.35, 5000, 100000),
                # Project("013", -5000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 75000),
                # Project("014", -5000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 150000),
                # Project("015", -5000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 300000),
                # Project("016", -5000, -35000, -5000, 0.1, 1, 10, 0.1, 5000, 100000),
            ]
        )
    except ValueError as e:
        print(e)

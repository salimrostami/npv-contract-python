# Description: This file contains the Project class which is used to store
# the project details. The Project class has the following attributes:
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    # Only imported for type checking to avoid runtime circular imports
    from source.definit.contract import Contract


@dataclass
class Result:
    enpv: Optional[float] = None
    risk: Optional[float] = None
    var: Optional[float] = None
    cvar: Optional[float] = None


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
    cont: Optional["Contract"] = None
    tvar: Optional[float] = None
    builder: Result = field(default_factory=Result)
    owner: Result = field(default_factory=Result)
    sim_results: SimResults = field(default_factory=SimResults)


@dataclass
class Project:
    proj_id: str
    c_down_pay: float
    c_low_b: float
    c_high_a: float
    d_lambda: float
    d_low_l: float
    d_high_h: float
    discount_rate: float
    b_t_enpv: float
    owner_income: float
    owner_target_enpv: Optional[float] = None
    owner_threshold: Optional[float] = None
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
                Project("001", -5000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 46000),
                Project("002", -1000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 46000),
                Project("003", -2500, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 46000),
                Project("004", -7500, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 46000),
                Project("005", -15000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 46000),
                Project("006", -30000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 46000),
                # c_low_b
                Project("007", -5000, -10000, -1000, 0.1, 1, 10, 0.1, 5000, 46000),
                Project("008", -5000, -20000, -1000, 0.1, 1, 10, 0.1, 5000, 46000),
                Project("009", -5000, -60000, -1000, 0.1, 1, 10, 0.1, 5000, 46000),
                Project("010", -5000, -80000, -1000, 0.1, 1, 10, 0.1, 5000, 46000),
                Project("011", -5000, -100000, -1000, 0.1, 1, 10, 0.1, 5000, 46000),
                # d_high_h
                Project("012", -5000, -40000, -1000, 0.1, 1, 3, 0.1, 5000, 46000),
                Project("013", -5000, -40000, -1000, 0.1, 1, 6, 0.1, 5000, 46000),
                Project("014", -5000, -40000, -1000, 0.1, 1, 15, 0.1, 5000, 46000),
                Project("015", -5000, -40000, -1000, 0.1, 1, 30, 0.1, 5000, 46000),
                Project("016", -5000, -40000, -1000, 0.1, 1, 60, 0.1, 5000, 46000),
                # discount_rate
                Project("017", -5000, -40000, -1000, 0.1, 1, 10, 0.025, 5000, 46000),
                Project("018", -5000, -40000, -1000, 0.1, 1, 10, 0.05, 5000, 46000),
                Project("019", -5000, -40000, -1000, 0.1, 1, 10, 0.15, 5000, 46000),
                Project("020", -5000, -40000, -1000, 0.1, 1, 10, 0.25, 5000, 46000),
                Project("021", -5000, -40000, -1000, 0.1, 1, 10, 0.4, 5000, 46000),
                # owner's income
                Project("022", -5000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 20000),
                Project("023", -5000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 30000),
                Project("024", -5000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 60000),
                Project("025", -5000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 80000),
                Project("026", -5000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 100000),
            ]
        )
    except ValueError as e:
        print(e)


"""
# Project("022", -5000, -40000, -1000, 0.1, 1, 10, 0.3, 5000, 50000),
# # this project causes lh better than cp: investigate
ls        	59572.0446	0         	0         	5000.0    	-2449.84481731	36.5537
36.63251191	0.0       	0         	-8126.38008592	-3745.80144097	-11882.63012049	-11872.18152689
cp        	57558.9309	0.0789    	0         	5000.0    	-2449.84481731	36.3565
36.36064006	0.6529    	0.6438712 	-8067.24097886	-3730.6523804	-11804.69683506	-11797.89335926
lh        	38873.7044	0         	5617.0608 	5000.0    	-2449.84481731	16.842
16.88007712	0.0       	0         	-6153.01493036	-1343.55495868	-7488.38375795	-7496.56988903
tm        	38380.0262	0.011     	5675.1854 	5000.0    	-2449.84481731	16.6294
16.59037528	0.0       	0         	-6125.68506989	-1362.02709599	-7480.17253416	-7487.71216588
"""

"""
# c_down_pay
Project("001", -5000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 100000),
Project("002", -1000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 100000),
Project("003", -2500, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 100000),
Project("004", -7500, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 100000),
Project("005", -15000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 100000),
Project("006", -30000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 100000),
# c_low_b
Project("007", -5000, -10000, -1000, 0.1, 1, 10, 0.1, 5000, 100000),
Project("008", -5000, -20000, -1000, 0.1, 1, 10, 0.1, 5000, 100000),
Project("009", -5000, -60000, -1000, 0.1, 1, 10, 0.1, 5000, 100000),
Project("010", -5000, -80000, -1000, 0.1, 1, 10, 0.1, 5000, 100000),
Project("011", -5000, -100000, -1000, 0.1, 1, 10, 0.1, 5000, 100000),
# d_high_h
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
# owner's income
Project("022", -5000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 50000),
Project("023", -5000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 75000),
Project("024", -5000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 150000),
Project("025", -5000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 200000),
Project("026", -5000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 250000),
# experimental projects
Project("022", -5000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 50000),
Project("023", -5000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 75000),
Project("024", -5000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 150000),
Project("025", -5000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 200000),
Project("026", -5000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 250000),
Project("026", -5000, -40000, -1000, 0.1, 1, 10, 0.1, 5000, 250000),
"""

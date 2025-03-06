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


# # Example Usage
# project_instance = Project(
#     proj_id=1,
#     c_down_pay=1000.0,
#     c_uni_low_b=500.0,
#     c_uni_high_a=2000.0,
#     d_expo_lambda=0.1,
#     d_uni_low_l=5.0,
#     d_uni_high_h=15.0,
#     discount_rate=0.05,
#     builder_target_enpv=5000.0,
#     owner_income=10000.0,
# )


# class Project:
#     def __init__(
#         self,
#         proj_id,
#         c_down_pay,
#         c_uni_low_b,
#         c_uni_high_a,
#         d_expo_lambda,
#         d_uni_low_l,
#         d_uni_high_h,
#         discount_rate,
#         builder_target_enpv,
#         owner_income,
#     ):
#         self.id = proj_id
#         self.c_down_pay = c_down_pay
#         self.c_uni_low_b = c_uni_low_b
#         self.c_uni_high_a = c_uni_high_a
#         self.d_expo_lambda = d_expo_lambda
#         self.d_uni_low_l = d_uni_low_l
#         self.d_uni_high_h = d_uni_high_h
#         self.discount_rate = discount_rate
#         self.builder_target_enpv = builder_target_enpv
#         self.owner_threshold = None
#         self.owner_income = owner_income
#         self.exact_results = {
#             "builder": {
#                 "enpv": None,
#                 "risk": None,
#                 "var": None,
#             },
#             "owner": {
#                 "enpv": None,
#                 "risk": None,
#                 "var": None,
#             },
#         }
#         self.sim_results = {
#             "builder": {
#                 "enpv": None,
#                 "risk": None,
#                 "var": None,
#             },
#             "owner": {
#                 "enpv": None,
#                 "risk": None,
#                 "var": None,
#             },
#         }


projects = []

# projects.append(Project("001", -4500, -10000, 0, 0.1, 1, 2, 0.1, 0, 1500, 100000))

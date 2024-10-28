# Description: This file contains the Project class which is used to store
# the project details. The Project class has the following attributes:
class Project:
    def __init__(
        self,
        proj_id,
        c_down_pay,
        c_uni_low_b,
        c_uni_high_a,
        d_expo_lambda,
        d_uni_low_l,
        d_uni_high_h,
        discount_rate,
        builder_threshold,
        builder_target_enpv,
        owner_income,
    ):
        self.id = proj_id
        self.c_down_pay = c_down_pay
        self.c_uni_low_b = c_uni_low_b
        self.c_uni_high_a = c_uni_high_a
        self.d_expo_lambda = d_expo_lambda
        self.d_uni_low_l = d_uni_low_l
        self.d_uni_high_h = d_uni_high_h
        self.discount_rate = discount_rate
        self.builder_threshold = builder_threshold
        self.builder_target_enpv = builder_target_enpv
        self.owner_threshold = None
        self.owner_income = owner_income


projects = []

# projects.append(Project("001", -4500, -10000, 0, 0.1, 1, 2, 0.1, 0, 1500, 100000))

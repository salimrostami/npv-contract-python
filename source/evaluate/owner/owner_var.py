from source.definit.project import Project
from source.definit.contract import Contract
from source.evaluate.owner.owner_risk import owner_risk
from source.definit.param import params


def owner_var(
    proj: Project,
    cont: Contract,
    target_probability,
    x_start: float | None = None,
):
    # Compute x_low and x_high
    x = proj.owner_threshold if x_start is None else x_start
    prob = owner_risk(proj, cont, x)
    if prob < target_probability:
        x_low = x
        while True:
            x += abs(proj.owner_target_enpv) / 10
            prob = owner_risk(proj, cont, x)
            if prob > target_probability:
                x_high = x
                break
            else:
                x_low = x
    elif prob > target_probability:
        x_high = x
        while True:
            x -= abs(proj.owner_target_enpv) / 10
            prob = owner_risk(proj, cont, x)
            if prob < target_probability:
                x_low = x
                break
            else:
                x_high = x
    else:
        return x

    # Compute VaR
    var = binary_search_var(proj, cont, target_probability, x_low, x_high)
    return var


def binary_search_var(
    proj: Project,
    cont: Contract,
    target_probability,
    x_low,
    x_high,
):
    while x_high - x_low > params.ePrecision:
        x_mid = (x_low + x_high) / 2
        prob = owner_risk(proj, cont, x_mid)
        if prob < target_probability:
            x_low = x_mid
        elif prob > target_probability:
            x_high = x_mid
        else:
            return x_mid
    return (x_low + x_high) / 2

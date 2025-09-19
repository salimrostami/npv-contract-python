from project import Project
from contract import Contract
from owner_risk import owner_risk


def owner_var(project: Project, contract: Contract, distribution, target_probability):
    # Compute x_low and x_high
    x = project.owner_threshold
    prob = owner_risk(project, contract, distribution, x)
    if prob < target_probability:
        x_low = x
        while True:
            x += project.owner_threshold / 10
            prob = owner_risk(project, contract, distribution, x)
            if prob > target_probability:
                x_high = x
                break
            else:
                x_low = x
    elif prob > target_probability:
        x_high = x
        while True:
            x -= project.owner_threshold / 10
            prob = owner_risk(project, contract, distribution, x)
            if prob < target_probability:
                x_low = x
                break
            else:
                x_high = x
    else:
        return x

    # Compute VaR
    var = binary_search_var(
        project, contract, distribution, target_probability, x_low, x_high, tol=0.000001
    )
    return var


def binary_search_var(
    project: Project,
    contract: Contract,
    distribution,
    target_probability,
    x_low,
    x_high,
    tol,
):
    while x_high - x_low > tol:
        x_mid = (x_low + x_high) / 2
        prob = owner_risk(project, contract, distribution, x_mid)
        if prob < target_probability:
            x_low = x_mid
        elif prob > target_probability:
            x_high = x_mid
        else:
            return x_mid
    return (x_low + x_high) / 2

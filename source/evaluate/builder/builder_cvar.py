from source.definit.project import Project
from source.definit.contract import Contract
from source.evaluate.builder.builder_var import builder_var


def builder_CVaR(
    proj: Project,
    cont: Contract,
    confidence_level: float = 0.95,
    n_alpha: int = 20,
) -> float:
    if not 0 < confidence_level < 1:
        raise ValueError("confidence_level must be in (0, 1).")
    if n_alpha <= 0:
        raise ValueError("n_alpha must be a positive integer.")

    tail_probability = 1 - confidence_level
    alpha_values = [tail_probability * (i + 1) / n_alpha for i in range(n_alpha)]
    var_values = []
    x_start = None
    for alpha in alpha_values:
        var = builder_var(proj, cont, alpha, x_start=x_start)
        var_values.append(var)
        x_start = var
    return sum(var_values) / len(var_values)


def builder_cvar(
    proj: Project,
    cont: Contract,
    confidence_level: float = 0.95,
    n_alpha: int = 20,
) -> float:
    return builder_CVaR(proj, cont, confidence_level, n_alpha)

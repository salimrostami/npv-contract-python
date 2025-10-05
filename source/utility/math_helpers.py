import numpy as np
from scipy.special import lambertw
from decimal import Decimal, ROUND_HALF_UP


def compute_lambert_w(z):
    z_real = np.real(z)
    threshold = -1 / np.e
    # Calculate the principal branch W_0, defined only for z in the range [-1/e, +inf)
    # if z_real == np.inf:
    #     print(f"{lambertw(z, k=0)}")
    W0 = lambertw(z, k=0) if z_real >= threshold else None
    # Calculate the second branch W_{-1}, defined only for z in the range [-1/e, 0)
    W_minus_1 = lambertw(z, k=-1) if threshold <= z_real <= 0 else None
    return W0, W_minus_1


def get_common_interval(interval1, interval2):
    # Find the maximum of the starting points and the minimum of the ending points
    if None in (interval1[0], interval1[1], interval2[0], interval2[1]):
        return None, None
    else:
        start, end = max(interval1[0], interval2[0]), min(interval1[1], interval2[1])
        return (start, end) if start <= end else (None, None)


def build_interval(low, high):
    if low is None and high is None:
        return (None, None)
    elif low is None and high is not None:
        return (0, max(high, 0))
    elif low is not None and high is None:
        return (low, None)
    elif low <= max(high, 0):
        return (low, max(high, 0))
    else:
        raise ValueError("Invalid interval: low must be less than or equal to high.")


def precise_round(value, decimals):
    quant = Decimal("1e-" + str(decimals))
    return Decimal(str(value)).quantize(quant, rounding=ROUND_HALF_UP)

import numpy as np
from scipy.special import lambertw


def compute_lambert_w(z):
    z_real = np.real(z)
    threshold = -1 / np.e
    # Calculate the principal branch W_0, defined only for z in the range [-1/e, +inf)
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

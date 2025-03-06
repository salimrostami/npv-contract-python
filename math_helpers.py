import numpy as np
from scipy.special import lambertw


def compute_lambert_w(z):
    # Calculate the principal branch W_0
    # This is defined only for z in the range [-1/e, +inf)
    if np.real(z) >= -1 / np.e:
        W0 = lambertw(z, k=0)
    else:
        W0 = None

    # Calculate the second branch W_{-1}
    # This is defined only for z in the range [-1/e, 0)
    if np.real(z) >= -1 / np.e and np.real(z) < 0:
        W_minus_1 = lambertw(z, k=-1)
    else:
        W_minus_1 = None

    return W0, W_minus_1


def get_common_interval(interval1, interval2):
    # Find the maximum of the starting points and the minimum of the ending points
    if (
        interval1[0] is None
        or interval1[1] is None
        or interval2[0] is None
        or interval2[1] is None
    ):
        return None, None  # No intersection
    else:
        start = max(interval1[0], interval2[0])
        end = min(interval1[1], interval2[1])
        # Check if there is a valid intersection
        if start > end:
            return None, None  # No intersection
        else:  # start <= end:
            return start, end  # Return the intersection min and max

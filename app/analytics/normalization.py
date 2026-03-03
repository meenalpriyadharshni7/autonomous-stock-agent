import numpy as np


def min_max_normalize(series):
    min_val = series.min()
    max_val = series.max()

    if max_val - min_val == 0:
        return series * 0 + 50

    return 100 * (series - min_val) / (max_val - min_val)


def z_score(series):
    mean = series.mean()
    std = series.std()

    if std == 0:
        return series * 0

    return (series - mean) / std
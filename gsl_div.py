from collections import defaultdict
from functools import partial

import numpy
from matplotlib import pyplot

from constants import PENNANT_MODEL_OPTIMUM_PARAMETERS
from pygsl_div.pygsl_div import gsl_div
from smm import simulate, simulate_linear_oracle, get_time_series_from_trade, simulate_noisy_linear_oracle, \
    simulate_oscillating_linear_oracle, simulate_identity
from utils import get_test_data

simulators = {
    'pennant_model': partial(simulate, PENNANT_MODEL_OPTIMUM_PARAMETERS),
    'linear_oracle': simulate_linear_oracle,
    'noisy_linear_oracle': simulate_noisy_linear_oracle,
    'oscillating_linear_oracle': simulate_oscillating_linear_oracle,
    'identity': simulate_identity,
}


def get_growth_series(series: list):
    last_price = series[0]
    result = []
    for i, number in enumerate(series):
        result.append(number / last_price)
        last_price = number
    return result


if __name__ == '__main__':
    test_data, _ = get_test_data(1)
    divergences = defaultdict(list)
    for trade in test_data:
        real_time_series = get_time_series_from_trade(trade)
        # pyplot.plot(range(len(real_time_series)), real_time_series, label='real')
        for simulator_name, simulator in simulators.items():
            simulated_time_series = simulator(real_time_series)
            # pyplot.plot(range(len(simulated_time_series)), simulated_time_series, label=simulator_name)
            divergences[simulator_name].append(gsl_div(
                numpy.array([get_growth_series(real_time_series)]),
                numpy.array([get_growth_series(simulated_time_series)]),
            ))
        # pyplot.legend()
        # pyplot.show()
        for simulator_name, divs in divergences.items():
            print(simulator_name, numpy.mean(divs))
        print()

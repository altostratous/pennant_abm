from abc import ABC, abstractmethod
import numpy

from utils import get_test_data, get_simulation_hint_series
from pennant_miner import mine_time_series
from pennant_model import MarketCore
from constants import VARIATIONS
from copy import copy
from utils import pw
import random


class StylizedFact:

    def __init__(self, real_data, simulated_data) -> None:
        self.real_data = real_data
        self.simulated_data = simulated_data
        super().__init__()

    @classmethod
    @abstractmethod
    def extract_fact(cls, price_time_series: list):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def desired_moments(cls, facts):
        raise NotImplementedError

    @classmethod
    def extract_facts(cls, data: list):
        result = []
        for datum in data:
            fact = cls.extract_fact(datum)
            if fact is not None:
                result.append(fact)
        return result

    def get_real_moments(self):
        real_facts = self.extract_facts(self.real_data)
        return self.desired_moments(real_facts)

    def get_simulated_moments(self):
        simulated_facts = self.extract_facts(self.simulated_data)
        return self.desired_moments(simulated_facts)

    def get_moments_error(self, w):
        real_moments = self.get_real_moments()
        simulated_moments = self.get_simulated_moments()
        real_moments_matrix = numpy.array(real_moments)
        simulated_moments_matrix = numpy.array(simulated_moments)
        moments_error = numpy.matmul(real_moments_matrix - simulated_moments_matrix, w)
        return moments_error


class PennantModelStylizedFacts(StylizedFact, ABC):

    @classmethod
    def desired_moments(cls, facts):
        return numpy.mean(facts), numpy.std(facts)


class Return60(PennantModelStylizedFacts):
    @classmethod
    def extract_fact(cls, price_time_series: list):
        isin_data_set, tot_isin_profit, counter = mine_time_series(price_time_series)
        return tot_isin_profit


class Return30(Return60):

    @classmethod
    def extract_fact(cls, price_time_series: list):
        return60 = super().extract_fact(price_time_series)
        bought60 = price_time_series[-1] / (1 + return60)
        sold30 = price_time_series[-30]
        return sold30 / bought60


class PennantLength(PennantModelStylizedFacts):
    @classmethod
    def extract_fact(cls, price_time_series: list):
        isin_data_set, tot_isin_profit, counter = mine_time_series(price_time_series)
        return isin_data_set[0]['buy_point']


def smm_error(data_set, parameters, facts, w: numpy.ndarray):
    real_time_series_collection = []
    simulated_time_series_collection = []
    trade_simulation_count = 1
    pw.plan('simulations', len(data_set))
    for trade in data_set:
        real_time_series = get_time_series_from_trade(trade)
        for _ in range(trade_simulation_count):
            simulated_time_series = simulate(parameters, real_time_series)
            real_time_series_collection.append(real_time_series)
            simulated_time_series_collection.append(simulated_time_series)
        pw.done('simulations')
    fact_errors = []
    for fact in facts:
        fact_instance = fact(real_data=real_time_series_collection, simulated_data=simulated_time_series_collection)
        moments_error = fact_instance.get_moments_error(w)
        print(fact_instance, fact_instance.get_simulated_moments(), fact_instance.get_real_moments(), moments_error)
        fact_errors.append(moments_error)
    return sum(fact_errors) / len(fact_errors)


def get_time_series_from_trade(trade):
    real_time_series = [float(x[5]) for x in trade['time_series']]
    return real_time_series


def simulate(parameters, real_time_series):
    simulation_hint = get_simulation_hint_series(real_time_series)
    market = MarketCore(**parameters, closing_prices=simulation_hint)
    pw.plan('days', len(simulation_hint) - len(market.instruments[0].closing_prices))
    while len(market.instruments[0].closing_prices) < len(real_time_series):
        market.simulate_one_day()
        pw.done('days')
    simulated_time_series = market.instruments[0].closing_prices.copy()
    # pyplot.plot(range(len(real_time_series)), real_time_series)
    # pyplot.plot(range(len(real_time_series)), simulated_time_series)
    # pyplot.show()
    return simulated_time_series


def simulate_linear_oracle(real_time_series):
    simulation_hint = get_simulation_hint_series(real_time_series)
    result = copy(simulation_hint)
    number_of_steps = len(real_time_series) - len(simulation_hint)
    total_discrepancy = real_time_series[-1] - simulation_hint[-1]
    for i in range(1, number_of_steps + 1):
        result.append(simulation_hint[-1] + total_discrepancy * i / number_of_steps)
    return result


def simulate_noisy_linear_oracle(real_time_series):
    simulation_hint = get_simulation_hint_series(real_time_series)
    result = copy(simulation_hint)
    number_of_steps = len(real_time_series) - len(simulation_hint)
    total_discrepancy = real_time_series[-1] - simulation_hint[-1]
    for i in range(1, number_of_steps + 1):
        result.append(simulation_hint[-1] + total_discrepancy * i / number_of_steps + (random.random() - 0.5) * 0.05 * result[-1])
    return result


def simulate_oscillating_linear_oracle(real_time_series):
    simulation_hint = get_simulation_hint_series(real_time_series)
    result = copy(simulation_hint)
    number_of_steps = len(real_time_series) - len(simulation_hint)
    total_discrepancy = real_time_series[-1] - simulation_hint[-1]
    random_initial_phase = random.random()
    for i in range(1, number_of_steps + 1):
        result.append(
            simulation_hint[-1] + total_discrepancy * i / number_of_steps +
            simulation_hint[-1] * 0.05 * numpy.sin((4 + random_initial_phase) * numpy.pi * i / number_of_steps)
        )
    return result


def simulate_identity(real_time_series):
    return copy(real_time_series)


def smm_optimize(data_set, search_space, facts, w):
    if not search_space:
        raise ValueError('Search space must not be empty!')
    minimum_error = None
    minimal_parameters = None
    pw.plan('parameters', len(search_space))
    for parameters in search_space:
        print(parameters)
        simulation_error = smm_error(data_set, parameters, facts, w)
        if minimum_error is None or simulation_error < minimum_error:
            minimum_error = simulation_error
            minimal_parameters = parameters
        pw.done('parameters')
    return minimal_parameters


def generate_parameters_search_space(variations=VARIATIONS):
    if not variations:
        return []
    first_parameter = next(iter(variations))
    rest_of_variations = copy(variations)
    rest_of_variations.pop(first_parameter)
    rest_of_search_space = generate_parameters_search_space(rest_of_variations)
    extended_search_space = []
    for parameters in rest_of_search_space:
        for value in variations[first_parameter]:
            extended_parameters = copy(parameters)
            extended_parameters[first_parameter] = value
            extended_search_space.append(extended_parameters)
    else:
        extended_search_space.extend({
            first_parameter: value
        } for value in variations[first_parameter])
    return extended_search_space


if __name__ == '__main__':
    test_set, training_set = get_test_data()
    stylized_facts = (
        Return60,
        Return30,
    )

    parameters_search_space = generate_parameters_search_space()

    w = numpy.ones((2,))

    optimal_parameters = smm_optimize(training_set, parameters_search_space, stylized_facts, w)

    print(optimal_parameters)

    error = smm_error(test_set, optimal_parameters, stylized_facts, w)

    print(error)

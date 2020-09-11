import csv
import os
from collections import defaultdict
from matplotlib import pyplot
from random import random, choice

from pennant_miner import is_float, mine_time_series


if __name__ == '__main__':

    learning_period = 300
    test_period = learning_period + 20
    for isin_csv_path in os.listdir('tsedata/'):
        reader = csv.reader(open('tsedata/' + isin_csv_path, encoding='utf-16'))
        isin_data = []
        prices = []
        volumes = []
        for row in reader:
            if is_float(row[5]):
                prices.append(float(row[5]))
                volumes.append(float(row[6]))
                isin_data.append(row)
        if len(prices) < test_period:
            continue
        skip = choice(range(0, len(prices) - test_period + 1))
        volumes, prices = volumes[skip:], prices[skip:]
        return_model = defaultdict(float)
        for price, volume in zip(prices[:learning_period], volumes[:learning_period]):
            model_volume = sum(return_model.values())
            if model_volume:
                for p in return_model:
                    return_model[p] -= volume * return_model[p] / model_volume
            else:
                return_model[price] = volume
            return_model[price] += volume
            dc = min(return_model.values())
            for p in return_model:
                return_model[p] -= dc

            if not return_model:
                continue
            i, j = max(return_model), min(return_model)
            interval = (i - j) / 3
            if not interval:
                continue
            compressed = defaultdict(float)
            for p, v in return_model.items():
                compressed[interval * (p // interval)] += v
            pyplot.plot(*zip(*sorted(compressed.items())))
            pyplot.plot((price, price + 1), (0, max(compressed.values())))
            pyplot.title(isin_csv_path)
            pyplot.show()

import csv
import os
from random import random, choice

from pennant_miner import is_float, mine_time_series

sharping_window = 90
sharping_ratio = 0.3
pennant_speculation_window = 90

if __name__ == '__main__':

    ending_cases_with_pennant_trailing_counter = 0
    total_ending_cases_count = 0
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
        mean_volume = sum(volumes) / (1 + len(volumes))
        sharping_end_points = []
        last_is_sharping = False
        for i in range(sharping_window, len(prices)):
            sharping_window_prices = prices[i - sharping_window: i]
            sharping_window_volumes = volumes[i - sharping_window: i]
            if not min(sharping_window_prices):
                continue
            is_sharping = max(sharping_window_prices) / min(sharping_window_prices) > 1 + sharping_ratio
            if random() < 0.001:  # 0.2688900468994268 1919
            # if random() < 0.001 and is_sharping:  # 0.4411764705882353 884
            # if random() < 0.001 and not is_sharping:  # 0.11996336996336997 1092
                sharping_end_points.append(i)
            last_is_sharping = is_sharping

        for sharping_end_point in sharping_end_points:
            _, _, happened = mine_time_series(
                prices[max(0, sharping_end_point - sharping_window): sharping_end_point + pennant_speculation_window]
            )
            if happened:
                ending_cases_with_pennant_trailing_counter += 1
        total_ending_cases_count += len(sharping_end_points)

        if total_ending_cases_count:
            print(ending_cases_with_pennant_trailing_counter / total_ending_cases_count, total_ending_cases_count)

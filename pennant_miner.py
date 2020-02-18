import numpy
from sklearn.metrics import r2_score
from matplotlib import pyplot
import os
import csv
import pickle

from utils import reshape


def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def push_back_increasing(ms, p):
    while ms and p[1] >= ms[-1][1]:
        del ms[-1]
    ms.append(p)


def scale(d):
    m = numpy.mean(d)
    return (d - m) / numpy.max(numpy.abs(d - m))


linearity = 0.96
minimum_line_points = 4
pattern_days = 30
sell_delay = 60
percentage_amplitude = 0.1
maximum_first_wavelength = 2
show_success_cases = False
collect_data_set = not os.path.exists('pennant_data_set.pkl')

tot_counter = 0
isin_counter = 0
tot_profit = 0
set_of_isins = set()
set_of_experienced_isins = set()
data_set = []


def mine_time_series(price_time_series):
    global tot_isin_profit, counter, isin_data_set
    minimums = []
    maximums = []
    k = 0
    last_do = -61
    tot_isin_profit = 0
    counter = 0
    isin_data_set = []
    while k < len(price_time_series):
        price = price_time_series[k]
        i = k
        k += 1
        push_back_increasing(minimums, (i, price))
        push_back_increasing(maximums, (i, -price))
        within_month_minimums = [minimum for minimum in minimums if minimum[0] > i - pattern_days]
        within_month_maximums = [maximum for maximum in maximums if maximum[0] > i - pattern_days]
        last_extermums = sorted(within_month_maximums + within_month_minimums, key=lambda x: x[0])
        to_deletes = []
        for j in range(1, len(last_extermums)):
            if last_extermums[j][1] * last_extermums[j - 1][1] >= 0:
                to_deletes.append(j)
        for to_delete in reversed(to_deletes):
            del last_extermums[to_delete]
        within_month_minimums = [last_extermum for last_extermum in last_extermums if last_extermum[1] > 0]
        within_month_maximums = [
            (last_extermum[0], -last_extermum[1])
            for last_extermum in last_extermums
            if last_extermum[1] < 0
        ]
        if not within_month_minimums or not within_month_maximums:
            continue
        if within_month_minimums[0][0] < within_month_maximums[0][0]:
            continue
        amplitude = max(last_extermum[1] for last_extermum in last_extermums) - min(
            last_extermum[1] for last_extermum in last_extermums)
        minimums_duration = max(x[0] for x in within_month_minimums) - min(x[0] for x in within_month_minimums)
        maximums_duration = max(x[0] for x in within_month_maximums) - min(x[0] for x in within_month_maximums)

        if maximums_duration > maximum_first_wavelength * minimums_duration:
            continue
        if minimums_duration > maximum_first_wavelength * maximums_duration:
            continue
        if (
                len(within_month_maximums) >= minimum_line_points and
                len(within_month_minimums) >= minimum_line_points and
                amplitude > percentage_amplitude * price
        ):
            x1 = numpy.array([m[0] for m in within_month_minimums])
            y1 = numpy.array([-m[1] for m in within_month_minimums])
            x2 = numpy.array([m[0] for m in within_month_maximums])
            y2 = numpy.array([m[1] for m in within_month_maximums])
            x1 = scale(x1)
            x2 = scale(x2)
            y1 = scale(y1)
            y2 = scale(y2)
            s1 = r2_score(x1, y1)
            s2 = r2_score(x2, y2)
            if min(s1, s2) < linearity:
                continue
            if i - last_do < sell_delay:
                continue
            try:
                profit = (price_time_series[i + sell_delay] - price) / price - 0.02
                tot_isin_profit += profit
                last_do = i
                counter += 1

                start_point = min(
                    min(x[0] for x in within_month_maximums),
                    min(x[0] for x in within_month_maximums)
                )
                isin_data_set.append(
                    {
                        'time_series': price_time_series[start_point:i + sell_delay + 1],
                        'buy_point': i - start_point,
                    }
                )

                if profit > 0.1 and show_success_cases:
                    pyplot.xlabel(reshape('شماره‌ی روز'))
                    pyplot.ylabel(reshape('قیمت'))
                    pyplot.plot(
                        range(len(price_time_series)),
                        price_time_series
                    )
                    pyplot.plot(*zip(*within_month_maximums))
                    pyplot.plot(*zip(*within_month_minimums))
                    pyplot.tight_layout()
                    pyplot.show()
            except IndexError:
                pass
    return isin_data_set, tot_isin_profit, counter


if __name__ == '__main__':
    for isin_csv_path in os.listdir('tsedata/'):
        set_of_isins.add(isin_csv_path)
        reader = csv.reader(open('tsedata/' + isin_csv_path, encoding='utf-16'))
        isin_data = []
        prices = []
        for row in reader:
            if is_float(row[5]):
                prices.append(float(row[5]))
                isin_data.append(row)
        if len(prices) < 800:
            continue
        isin_counter += 1

        isin_data_set, tot_isin_profit, counter = mine_time_series(prices)

        if collect_data_set:
            data_set.extend(isin_data_set)
        if isin_data_set:
            set_of_experienced_isins.add(isin_csv_path)
        tot_profit += tot_isin_profit
        tot_counter += counter
        print(tot_profit / tot_counter)

    if collect_data_set:
        pickle.dump(data_set, open('pennant_data_set.pkl', mode='wb'))
    print(tot_profit / tot_counter)
    print(len(set_of_isins), len(set_of_experienced_isins))


import numpy
from sklearn.metrics import r2_score
from matplotlib import pyplot
import os
import csv


def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def turn_to_lines(minimums, param):
    last_len = len(minimums) + 1
    while last_len == len(minimums):
        last_len = len(minimums)
        caught = False
        for i in range(len(minimums) - 2, 1, -1):
            if caught:
                caught = False
                continue
            if abs((minimums[i - 1][1] + minimums[i + 1][1]) / 2 - minimums[i][1]) < minimums[i][1] * 0.005:
                del minimums[i]
                caught = True


def median(minimums, k=2):
    result = []
    for i in range(int(k / 2), len(minimums) - int(k / 2)):
        result.append(sorted(minimums[i - int(k / 2): i + int(numpy.ceil(k / 2))])[int(k / 2)])
    return result


def push_back_increasing(maximums, price):
    while maximums and price[1] >= maximums[-1][1]:
        del maximums[-1]
    maximums.append(price)


def scale(d):
    m = numpy.mean(d)
    return (d - m) / numpy.max(numpy.abs(d - m))


linearity = 0.96
minimum_line_points = 4
pattern_days = 30
sell_delay = 60
percentage_amplitude = 0.1
maximum_first_wavelength = 2

counter = 0
isin_counter = 0
tot_profit = 0
for isin_csv_path in os.listdir('data/tsedata/'):
    reader = csv.reader(open('data/tsedata/' + isin_csv_path, encoding='utf-16'))
    prices = []
    for row in reader:
        if is_float(row[5]):
            prices.append(float(row[5]))
    if len(prices) < 800:
        continue
    isin_counter += 1
    # prices = median(prices)
    minimums = []
    maximums = []
    k = 0
    last_do = -61
    while k < len(prices):
        price = prices[k]
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
        within_month_maximums = [(last_extermum[0], -last_extermum[1]) for last_extermum in last_extermums if last_extermum[1] < 0]
        if not within_month_minimums or not within_month_maximums:
            continue
        if within_month_minimums[0][0] < within_month_maximums[0][0]:
            continue
        amplitude = max(last_extermum[1] for last_extermum in last_extermums) - min(last_extermum[1] for last_extermum in last_extermums)
        minimums_duration = max(x[0] for x in within_month_minimums) - min(x[0] for x in within_month_minimums)
        maximums_duration = max(x[0] for x in within_month_maximums) - min(x[0] for x in within_month_maximums)
        # print(maximums_duration, minimums_duration)
        if maximums_duration > maximum_first_wavelength * minimums_duration:
            continue
        if minimums_duration > maximum_first_wavelength * maximums_duration:
            continue
        if len(within_month_maximums) >= minimum_line_points and len(within_month_minimums) >= minimum_line_points and amplitude > percentage_amplitude * price:
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
                profit = (prices[i + sell_delay] - price) / price - 0.02
                tot_profit += profit
                last_do = i
                counter += 1
                if profit > 0.1:
                    pyplot.plot(
                        range(len(prices)),
                        prices
                    )
                    pyplot.plot(*zip(*within_month_maximums))
                    pyplot.plot(*zip(*within_month_minimums))
                    pyplot.show()
                print(tot_profit / counter)
            except IndexError:
                pass
print(tot_profit / counter)
print(isin_counter)

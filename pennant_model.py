import random
from matplotlib import pyplot

import numpy


class NormalDistribution:

    def __init__(self, mu, sigma) -> None:
        super().__init__()
        self.mu, self.sigma = mu, sigma

    def sample(self):
        return int(numpy.random.normal(self.mu, self.sigma, 1)[0])


class BimodalNormalDistribution:

    def __init__(self, mu, sigma) -> None:
        super().__init__()
        self.mu, self.sigma = mu, sigma

    def sample(self):
        if random.random() < 0.5:
            return int(numpy.random.normal(self.mu + self.sigma, self.sigma, 1)[0])
        else:
            return int(numpy.random.normal(self.mu - self.sigma, self.sigma, 1)[0])


class UniformDistribution:
    def __init__(self, mu, sigma) -> None:
        super().__init__()
        self.mu, self.sigma = mu, sigma

    def sample(self):
        return int(numpy.random.uniform(self.mu - self.sigma, self.mu + self.sigma, 1)[0])



class Instrument:

    def __init__(self) -> None:
        super().__init__()
        self.fee = 0.02
        self.closing_prices = [1200, 1300, 1100, 1200]
        # self.prior_price_distribution = BimodalNormalDistribution(self.closing_prices[-1], 200)
        # self.prior_price_distribution = UniformDistribution(self.closing_prices[-1], 200)
        self.prior_price_distribution = NormalDistribution(self.closing_prices[-1], 200)
        self.last_high = 1300
        self.last_low = 1100
        self.day_transactions = []
        self.bid_queue = []
        self.ask_queue = []
        self.volumes = []
        self.highs = [self.last_high]
        self.lows = [self.last_low]
        self.low_log = []
        self.high_log = []

    def close(self):
        if self.day_transactions:
            self.closing_prices.append(int(round(numpy.average(self.day_transactions))))
        else:
            self.closing_prices.append(self.closing_prices[-1])
        self.volumes.append(len(self.day_transactions))
        self.day_transactions = []
        equiless = [self.closing_prices[0]]
        for p in self.closing_prices:
            if equiless[-1] != p:
                equiless.append(p)
        if equiless[-3] <= equiless[-2] > equiless[-1]:
            self.last_high = self.closing_prices[-2]
        if equiless[-3] >= equiless[-2] < equiless[-1]:
            self.last_low = self.closing_prices[-2]
        self.low_log.append(self.last_low)
        self.high_log.append(self.last_high)

    def bid(self, stock_holder, price):
        if self.ask_queue:
            highest_ask_price = self.ask_queue[0][0]
            if price <= highest_ask_price:
                self.day_transactions.append(highest_ask_price)
                stock_holder_in_queue = self.ask_queue[0][1]
                stock_holder_in_queue.basket[self] = highest_ask_price
                del stock_holder.basket[self]
                self.ask_queue = [e for e in self.ask_queue if e[1] != stock_holder_in_queue]
                self.bid_queue = [e for e in self.bid_queue if e[1] != stock_holder]
                return
        self.bid_queue.append((price, stock_holder))
        self.bid_queue.sort(key=lambda x: x[0])

    def ask(self, stock_holder, price):
        if self.bid_queue:
            lowest_bid_price = self.bid_queue[0][0]
            if price >= lowest_bid_price:
                self.day_transactions.append(lowest_bid_price)
                stock_holder.basket[self] = lowest_bid_price
                stock_holder_in_queue = self.bid_queue[0][1]
                del stock_holder_in_queue.basket[self]
                self.bid_queue = [e for e in self.bid_queue if e[1] != stock_holder_in_queue]
                self.ask_queue = [e for e in self.ask_queue if e[1] != stock_holder]
                return
        self.ask_queue.append((price, stock_holder))
        self.ask_queue.sort(key=lambda x: x[0], reverse=True)


class MarkerCore:

    def __init__(self) -> None:
        super().__init__()
        self.fee = 0.01
        # https://www.isna.ir/news/98021206602/%DA%86%D9%86%D8%AF-%D9%86%D9%81%D8%B1-%D8%AF%D8%B1-%D8%A8%D9%88%D8%B1%D8%B3-%D8%B3%D9%87%D8%A7%D9%85-%D8%AF%D8%A7%D8%B1%D9%86%D8%AF
        self.number_of_stock_holders = 84000
        # self.number_of_stock_holders = 20000
        self.number_of_instruments = 400
        self.number_of_actions_distribution = NormalDistribution(
            0.33 * self.number_of_stock_holders / self.number_of_instruments,
            numpy.sqrt(1 * self.number_of_stock_holders)
        )
        self.instruments = [
            Instrument()
        ]
        self.stock_holders = [StockHolder(self) for _ in
                              range(2 * int(self.number_of_stock_holders / self.number_of_instruments))]
        for instrument in self.instruments:
            for i in range(int(len(self.stock_holders) / 2)):
                self.stock_holders[i].initially_own(instrument)

    def simulate_single_action(self):
        random_stock_holder = random.choice(self.stock_holders)
        random_instrument = random.choice(self.instruments)
        bid_price = random_stock_holder.get_bid_price(random_instrument)
        if not bid_price:
            return
        if random_stock_holder.has(random_instrument):
            random_instrument.bid(random_stock_holder, bid_price)
        else:
            random_instrument.ask(random_stock_holder, bid_price)

    def simulate_one_day(self):
        number_of_actions = self.number_of_actions_distribution.sample()
        for _ in range(number_of_actions):
            self.simulate_single_action()
            # self.draw()
        for instrument in self.instruments:
            instrument.close()

    def draw(self):
        for instrument in self.instruments:
            x = []
            y = []
            for i, stock_holder in enumerate(self.stock_holders):
                bought_price = stock_holder.basket.get(instrument)
                x.append(i)
                if not bought_price:
                    y.append(0)
                else:
                    last_price = instrument.day_transactions[-1] if instrument.day_transactions else instrument.closing_prices[-1]
                    y.append(last_price - bought_price * (1 + self.fee))
            pyplot.plot(
                x, y,
                marker='.',
                linestyle="None"
            )
            pyplot.plot(
                range(len(instrument.volumes)),
                list(instrument.volumes)
            )
            pyplot.plot(
                range(len(instrument.high_log)),
                list(map(lambda x: x - instrument.closing_prices[0], instrument.high_log))
            )
            pyplot.plot(
                range(len(instrument.low_log)),
                list(map(lambda x: x - instrument.closing_prices[0], instrument.low_log))
            )
            pyplot.plot(
                range(len(instrument.closing_prices)),
                list(map(lambda x: x - instrument.closing_prices[0], instrument.closing_prices))
            )
            pyplot.savefig('images/{}-{}.png'.format(len(instrument.closing_prices), len(instrument.day_transactions)))
            pyplot.clf()


class StockHolder:

    def __init__(self, core) -> None:
        super().__init__()
        self.core = core
        self.basket = {}

    def initially_own(self, instrument):
        self.basket[instrument] = instrument.prior_price_distribution.sample()

    def has(self, instrument):
        return instrument in self.basket

    def get_price_perception(self, instrument):
        mean = instrument.day_transactions[-1] if instrument.day_transactions else instrument.closing_prices[-1]
        return NormalDistribution(
            mean,
            mean * 0.01
        ).sample()

    def get_bid_price(self, instrument: Instrument):
        closing = instrument.closing_prices[-1]
        bid_price = max(closing * 0.95, min(closing * 1.05, self.get_price_perception(instrument)))
        if self.tends_to_act(instrument, bid_price):
            return bid_price

    def tends_to_act(self, instrument: Instrument, bid_price):
        if instrument in self.basket:
            bought_price = self.basket.get(instrument)
            profit = bid_price - bought_price * (1 + self.core.fee)
            profit_percentage = profit / bought_price
            if bid_price <= instrument.last_high:
                probability = (bid_price - instrument.last_low) / (instrument.last_high - instrument.last_low + 1)
            else:
                probability = profit_percentage / 0.1
            # probability = (bid_price - instrument.last_low) / (instrument.last_high - instrument.last_low)
            if random.random() < probability:
                return True
        else:
            if bid_price <= instrument.last_high:
                action_probability = (instrument.last_high - bid_price) / max(instrument.last_high - instrument.last_low, 1)
            else:
                action_probability = 0.1
            # action_probability = (instrument.last_high - bid_price) / (instrument.last_high - instrument.last_low)
            if random.random() < action_probability:
                return True
        return False


market_core = MarkerCore()
for _ in range(1000):
    market_core.simulate_one_day()
    market_core.draw()
    print(market_core.instruments[0].closing_prices[-1])


# https://www.sciencedirect.com/science/article/pii/S0378437112003950
# http://taupe.free.fr/Tz/LogP/A%20Complex%20System%20View%20of%20why%20Stock%20Markets%20Crash-01-200401.pdf

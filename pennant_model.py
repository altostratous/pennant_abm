import random
from matplotlib import pyplot

from distributions import NormalDistribution
from utils import reshape
import numpy


class Instrument:

    def __init__(self,
                 prior_ask_probability=0.1,
                 initial_return_distribution=NormalDistribution,
                 closing_prices=None) -> None:
        super().__init__()
        if not closing_prices:
            closing_prices = (1200, 1300, 1100, 1200)
        self.fee = 0.02
        self.prior_ask_probability = prior_ask_probability
        self.closing_prices = list(closing_prices)
        self.highs, self.lows = self.get_past_low_highs(self.get_distinct_prices())
        self.last_high = self.highs[-1]
        self.last_low = self.lows[-1]
        self.prior_price_distribution = initial_return_distribution(
            self.closing_price,
            max(self.closing_prices) - min(self.closing_prices)
        )
        self.day_transactions = []
        self.bid_queue = []
        self.ask_queue = []
        self.volumes = []
        self.low_log = []
        self.high_log = []

    @property
    def closing_price(self):
        return self.closing_prices[-1]

    def close(self):
        if self.day_transactions:
            self.closing_prices.append(int(round(numpy.average(self.day_transactions))))
        else:
            self.closing_prices.append(self.closing_price)
        self.volumes.append(len(self.day_transactions))
        self.day_transactions = []
        distinct_prices = self.get_distinct_prices()
        assert len(distinct_prices) >= 3
        highs, lows = self.get_past_low_highs(distinct_prices[-3:])
        if highs:
            self.last_high = highs[-1]
        if lows:
            self.last_low = lows[-1]
        self.low_log.append(self.last_low)
        self.high_log.append(self.last_high)

    def get_past_low_highs(self, distinct_prices):
        highs = []
        lows = []
        for i in range(-len(distinct_prices) + 2, 0, 1):
            if distinct_prices[i - 2] <= distinct_prices[i - 1] > distinct_prices[i]:
                highs.append(self.closing_prices[-2])
            if distinct_prices[i - 2] >= distinct_prices[i - 1] < distinct_prices[i]:
                lows.append(self.closing_prices[-2])
        return highs, lows

    def get_distinct_prices(self):
        equiless = [self.closing_prices[0]]
        for p in self.closing_prices:
            if equiless[-1] != p:
                equiless.append(p)
        return equiless

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


class MarketCore:

    def __init__(self,
                 holders_to_seekers_ratio=None,
                 prior_ask_probability=None,
                 initial_return_distribution=None,
                 closing_prices=None) -> None:
        self.description = {}

        if not holders_to_seekers_ratio:
            holders_to_seekers_ratio = 1
        else:
            self.description['h.r.'] = holders_to_seekers_ratio
        if not prior_ask_probability:
            prior_ask_probability = 0.2
        else:
            self.description['p.p.'] = prior_ask_probability
        if not initial_return_distribution:
            initial_return_distribution = NormalDistribution
        else:
            self.description['r.d.'] = initial_return_distribution.verbose
        super().__init__()
        self.fee = 0.01
        self.holders_to_seekers_ratio = holders_to_seekers_ratio
        # https://www.isna.ir/news/98021206602/%DA%86%D9%86%D8%AF-%D9%86%D9%81%D8%B1-%D8%AF%D8%B1-%D8%A8%D9%88%D8%B1%D8%B3-%D8%B3%D9%87%D8%A7%D9%85-%D8%AF%D8%A7%D8%B1%D9%86%D8%AF
        self.number_of_stock_holders = 84000
        self.number_of_instruments = 400
        self.number_of_actions_distribution = NormalDistribution(
            0.33 * self.number_of_stock_holders / self.number_of_instruments,
            numpy.sqrt(1 * self.number_of_stock_holders)
        )
        self.instruments = [
            Instrument(
                prior_ask_probability=prior_ask_probability,
                initial_return_distribution=initial_return_distribution,
                closing_prices=closing_prices,
            )
        ]
        holders_to_all_ratio = self.holders_to_seekers_ratio / (1 + self.holders_to_seekers_ratio)
        all_to_holders_ratio = 1 / holders_to_all_ratio
        self.stock_holders = [StockHolder(self) for _ in
                              range(int(all_to_holders_ratio * int(
                                  self.number_of_stock_holders / self.number_of_instruments)))]
        for instrument in self.instruments:
            for i in range(int(len(self.stock_holders) / all_to_holders_ratio)):
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
                    last_price = instrument.day_transactions[-1] if instrument.day_transactions else \
                    instrument.closing_prices[-1]
                    y.append(last_price - bought_price * (1 + self.fee))
            pyplot.figure(figsize=(5, 10))
            ax = pyplot.subplot(3, 1, 1)
            pyplot.plot(
                x, y,
                marker='.',
                linestyle="None",
                label=reshape('سودها'),
            )
            pyplot.xlabel(reshape('شماره‌ی صاحب سهم'))
            pyplot.ylabel(reshape('سود صاحبان'))
            ylim_abs = 150
            ax = pyplot.subplot(3, 1, 2)
            ax.set_xlim(0, ylim_abs)
            ax.set_ylim(0, ylim_abs)
            pyplot.plot(
                range(len(instrument.volumes)),
                list(instrument.volumes),
                label=reshape('حجم'),
            )
            pyplot.xlabel(reshape('شماره‌ي روز'))
            pyplot.ylabel(reshape('حجم'))
            ax = pyplot.subplot(3, 1, 3)
            ax.set_xlim(0, ylim_abs)
            # ax.set_ylim(-ylim_abs, ylim_abs)
            pyplot.plot(
                range(len(instrument.high_log)),
                list(map(lambda x: x - instrument.closing_prices[0], instrument.high_log)),
                label=reshape('آخرین سقف'),

            )
            pyplot.plot(
                range(len(instrument.low_log)),
                list(map(lambda x: x - instrument.closing_prices[0], instrument.low_log)),
                label=reshape('آخرین کف'),
            )
            pyplot.plot(
                range(len(instrument.closing_prices)),
                list(map(lambda x: x - instrument.closing_prices[0], instrument.closing_prices)),
                label=reshape('قیمت'),
            )
            pyplot.ylabel(reshape('قیمت'))
            pyplot.xlabel(reshape('شماره‌ی روز'))
            pyplot.legend()
            pyplot.suptitle('\n'.join([
                reshape('وضعیت روز {}'.format(''.join(reversed(str(len(instrument.closing_prices)))))),
                *['{} = {}'.format(value, reshape(key)) for key, value in self.translated_description().items()],
            ]))
            pyplot.tight_layout(rect=[0, 0.05, 1, 0.92], h_pad=3)
            name = '{}-{}-{}-{}'.format(
                self.number_of_actions_distribution.slug, self.holders_to_seekers_ratio,
                instrument.prior_ask_probability, len(instrument.closing_prices))
            pyplot.savefig('images/' + name + '.png')
            pyplot.clf()
            return name

    def translated_description(self):
        return {
            translation[key]: value for key, value in self.description.items()
        }


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
                probability = (bid_price - instrument.last_low) / max(instrument.last_high - instrument.last_low, 1)
            else:
                probability = profit_percentage / 0.1
            # probability = (bid_price - instrument.last_low) / (instrument.last_high - instrument.last_low)
            if random.random() < probability:
                return True
        else:
            if bid_price <= instrument.last_high:
                action_probability = (instrument.last_high - bid_price) / max(
                    instrument.last_high - instrument.last_low, 1)
            else:
                action_probability = instrument.prior_ask_probability
            # action_probability = (instrument.last_high - bid_price) / (instrument.last_high - instrument.last_low)
            if random.random() < action_probability:
                return True
        return False

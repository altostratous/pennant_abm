import random

import numpy

from utils import reshape


class NormalDistribution:
    slug = 'normal'
    verbose = reshape('نرمال')

    def __init__(self, mu, sigma) -> None:
        super().__init__()
        self.mu, self.sigma = mu, sigma

    def sample(self):
        return int(numpy.random.normal(self.mu, self.sigma, 1)[0])


class BimodalNormalDistribution:
    slug = 'bimodal'
    verbose = reshape('نرمال دو قله‌ای')

    def __init__(self, mu, sigma) -> None:
        super().__init__()
        self.mu, self.sigma = mu, sigma

    def sample(self):
        if random.random() < 0.5:
            return int(numpy.random.normal(self.mu + self.sigma, self.sigma, 1)[0])
        else:
            return int(numpy.random.normal(self.mu - self.sigma, self.sigma, 1)[0])


class UniformDistribution:
    slug = 'uniform'
    verbose = reshape('همگن')

    def __init__(self, mu, sigma) -> None:
        super().__init__()
        self.mu, self.sigma = mu, sigma

    def sample(self):
        return int(numpy.random.uniform(self.mu - self.sigma, self.mu + self.sigma, 1)[0])
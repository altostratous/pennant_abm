from utils import get_test_data


class StylizedFact:

    def __init__(self, real_data, simulated_data) -> None:
        self.real_data = real_data
        self.simulated_data = simulated_data
        super().__init__()

    @classmethod
    @abstractmethod
    def extract_fact(cls, price_time_series: list) -> cls:
        raise NotImplementedError

    def get_normal_fitting(self):
        pass


class Return(StylizedFact):
    @classmethod
    def extract_fact(cls, price_time_series: list) -> cls:
        pass


class PennantLength(StylizedFact):
    @classmethod
    def extract_fact(cls, price_time_series: list) -> cls:
        pass


if __name__ == '__main__':
    test_set, training_set = get_test_data()

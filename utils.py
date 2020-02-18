import pickle
from collections import defaultdict
from random import shuffle

from arabic_reshaper import reshape as _reshape


def reshape(s):
    return ''.join(reversed(_reshape(s)))


def get_test_data():
    data_set = pickle.load(open('pennant_data_set.pkl', mode='rb'))  # type: list
    test_ratio = 0.99
    shuffle(data_set)
    test_separation_point = int(test_ratio * len(data_set))
    test_set, training_set = data_set[:test_separation_point], data_set[test_separation_point:]
    return test_set, training_set


class ProgressWatch:

    tracked_progress = (
        'simulations',
        'parameters'
    )

    def __init__(self) -> None:
        super().__init__()
        self.to_go = defaultdict(lambda: defaultdict(int))

    def plan(self, key, count):
        self.to_go[key]['planned'] = count
        self.to_go[key]['done'] = 0

    def done(self, key, count=1):
        self.to_go[key]['done'] += count
        if key in self.tracked_progress:
            self.report()

    def report(self):
        for key, progress in self.to_go.items():
            if key not in self.tracked_progress:
                continue
            print('{}:\tdone {}\tout of {}\t ({}\t%)'.format(
                key, progress['done'], progress['planned'],
                round(100 * progress['done'] / progress['planned'])
            ))


pw = ProgressWatch()

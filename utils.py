import pickle
from random import shuffle

from arabic_reshaper import reshape as _reshape


def reshape(s):
    return ''.join(reversed(_reshape(s)))


def get_test_data():
    data_set = pickle.load(open('pennant_data_set.pkl', mode='rb'))  # type: list
    test_ratio = 0.2
    shuffle(data_set)
    test_separation_point = int(test_ratio * len(data_set))
    test_set, training_set = data_set[:test_separation_point], data_set[test_separation_point:]
    return test_set, training_set
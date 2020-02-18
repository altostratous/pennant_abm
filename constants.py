from distributions import NormalDistribution, BimodalNormalDistribution, UniformDistribution

VARIATIONS = {
    'initial_return_distribution': (
        NormalDistribution,
        BimodalNormalDistribution,
        UniformDistribution,
    ),
    'holders_to_seekers_ratio': (
        0.02,
        0.06,
        0.1
    ),
    'prior_ask_probability': (
        0.05,
        0.2,
        0.4
    )
}
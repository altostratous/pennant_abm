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
TRANSLATION = {
    'h.r.': 'نسبت مالکین',
    'p.p.': 'احتمال ثابت تقاضا',
    'r.d.': 'توزیع اولیه‌ی سود',
    'initial_return_distribution': 'توزیع اولیه‌ی سود‌ها',
    'holders_to_seekers_ratio': 'نسبت مالکین به غیر مالکین',
    'prior_ask_probability': 'احتمال ثابت تقاضا'
}

PENNANT_MODEL_OPTIMUM_PARAMETERS = {
    parameter: values[1] for parameter, values in VARIATIONS.items()
}

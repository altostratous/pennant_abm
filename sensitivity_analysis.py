from constants import VARIATIONS, TRANSLATION
from pennant_model import MarketCore
from utils import reshape

if __name__ == '__main__':

    description_latex = 'می‌توانید '
    latex = ''
    for parameter in VARIATIONS:
        description_latex += 'نتیجه‌ی حساسیت مدل نسبت به {} را در شکل‌های '.format(
            TRANSLATION[parameter]
        )
        for value in VARIATIONS[parameter]:
            market_core = MarketCore(**{parameter: value})
            latex += '\\begin{figure}'
            for _ in range(2):
                latex += '\\begin{subfigure}{0.5\\textwidth}'
                for __ in range(45):
                    market_core.simulate_one_day()
                latex += '\\includegraphics[width=\\textwidth]{' + market_core.draw() + '.png}'
                print(market_core.instruments[0].closing_prices[-1])
                latex += '\\end{subfigure}'
            latex += '\\caption{' + 'بررسی حساسیت مدل نسبت به {} با مقدار {}'.format(
                TRANSLATION[parameter],
                reshape(value.verbose) if hasattr(value, 'verbose') else value
            ) + '}'
            label = parameter + str(value.slug if hasattr(value, 'verbose') else value)
            description_latex += '\\رجوع{' + label + '}، '
            latex += '\\label{' + label + '}\\end{figure}'

    description_latex += ' مشاهده کنید.'
    print(latex)
    print(description_latex)

import re


def parse_compensation(compensation_text):
    compensation = re.sub(r"( |– )", r"", compensation_text).split()
    min_compensation = None
    max_compensation = None
    currency = None
    if '–' in compensation_text:
        min_compensation = compensation[0]
        max_compensation = compensation[1]
        currency = compensation[2]
    elif 'от' in compensation_text:
        min_compensation = compensation[1]
        currency = compensation[2]
    elif 'до' in compensation_text:
        max_compensation = compensation[1]
        currency = compensation[2]
    return min_compensation, max_compensation, currency


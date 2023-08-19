from math import *

saved_names = []

def store(name: str, expression: str) -> None:
    globals()[name] = lambda x : eval(expression.replace("\U0001d465", str(x)))
    if name not in saved_names:
        saved_names.append(name)

def clear():
    for x in saved_names:
        del globals()[x]
    saved_names.clear()

def evaluate(expression: str, x_value: float | None = None):
    return eval(expression.replace("\U0001d465", str(x_value)))
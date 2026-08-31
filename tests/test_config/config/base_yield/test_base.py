from src.config.base_yield.base import AdditiveYield, MultiplicativeYield

dummy_additive = AdditiveYield(food=4, production = 2, gold = 4, happiness = 2, science = 2, culture = 1)

dummy_multiplicative = MultiplicativeYield(food=0.5, production = 1.2, gold = 0.9, happiness = 1.1, science = 1.3, culture = 1.0)


def test_additive_yield():
    assert isinstance(dummy_additive, AdditiveYield)

def test_mutiplicative_yield():
    assert isinstance(dummy_multiplicative, MultiplicativeYield)
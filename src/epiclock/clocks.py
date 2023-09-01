import numpy as np
import xarray as xr
from dowhy import gcm
from epiclock import get_clock_weights


class BaseClock(gcm.ml.PredictionModel):
    def __init__(self, alias=None):
        self.weights = get_clock_weights()
        if alias:
            self.weights = self.weights.sel(clock=alias)
        self.intercept = 0

    def fit(self, X, y=None):
        pass

    def predict(self, X: xr.DataArray) -> xr.DataArray:
        return self._f(self._linear_component(X))

    def _linear_component(self, X):
        return xr.dot(X, self.weights, dims='probe') + self.intercept

    def _f(self, X):
        return X

class HannumClock(BaseClock):
    def __init__(self):
        super().__init__('hannum')


class LinClock(BaseClock):
    def __init__(self):
        super().__init__('lin')
        self.intercept = 12.2169841


class PhenoAgeClock(BaseClock):
    def __init__(self):
        super().__init__('phenoage')
        self.intercept = 60.664

class Zhang2019Clock(BaseClock):
    def __init__(self):
        super().__init__('zhang2019')
        self.intercept = 65.8


class _TFormedClock(BaseClock):
    def __init__(self, alias, intercept, adult_age):
        super().__init__(alias)
        self.intercept = intercept
        self.adult_age = adult_age

    def _f(self, X):
        return tform_linear_comp(X, self.adult_age)


class Horvath1Clock(_TFormedClock):
    def __init__(self, adult_age=20):
        super().__init__('horvath1', 0.696, adult_age)


class Horvath2Clock(_TFormedClock):
    def __init__(self, adult_age=20):
        super().__init__('horvath1', -0.447119319, adult_age)


class PedbeClock(_TFormedClock):
    def __init__(self, adult_age=20):
        super().__init__('pedbe', -2.10, adult_age)


def tform_linear_comp(age_linear_comp, adult_age=20):
    return xr.where(age_linear_comp < 0,
                    (1 + adult_age) * np.exp(age_linear_comp) - 1,
                    (1 + adult_age) * age_linear_comp + adult_age)
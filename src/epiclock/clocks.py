import warnings
from typing import Callable, Dict, List, Optional, Type, Union

import numpy as np
import xarray as xr
from dowhy import gcm
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

from epiclock import get_clock_weights


_allclocks: Dict[str, List[Type[BaseEstimator]]] = {}

def register_clock(categories: List[str] = None) -> Callable[[Type], Type]:
    """A decorator factory for registering a clock class with optional categories."""

    def _decorator(cls: Type) -> Type:

        nonlocal categories
        
        if categories is None:
            categories = ['default']
        else:
            categories = [categories] if isinstance(categories, str) else categories
            if 'default' not in categories:
                categories = ['default'] + categories
        
        for category in categories:
            if category not in _allclocks:
                _allclocks[category] = []
            _allclocks[category].append(cls)
        
        return cls

    return _decorator


def list_available_clocks(category: str = 'default') -> List[str]:
    """List names of all available clock classes."""
    return [cls.__name__ for cls in _allclocks.get(category, [])]

def list_all_categories() -> List[str]:
    """List all clock categories."""
    return list(_allclocks.keys())

def list_core_clocks() -> List[str]:
    """List names of all core clock classes."""
    return list_available_clocks('core')

def tform_linear_comp(age_linear_comp: xr.DataArray, adult_age: int = 20) -> xr.DataArray:
    """Transform the linear component of age."""
    return xr.where(
        age_linear_comp < 0,
        (1 + adult_age) * np.exp(age_linear_comp) - 1,
        (1 + adult_age) * age_linear_comp + adult_age
    )


class MethylImputer(SimpleImputer):
    """Custom imputer for methylation data."""
    def transform(self, X: xr.DataArray) -> xr.DataArray:
        X.values = super().transform(X.values)
        return X


class BaseClock(BaseEstimator, TransformerMixin, gcm.ml.PredictionModel):
    """
    Base class for age clocks.
    
    This class can function both as a prediction model and as a transformer.
    It employs the same method for `transform` and `predict` to facilitate this dual functionality.
    """
    def __init__(self, alias: Optional[str] = None):
        self.weights = get_clock_weights()
        self.alias = alias if alias else 'biological_age'
        self.weights = self.weights.sel(clock=self.alias) if alias else self.weights
        self.coef_ = self.weights.to_numpy()  # Pass fit checks
        self.intercept_ = 0  # Pass fit checks
        self.is_fitted_ = True  # Pass fit checks

    def fit(self, X: xr.DataArray, y: Optional[xr.DataArray] = None) -> "BaseClock":
        if y is not None:
            warnings.warn('A target y was provided but will be ignored. '
                          f'Pre-fit weights are used for {self.__class__.__name__}, '
                          ' per the original publication.')
        return self

    def transform(self, X: xr.DataArray) -> xr.DataArray:
        return self._f(self._linear_component(X))

    predict = transform
    
    fit_predict = TransformerMixin.fit_transform

    def set_output(self, transform: Optional[str] = None) -> "BaseClock":
        if transform not in ['default', None]:
            raise NotImplementedError('Only default output is supported')
        return self

    def _linear_component(self, X: xr.DataArray) -> xr.DataArray:
        return xr.dot(X, self.weights, dims='probe') + self.intercept_

    def _f(self, X: xr.DataArray) -> xr.DataArray:
        return X

    def __repr__(self):
        return f"{self.__class__.__name__}(alias={self.alias}, intercept={self.intercept_})"

    def __str__(self):
        return f"{self.__class__.__name__} instance with alias {self.alias} and intercept {self.intercept_}"

@register_clock(categories=['core'])
class HannumClock(BaseClock):
    def __init__(self, **kwargs):
        super().__init__('hannum')

@register_clock()
class LinClock(BaseClock):
    def __init__(self, **kwargs):
        super().__init__('lin')
        self.intercept_ = 12.2169841

@register_clock(categories=['core'])
class PhenoAgeClock(BaseClock):
    def __init__(self, **kwargs):
        super().__init__('phenoage')
        self.intercept_ = 60.664

@register_clock()
class Zhang2019Clock(BaseClock):
    def __init__(self, **kwargs):
        super().__init__('zhang2019')
        self.intercept_ = 65.8

class BaseNonlinearClock(BaseClock):
    def __init__(self, alias, intercept, adult_age):
        super().__init__(alias)
        self.intercept_ = intercept
        self.adult_age = adult_age

    def _f(self, X):
        return tform_linear_comp(X, self.adult_age)

@register_clock(categories=['core'])
class Horvath1Clock(BaseNonlinearClock):
    def __init__(self, adult_age=20, **kwargs):
        super().__init__('horvath1', 0.696, adult_age)

@register_clock()
class Horvath2Clock(BaseNonlinearClock):
    def __init__(self, adult_age=20, **kwargs):
        super().__init__('horvath2', -0.447119319, adult_age)

@register_clock()
class PedbeClock(BaseNonlinearClock):
    def __init__(self, adult_age=20, **kwargs):
        super().__init__('pedbe', -2.10, adult_age)


def fit_all_clocks(data: xr.DataArray, imputer: Optional[MethylImputer] = None,
                   clocks: Optional[Union[Type[BaseEstimator], List[Type[BaseEstimator]]]] = None,
                   clock_kws: Optional[Dict] = None) -> xr.Dataset:
    """
    Convenience function to fit multiple clocks, since FeatureUnion is not supported.
    """
    if imputer is None:
        imputer = MethylImputer(strategy='constant', fill_value=0)

    if clocks is None:
        clocks = _allclocks['default']
        if len(clocks) == 0:
            raise ValueError('No clocks to fit')
    else:
        if not isinstance(clocks, list):
            clocks = [clocks]

    if clock_kws is None:
        clock_kws = {}
        
    bio_age_clocks = [
        Pipeline([('imputer', imputer), ('clock', clock(**clock_kws))]).fit_transform(data)
        for clock in clocks
    ]

    return xr.concat(bio_age_clocks, dim='clock').to_dataset(name='bio_age')

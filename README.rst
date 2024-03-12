.. image:: https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold
    :alt: Project generated with PyScaffold
    :target: https://pyscaffold.org/

|

========
epiclock
========


    Pure Python implementation of :code:`MorganLevineLab/methylCIPHER`.


Provides scikit-learn compatible "epigenetic clocks" for the common clock models provided by the :code:`MorganLevineLab/methylCIPHER` `R package`_. These models can be used as both `transformers`_ and `prediction models`_. Essentially a pure python port of that package with some different design choices. Code is in a functional state for use in personal projects.

While packaged, this is not yet a release of any kind. Use at your own risk.


.. _prediction models: https://www.pywhy.org/dowhy/v0.9.1/user_guide/gcm_based_inference/customizing_model_assignment.html
.. _R package: https://github.com/MorganLevineLab/methylCIPHER
.. _transformers: https://scikit-learn.org/stable/modules/generated/sklearn.base.TransformerMixin.html
import os
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from pkgutil import extend_path

import pandas as pd
import xarray as xr

from .assets import download_assets

try:
    dist_name = __name__
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = 'unknown'
finally:
    del version, 

LOCAL_DATA = Path(__file__).parent.parent / 'assets'
"""Point to included `epiclock/src/assets` directory for local data."""

# On init, if no assets are found, download them
if len(os.listdir(LOCAL_DATA)) == 0:
    gh_token = os.environ.get('GH_ACCESS_TOKEN', None)
    if gh_token is None:
        print('No GitHub access token found. CpG data are missing, but cannot be downloaded.')
    else:
        download_assets(gh_token, LOCAL_DATA)

def list_cpgs():
    """List all CpGs in the data source."""
    return [f for f in LOCAL_DATA.glob('*_CpGs.csv')]

def get_clock_weights() -> xr.DataArray:
    col_aliases = get_col_aliases()
    cpg_mat = []
    for cpg_path in list_cpgs():
        clock_name = cpg_path.stem
        if clock_name in ['Alcohol_CpGs', 'BMI_CpGs']:
            # Clinical covariate-associated
            continue

        if clock_name == 'MiAge_CpGs':
            # Different methodology
            continue
        
        cpg_mat.append(
            pd.read_csv(cpg_path)
            .rename(columns=col_aliases)
            .assign(clock=clock_name)
        )

    cpg_weights = (
        pd.concat(cpg_mat)
        .pivot_table(index='probe', columns='clock', values='beta')
        .rename(columns=lambda x: x.split('_CpGs')[0].lower())
        .fillna(0)
    )
    
    return xr.DataArray(cpg_weights)

def get_col_aliases():
    PROBES_COL_ALIASES = ['CpG', 'CpGs', 'ID', 'Marker', 'CpGmarker', 'id']
    WEIGHT_COL_ALIASES = ['Beta', 'coef', 'Coef', 'Weight', 'Coefficient', 'CoefficientTraining']
    probes_aliases = {k:'probe' for k in PROBES_COL_ALIASES}
    weight_aliases = {k:'beta' for k in WEIGHT_COL_ALIASES}
    col_aliases = dict()
    col_aliases.update(probes_aliases)
    col_aliases.update(weight_aliases)
    
    return col_aliases
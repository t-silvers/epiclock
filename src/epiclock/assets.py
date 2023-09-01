import os
import requests
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import rdata
from github import Github


DATA_SRC_REPO = 'MorganLevineLab/methylCIPHER'
"""Data source GitHub repository."""

DATA_SRC_DIR = 'data'
"""Data source directory."""


def download_assets(gh_token, dest):

    # Access repo
    gh = Github(gh_token)
    methylcipher_repo = gh.get_repo(DATA_SRC_REPO)
    methylcipher_data_contents = methylcipher_repo.get_contents(DATA_SRC_DIR)

    # Download all files in methylcipher_data_path
    local_data_path.mkdir(parents=True, exist_ok=True)
    
    # Download CpG files
    warnings.filterwarnings("ignore", category=UserWarning)
    
    for content in methylcipher_data_contents:
        if content.type == 'file' and 'test' not in content.name and 'README' not in content.name:
            cpg_path = local_data_path / content.name

            if not cpg_path.with_suffix('.csv').exists() and not cpg_path.with_suffix('.npy').exists():
                print(f"Downloading {content.path} to {cpg_path}")
                cpg_rdata = requests.get(content.download_url)

                # Save RData file
                with open(cpg_path, 'wb') as f:
                    f.write(cpg_rdata.content)
                    
                # Save csv file
                try:
                    cpg_rdata_parsed = rdata.parser.parse_file(cpg_path)
                    cpg_rdata_convrt = rdata.conversion.convert(cpg_rdata_parsed)
                    
                    # Check if key matches expected key
                    rdata_key = list(cpg_rdata_convrt.keys())[0]
                    expected_key = content.name.split('.')[0]
                    if rdata_key != expected_key:
                        warnings.warn(f'Key mismatch: {rdata_key} != {expected_key}')
                        expected_key = rdata_key

                    cpg_data = cpg_rdata_convrt[expected_key]
                    
                    if isinstance(cpg_data, np.ndarray):
                        np.save(cpg_path.with_suffix('.npy'), cpg_data)

                    elif isinstance(cpg_data, pd.DataFrame):
                        cpg_data.to_csv(cpg_path.with_suffix('.csv'), index=False)
                    
                    elif isinstance(cpg_data, list):
                        print(f'{content.path} is a list')
                        continue

                    else:
                        print(f'{content.path} is not a data frame or numpy array')
                        continue
                
                except NotImplementedError:
                    print(f'Could not convert {content.path} to csv')
                    continue

                except AttributeError:
                    print(f'{content.path} is not a data frame or numpy array')
                    continue
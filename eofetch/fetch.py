import os
import re

from . import cdse
from . import s5ppal

MAPPING = {
  r"^S1.*\.SAFE$": cdse.download,
  r"^S2.*\.SAFE$": cdse.download,
  r"^S3.*\.SEN3$": cdse.download,
  r"^S5P_PAL_.*\.nc$": s5ppal.download,
  r"^S5P.*\.nc$": cdse.download,
}

def download(products, target_directory=None):
    """
    Download product(s) from their source archive, skipping files that already exist.

    Supported archives are:
      - CDSE: https://dataspace.copernicus.eu
      - S5P-PAL: https://data-portal.s5p-pal.com

    Arguments:
    products -- product file/directory name or list/tuple of file/directory names
    target_directory -- path where to store products (default '.')
    """
    if isinstance(products, (list, tuple)):
        for product in products:
            download(product)
        return

    product = os.path.basename(products)
    if target_directory is None:
        target_directory = "."
    targetpath = os.path.join(target_directory, product)

    if os.path.exists(targetpath):
        return

    if not os.path.exists(target_directory):
        os.makedirs(target_directory)

    for mapping in MAPPING:
        if re.match(mapping, product) is not None:
            download_backend = MAPPING[mapping]
            download_backend(product, target_directory)
            return

    raise Exception(f"could not determine source archive for '{product}'")

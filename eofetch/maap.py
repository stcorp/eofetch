import os

from pystac_client import Client
import requests


COLLECTIONS = [
    {
        'id': 'EarthCAREL1Validated_MAAP',
        'mission': 'ECA',
        'product_types': [
            'ATL_NOM_1B',
            'AUX_JSG_1D',
            'BBR_NOM_1B',
            'BBR_SNG_1B',
            'CPR_NOM_1B',
            'MSI_NOM_1B',
            'MSI_RGR_1C',
        ],
    },
    {
        'id': 'EarthCAREXMETL1DProducts10_MAAP',
        'mission': 'ECA',
        'product_types': [
            'AUX_MET_1D',
        ],
    },
    {
        'id': 'EarthCAREL2Validated_MAAP',
        'mission': 'ECA',
        'product_types': [
            'AC__TC__2B',
            'ACM_CAP_2B',
            'ACM_COM_2B',
            'ACM_RT__2B',
            'ALL_3D__2B',
            'ALL_DF__2B',
            'AM__ACD_2B',
            'AM__CTH_2B',
            'ATL_AER_2A',
            'ATL_ALD_2A',
            'ATL_CTH_2A',
            'ATL_EBD_2A',
            'ATL_FM__2A',
            'ATL_ICE_2A',
            'ATL_TC__2A',
            'BM__RAD_2B',
            'BMA_FLX_2B',
            'CPR_CD__2A',
            'CPR_CLD_2A',
            'CPR_FMR_2A',
            'CPR_TC__2A',
            'MSI_AOT_2A',
            'MSI_CM__2A',
            'MSI_COP_2A',
        ],
    },
    {
        'id': 'JAXAL2Validated_MAAP',
        'mission': 'ECA',
        'product_types': [
            'AC__CLP_2B',
            'ACM_CLP_2B',
            'ALL_RAD_2B',
            'ATL_CLA_2A',
            'CPR_CLP_2A',
            'CPR_ECO_2A',
            'MSI_CLP_2A',
        ],
    },
    {
        'id': 'EarthCAREOrbitData_MAAP',
        'mission': 'ECA',
        'product_types': [
            'AUX_ORBPRE',
            'MPL_ORBSCT',
        ],
    },
]

COLLECTION_MAPPING = {}
for collection in COLLECTIONS:
    for product_type in collection['product_types']:
        COLLECTION_MAPPING[(collection['mission'], product_type)] = collection


def get_token():
    if "MAAP_OFFLINE_TOKEN" not in os.environ:
        raise Exception("MAAP_OFFLINE_TOKEN environment variable needs to be set to download from the ESA MAAP. "
                        "A 90-day token can be obtained via "
                        "https://portal.maap.eo.esa.int/ini/services/auth/token/90dToken.php")
    url = "https://iam.maap.eo.esa.int/realms/esa-maap/protocol/openid-connect/token"
    data = {
        "client_id": "offline-token",
        "client_secret": "p1eL7uonXs6MDxtGbgKdPVRAmnGxHpVE",
        "grant_type": "refresh_token",
        "refresh_token": os.environ["MAAP_OFFLINE_TOKEN"],
        "scope": "offline_access openid"
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    access_token = response.json().get('access_token')
    if not access_token:
        raise Exception("failed to retrieve access token from IAM response")
    return access_token


def get_url(product):
    mission = product[:3]
    product_type = product[9:19]
    productname, extension = os.path.splitext(product)
    try:
        collection = COLLECTION_MAPPING[(mission, product_type)]
    except KeyError:
        raise Exception(f"could not determine MAAP collection id for mission '{mission}' and product type "
                        f"'{product_type}'")

    catalog = Client.open("https://catalog.maap.eo.esa.int/catalogue/")
    search = catalog.search(collections=[collection["id"]], ids=productname, method="GET")
    items = list(search.items()) # Get all items as a list
    if len(items) == 0:
        raise Exception(f"could not find product '{product}' in MAAP STAC catalogue")
    if extension == ".EOF":
        return items[0].assets["enclosure_eof"].href
    if extension == ".h5":
        return items[0].assets["enclosure_h5"].href
    return items[0].assets["product"].href


def download(product, target_directory):
    url = get_url(product)
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}",
    }
    with requests.get(url, headers=headers, stream=True) as r:
        r.raise_for_status()
        with open(os.path.join(target_directory, product), 'wb') as f:
            for chunk in r.iter_content(1048576):  # use 1MB blocks
                f.write(chunk)

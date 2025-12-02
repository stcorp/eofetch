import os
import re
import tempfile
import zipfile

import requests


COLLECTIONS = [
    {
        'id': 'EarthCAREL1Validated',
        'hostname': 'ec-pdgs-dissemination1.eo.esa.int',
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
        'id': 'EarthCAREXMETL1DProducts10',
        'hostname': 'ec-pdgs-dissemination1.eo.esa.int',
        'mission': 'ECA',
        'product_types': [
            'AUX_MET_1D',
        ],
    },
    {
        'id': 'EarthCAREL2Validated',
        'hostname': 'ec-pdgs-dissemination2.eo.esa.int',
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
        'id': 'JAXAL2Validated',
        'hostname': 'ec-pdgs-dissemination1.eo.esa.int',
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
        'id': 'EarthCAREOrbitData',
        'hostname': 'ec-pdgs-dissemination1.eo.esa.int',
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


def get_session_cookies(hostname, username, password):
    response = requests.get(f"https://{hostname}/oads/access/login")
    response.raise_for_status()
    cookies = response.cookies
    for r in response.history:
        cookies = requests.cookies.merge_cookies(cookies, r.cookies)
    match = re.search(r"\?sessionDataKey=([0-9a-f-]+)&", response.text)
    session_data_key = match.group(1)

    post_data = {
       "tocommonauth": "true",
       "username": username,
       "password": password,
       "sessionDataKey": session_data_key,
    }
    response = requests.post(url="https://eoiam-idp.eo.esa.int/samlsso", data=post_data, cookies=cookies)
    response.raise_for_status()

    match = re.search("method=\"post\" action=\"([^\"]+)\"", response.text)
    response_url = match.group(1)
    match = re.search("name='RelayState' value='([^']+)'", response.text)
    relay_state = match.group(1)
    match = re.search("name='SAMLResponse' value='([^']+)'", response.text)
    saml_response = match.group(1)

    post_data = {"RelayState": relay_state, "SAMLResponse": saml_response}
    response = requests.post(url=response_url, data=post_data, cookies=cookies)
    response.raise_for_status()
    cookies = requests.cookies.merge_cookies(cookies, response.cookies)
    for r in response.history:
        cookies = requests.cookies.merge_cookies(cookies, r.cookies)
    return cookies


def download(product, target_directory):
    mission = product[:3]
    product_type = product[9:19]

    if product.endswith('.h5') or product.endswith('.EOF'):
        zipped_product = os.path.splitext(product)[0] + ".ZIP"
        with tempfile.TemporaryDirectory() as tempdir:
            download(zipped_product, tempdir)
            with zipfile.ZipFile(os.path.join(tempdir, zipped_product), 'r') as ziparchive:
                ziparchive.extract(product, target_directory)
        return

    try:
        collection = COLLECTION_MAPPING[(mission, product_type)]
    except KeyError:
        raise Exception(f"could not determine OADS collection id for mission '{mission}' and product type "
                        f"'{product_type}'")

    if "OADS_USERNAME" not in os.environ or "OADS_PASSWORD" not in os.environ:
        raise Exception("OADS_USERNAME and OADS_PASSWORD environment variables need to be set to download from OADS. "
                        "OADS credentials can be obtained by creating an account at https://eoiam-idp.eo.esa.int/")

    cookies = get_session_cookies(collection['hostname'], os.environ["OADS_USERNAME"], os.environ["OADS_PASSWORD"])

    url = f"https://{collection['hostname']}/oads/data/{collection['id']}/{product}"
    with requests.get(url, cookies=cookies, stream=True, allow_redirects=False) as r:
        r.raise_for_status()
        if r.status_code == 302:
            raise Exception(f"OADS authentication failed")
        with open(os.path.join(target_directory, product), 'wb') as f:
            for chunk in r.iter_content(1048576):  # use 1MB blocks
                f.write(chunk)

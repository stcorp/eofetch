# eofetch

This package allows for easy downloading of EO data products.

You just provide the list of filenames that you want, and, if the products
are supported, the library will automatically determine which archive to use
and will then download the product from that archive.

The library currently supports downloading data from the following archives:

- [Copernicus Dataspace Ecosystem (CDSE)](https://dataspace.copernicus.eu):
  Sentinel-1, Sentinel-2, Sentinel-3, and Sentinel-5P products
- [S5P-PAL](https://data-portal.s5p-pal.com): Pre-operational Sentinel-5P
  products


## Examples

From the command line:

```
eofetch S5P_OFFL_L2__CH4____20230501T010659_20230501T024829_28739_03_020500_20230502T170746.nc \
   S5P_PAL__L2__NO2____20211114T004748_20211114T022918_21177_02_020301_20211215T133738.nc \
   S1A_EW_OCN__2SDV_20230726T143837_20230726T143937_049595_05F6B7_015D.SAFE
```


From python:

```
import eofetch

eofetch.download([
    "S5P_OFFL_L2__CH4____20230501T010659_20230501T024829_28739_03_020500_20230502T170746.nc",
    "S5P_PAL__L2__NO2____20211114T004748_20211114T022918_21177_02_020301_20211215T133738.nc",
    "S1A_EW_OCN__2SDV_20230726T143837_20230726T143937_049595_05F6B7_015D.SAFE",
])
```


## CDSE access

Eofetch uses the S3 access service of CDSE to download data. This service
allows direct download of data without going through the zipper service and is
therefore the fastest means of downloading products.

For downloading data from the CDSE, you will need to have a registered account
on dataspace.copernicus.eu and contact CDSE support to request S3 credentials.
Details on this can be found in the
[CDSE documentation](https://documentation.dataspace.copernicus.eu/APIs/S3.html).

You will have to define environment variables `CDSE_S3_ACCESS` and
`CDSE_S3_SECRET` that contain the access key and secret key that you get from the
CDSE helpdesk.

You can set these environment variables within a linux shell using:

```
export CDSE_S3_ACCESS="XXXXXXXXXXXXXXXXXXXX"
export CDSE_S3_SECRET="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```
(replacing the XXX values with the credentials you got from the CDSE)

or from within python, using:

```
os.environ["CDSE_S3_ACCESS"] = "XXXXXXXXXXXXXXXXXXXX"
os.environ["CDSE_S3_SECRET"] = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

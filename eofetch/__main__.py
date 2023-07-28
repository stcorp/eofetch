import argparse
from .fetch import download

"""Download products from their respective archives.

For each filename provided as argument eofetch will try to retrieve it from the appropriate archive.
Each filename needs to be the filename of a product in the unzipped form.
For e.g. SAFE products you should pass the name of the top-level SAFE directory.

Depending on the archive where the products are hosted, you may need to set environment settings
with the credentials needed for downloading.
"""


def main():
    parser = argparse.ArgumentParser(prog="eofetch", description=__doc__)
    parser.add_argument("-o", "--output", metavar="OUTPUT_DIRECTORY",
                        help="output path where all products will be stored")
    parser.add_argument("products", nargs="+", metavar="<product>")
    args = parser.parse_args()
    for product in args.products:
        download(product, args.output)


main()

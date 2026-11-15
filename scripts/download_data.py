import urllib.request

from sfp.config import DATA_DIR, load_instruments

SOURCE = "https://raw.githubusercontent.com/robcarver17/pysystemtrade/master/data/futures"


# Download one file unless we already have it
def download(url, path):
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, path)
    print("downloaded", path.name)


# Download prices for every market plus the FX rates we need
def main():
    instruments = load_instruments()
    for code in instruments:
        download(f"{SOURCE}/adjusted_prices_csv/{code}.csv", DATA_DIR / "adjusted" / f"{code}.csv")
        download(f"{SOURCE}/multiple_prices_csv/{code}.csv", DATA_DIR / "multiple" / f"{code}.csv")

    currencies = {i.currency for i in instruments.values()} - {"USD"}
    for currency in currencies:
        download(f"{SOURCE}/fx_prices_csv/{currency}USD.csv", DATA_DIR / "fx" / f"{currency}USD.csv")


if __name__ == "__main__":
    main()

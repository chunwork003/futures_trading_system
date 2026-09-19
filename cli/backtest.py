import polars as pl

from cleaning.validator import MarketDataValidator


def validate_file(path: str):

    df = pl.read_parquet(path)

    validator = MarketDataValidator()

    result = validator.validate_bar(df)

    print("VALID:", result.valid)

    for error in result.errors:
        print("ERROR:", error)

    for warning in result.warnings:
        print("WARNING:", warning)


if __name__ == "__main__":
    import sys

    validate_file(sys.argv[1])
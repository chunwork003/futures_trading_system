from pathlib import Path

from ingestion.github_txf_stream import iter_txf_sql_batches


def main():
    path = Path(
        "data/raw/github/txf/data_TXFR1_2026.sql"
    )

    if not path.exists():
        raise FileNotFoundError(path)

    total = 0
    first_timestamp = None
    last_timestamp = None
    first_batch = None

    for batch in iter_txf_sql_batches(
        path,
        batch_size=100_000,
    ):
        total += batch.height

        if first_batch is None:
            first_batch = batch

        if batch.height > 0:
            if first_timestamp is None:
                first_timestamp = batch["timestamp"][0]

            last_timestamp = batch["timestamp"][-1]

    print(f"Total rows: {total:,}")
    print(f"First timestamp: {first_timestamp}")
    print(f"Last timestamp: {last_timestamp}")

    if first_batch is not None:
        print(f"Columns: {first_batch.columns}")
        print(f"Schema: {first_batch.schema}")


if __name__ == "__main__":
    main()

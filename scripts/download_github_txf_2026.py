from ingestion.github_downloader import GitHubRawDownloader


def main():
    downloader = GitHubRawDownloader()

    path = downloader.download(
        "data_TXFR1_2026.sql",
    )

    print(f"Downloaded: {path}")
    print(f"Size: {path.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()

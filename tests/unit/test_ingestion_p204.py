from pathlib import Path

from ingestion.github_downloader import GitHubRawDownloader


def test_build_url():
    downloader = GitHubRawDownloader()

    assert downloader.build_url(
        "data_TXFR1_2026.sql"
    ) == (
        "https://raw.githubusercontent.com/"
        "jason43314-crypto/"
        "taiwan-futures-1min-ohlc/"
        "main/"
        "data_TXFR1_2026.sql"
    )


def test_download_existing_file(tmp_path):
    downloader = GitHubRawDownloader(
        output_dir=tmp_path,
    )

    existing = tmp_path / "sample.sql"
    existing.write_text(
        "sample",
        encoding="utf-8",
    )

    result = downloader.download(
        "sample.sql",
    )

    assert result == existing
    assert result.read_text(
        encoding="utf-8"
    ) == "sample"

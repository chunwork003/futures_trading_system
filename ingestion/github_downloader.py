from pathlib import Path
from urllib.request import Request, urlopen


class GitHubRawDownloader:
    """Download raw files from a GitHub repository."""

    def __init__(
        self,
        repository: str = "jason43314-crypto/taiwan-futures-1min-ohlc",
        branch: str = "main",
        output_dir: str | Path = "data/raw/github/txf",
    ):
        self.repository = repository
        self.branch = branch
        self.output_dir = Path(output_dir)

    def build_url(self, filename: str) -> str:
        return (
            f"https://raw.githubusercontent.com/"
            f"{self.repository}/"
            f"{self.branch}/"
            f"{filename}"
        )

    def download(
        self,
        filename: str,
        overwrite: bool = False,
    ) -> Path:
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination = self.output_dir / filename

        if destination.exists() and not overwrite:
            return destination

        url = self.build_url(filename)

        request = Request(
            url,
            headers={
                "User-Agent": "futures-trading-system/1.0"
            },
        )

        with urlopen(request, timeout=120) as response:
            with destination.open("wb") as output:
                while True:
                    chunk = response.read(1024 * 1024)

                    if not chunk:
                        break

                    output.write(chunk)

        return destination

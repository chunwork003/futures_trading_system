from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GitHubTXFConfig:
    """Configuration for the public GitHub TXF historical dataset."""

    repository: str = "jason43314-crypto/taiwan-futures-1min-ohlc"
    branch: str = "main"
    file_prefix: str = "data_TXFR1_"
    local_raw_path: Path = Path("data/raw/github/txf")

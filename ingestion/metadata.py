from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass(frozen=True)
class SourceMetadata:
    """Provenance information attached to ingested market data."""

    source: str
    source_file: Optional[str] = None
    source_version: Optional[str] = None
    source_hash: Optional[str] = None
    ingested_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

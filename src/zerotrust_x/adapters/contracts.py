"""Vendor-neutral telemetry adapter contract."""
from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Protocol

from zerotrust_x.adapters.readers import read_csv, read_json
from zerotrust_x.models import RawEnvelope


class TelemetryAdapter(Protocol):
    source: str

    def read(self) -> Iterable[RawEnvelope]: ...


class CsvTelemetryAdapter:
    def __init__(self, path: Path, source: str, id_field: str):
        self.path, self.source, self.id_field = path, source, id_field

    def read(self) -> Iterable[RawEnvelope]:
        return read_csv(self.path, self.source, self.id_field)


class JsonTelemetryAdapter:
    def __init__(self, path: Path, source: str, id_field: str):
        self.path, self.source, self.id_field = path, source, id_field

    def read(self) -> Iterable[RawEnvelope]:
        return read_json(self.path, self.source, self.id_field)

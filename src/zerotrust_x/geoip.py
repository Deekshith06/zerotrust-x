"""GeoIP provider abstraction and provenance tracking.

Strict policy:
- Explicit telemetry fields (e.g. `geo_country`) are prioritized and authoritative.
- Geolocation is NEVER guessed or inferred from raw IP strings.
- Unresolved IPs are marked UNKNOWN / UNRESOLVED.
- If no external GeoIP provider is configured or available, the provider returns
  status="unavailable" with label "Geo enrichment unavailable" without blocking the SOC.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class GeoIPResolution:
    ip: str
    country: str | None
    country_code: str | None
    region: str | None = None
    city: str | None = None
    confidence: float | None = None
    source: str = "unresolved"
    lookup_timestamp: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )
    status: str = "unresolved"  # "resolved", "unresolved", "unavailable"
    provenance: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ip": self.ip,
            "country": self.country or "UNKNOWN / UNRESOLVED",
            "country_code": self.country_code or "UNRESOLVED",
            "region": self.region,
            "city": self.city,
            "confidence": self.confidence,
            "source": self.source,
            "lookup_timestamp": self.lookup_timestamp,
            "status": self.status,
            "provenance": self.provenance,
        }


class GeoIPProvider(ABC):
    """Abstract provider for IP-to-country resolution with provenance tracking."""

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def is_available(self) -> bool:
        ...

    @abstractmethod
    def resolve(self, ip: str, explicit_country: str | None = None) -> GeoIPResolution:
        """Resolve IP address with explicit provenance.

        Never guesses country. If unavailable or missing, returns unresolvable/unavailable status.
        """
        ...


class OfflineGeoIPProvider(GeoIPProvider):
    """Default zero-guess provider.

    Accepts explicit telemetry provenance when available from canonical records.
    When no explicit record exists, reports 'Geo enrichment unavailable' rather
    than fabricating a location from an IP string.
    """

    @property
    def name(self) -> str:
        return "offline-telemetry-strict"

    @property
    def is_available(self) -> bool:
        return False  # External GeoIP service is not wired locally

    def resolve(self, ip: str, explicit_country: str | None = None) -> GeoIPResolution:
        now = datetime.now(UTC).isoformat()
        if explicit_country and explicit_country.strip().upper() not in ("", "UNKNOWN", "UNRESOLVED", "NULL"):
            code = explicit_country.strip().upper()
            names = {
                "US": "United States",
                "IN": "India",
                "RU": "Russia",
                "CN": "China",
                "GB": "United Kingdom",
            }
            return GeoIPResolution(
                ip=ip,
                country=names.get(code, code),
                country_code=code,
                confidence=1.0,
                source="explicit telemetry field",
                lookup_timestamp=now,
                status="resolved",
                provenance={
                    "provider": self.name,
                    "evidence_type": "canonical_event_telemetry",
                    "policy": "explicit_record_only",
                    "inference_used": False,
                },
            )

        return GeoIPResolution(
            ip=ip,
            country="UNKNOWN / UNRESOLVED",
            country_code=None,
            confidence=None,
            source="none",
            lookup_timestamp=now,
            status="unavailable",
            provenance={
                "provider": self.name,
                "label": "Geo enrichment unavailable",
                "reason": "No external GeoIP provider configured. IP geolocation inference prohibited.",
                "inference_used": False,
            },
        )


_DEFAULT_PROVIDER: GeoIPProvider = OfflineGeoIPProvider()


def get_geoip_provider() -> GeoIPProvider:
    """Return active GeoIP provider instance."""
    return _DEFAULT_PROVIDER


def set_geoip_provider(provider: GeoIPProvider) -> None:
    """Override active GeoIP provider (for testing or external integrations)."""
    global _DEFAULT_PROVIDER
    _DEFAULT_PROVIDER = provider

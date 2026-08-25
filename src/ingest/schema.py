"""Esquema de datos para vehículos (Dataset Tidy)."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional

@dataclass(frozen=True, slots=True)
class VehicleListing:
    source: str
    source_listing_id: str
    make: str
    model: str
    version: Optional[str]
    year: int
    mileage: int
    price: float
    currency: str
    engine: Optional[str] = None
    power_hp: Optional[float] = None
    transmission: Optional[str] = None
    traction: Optional[str] = None
    fuel_type: Optional[str] = None
    consumption: Optional[str] = None
    location: Optional[str] = None
    url: Optional[str] = None
    collected_at: str = ""

    def __post_init__(self):
        if not self.collected_at:
            object.__setattr__(self, "collected_at", datetime.now(timezone.utc).isoformat())

    def to_row(self) -> dict:
        return asdict(self)
"""Dang ky connector — noi duy nhat biet co nhung connector nao."""
from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path

from vnir.connectors.base import BaseConnector

_REGISTRY: dict[str, type[BaseConnector]] = {}


def discover() -> dict[str, type[BaseConnector]]:
    """Tu dong tim moi lop ke thua BaseConnector trong package nay."""
    if _REGISTRY:
        return _REGISTRY
    pkg_dir = Path(__file__).resolve().parent
    for mod in pkgutil.iter_modules([str(pkg_dir)]):
        if mod.name in {"base", "registry", "__init__"}:
            continue
        try:
            m = importlib.import_module(f"vnir.connectors.{mod.name}")
        except Exception as exc:
            # Khong nuot loi im lang (P8: that bai phai on ao)
            import logging
            logging.getLogger("connector.registry").error(
                "Khong nap duoc connector %s: %s", mod.name, exc)
            continue
        for attr in vars(m).values():
            if (isinstance(attr, type) and issubclass(attr, BaseConnector)
                    and attr is not BaseConnector and getattr(attr, "source_id", "")):
                _REGISTRY[f"{attr.source_id}.{attr.dataset}"] = attr
    return _REGISTRY


def get(key: str) -> type[BaseConnector]:
    reg = discover()
    if key not in reg:
        raise KeyError(f"Khong co connector {key!r}. Co san: {sorted(reg)}")
    return reg[key]


def list_connectors() -> list[dict]:
    out = []
    for key, cls in sorted(discover().items()):
        out.append({
            "key": key, "source_id": cls.source_id, "dataset": cls.dataset,
            "title": cls.title, "homepage": cls.homepage, "schedule": cls.schedule,
            "legal_risk": cls.legal_risk, "requires_key": cls.requires_key,
            "freshness_sla_days": cls.freshness_sla_days,
            "description": cls.description, "class": cls.__name__,
        })
    return out

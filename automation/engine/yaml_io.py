"""Frozen automation contract 的安全 YAML read boundary。"""

from __future__ import annotations

from pathlib import Path
from typing import TypeVar, overload

import yaml

from automation.engine.contracts import (
    CONTRACT_BY_SCHEMA,
    AutomationContract,
)


class AutomationYamlError(ValueError):
    """YAML 無法安全解析、不是 mapping，或 schema 未受支援時的明確錯誤。"""


ContractT = TypeVar("ContractT", bound=AutomationContract)


def load_yaml_mapping(path: str | Path) -> dict[str, object]:
    """以 safe_load 讀取單一 mapping document；不寫檔、不改變任何 authority。"""

    source = Path(path)
    try:
        loaded = yaml.safe_load(source.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise AutomationYamlError(f"invalid safe YAML document: {source}") from exc
    if not isinstance(loaded, dict):
        raise AutomationYamlError("automation YAML top level must be a mapping")
    if any(not isinstance(key, str) for key in loaded):
        raise AutomationYamlError("automation YAML top-level keys must be strings")
    return loaded


@overload
def load_yaml_contract(path: str | Path, model: type[ContractT]) -> ContractT: ...


@overload
def load_yaml_contract(
    path: str | Path, model: None = None
) -> AutomationContract: ...


def load_yaml_contract(
    path: str | Path,
    model: type[ContractT] | None = None,
) -> ContractT | AutomationContract:
    """依 caller model 或 schema_version 建立 frozen contract；未知 schema fail closed。"""

    payload = load_yaml_mapping(path)
    selected: type[AutomationContract]
    if model is not None:
        selected = model
    else:
        schema_version = payload.get("schema_version")
        if not isinstance(schema_version, str):
            raise AutomationYamlError("automation YAML requires string schema_version")
        selected = CONTRACT_BY_SCHEMA.get(schema_version)  # type: ignore[assignment]
        if selected is None:
            raise AutomationYamlError(
                f"unsupported automation schema_version: {schema_version}"
            )
    return selected.model_validate(payload)


__all__ = ["AutomationYamlError", "load_yaml_contract", "load_yaml_mapping"]

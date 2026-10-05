"""Frozen automation contract 的安全 YAML read boundary。"""

from __future__ import annotations

from pathlib import Path
from typing import TypeVar, overload

import yaml
from yaml.constructor import ConstructorError
from yaml.nodes import MappingNode
from yaml.resolver import BaseResolver

from automation.engine.contracts import (
    CONTRACT_BY_SCHEMA,
    AutomationContract,
)


class AutomationYamlError(ValueError):
    """YAML 無法安全解析、不是 mapping，或 schema 未受支援時的明確錯誤。"""


ContractT = TypeVar("ContractT", bound=AutomationContract)


class _DuplicateMappingKeyError(ConstructorError):
    """標記 YAML mapping 內重複 key，讓公開 boundary 回傳一致錯誤。"""


class _UniqueKeySafeLoader(yaml.SafeLoader):
    """保留 SafeLoader 限制，並在每一層 mapping 拒絕重複 key。"""


def _construct_unique_mapping(
    loader: _UniqueKeySafeLoader,
    node: MappingNode,
    deep: bool = False,
) -> dict[object, object]:
    """在建構 mapping 前檢查原始 key；容器內的巢狀 mapping 也會經過此處。"""

    seen: set[object] = set()
    for key_node, _ in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in seen
            seen.add(key)
        except TypeError:
            # 非 hashable key 交由 SafeLoader 原有驗證處理，不改寫其安全語意。
            continue
        if duplicate:
            raise _DuplicateMappingKeyError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
    return yaml.SafeLoader.construct_mapping(loader, node, deep=deep)


_UniqueKeySafeLoader.add_constructor(
    BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def load_yaml_mapping(path: str | Path) -> dict[str, object]:
    """以 safe_load 讀取單一 mapping document；不寫檔、不改變任何 authority。"""

    source = Path(path)
    try:
        loaded = yaml.load(
            source.read_text(encoding="utf-8"),
            Loader=_UniqueKeySafeLoader,
        )
    except _DuplicateMappingKeyError as exc:
        raise AutomationYamlError(f"duplicate YAML mapping key: {source}") from exc
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

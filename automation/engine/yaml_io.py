"""Frozen automation contract 的安全 YAML read boundary。"""

from __future__ import annotations

from pathlib import Path
from typing import TypeVar, overload

import yaml
from yaml.constructor import ConstructorError
from yaml.nodes import MappingNode

from automation.engine.contracts import (
    CONTRACT_BY_SCHEMA,
    AutomationContract,
)


class AutomationYamlError(ValueError):
    """YAML 無法安全解析、不是 mapping，或 schema 未受支援時的明確錯誤。"""


ContractT = TypeVar("ContractT", bound=AutomationContract)


class _DuplicateMappingKeyError(ConstructorError):
    """標記 explicit YAML mapping key 重複，供公開 boundary 統一轉譯。"""


class _UniqueKeySafeLoader(yaml.SafeLoader):
    """在 SafeLoader mapping boundary 拒絕重複 explicit key。

    檢查發生於 merge flattening 前，因此合法 merge precedence、alias 與
    SafeLoader 的 generator placeholder 行為保持不變；此類別不增加 YAML 功能。
    """

    def construct_mapping(
        self,
        node: MappingNode,
        deep: bool = False,
    ) -> dict[object, object]:
        seen: set[object] = set()
        for key_node, _ in node.value:
            # Merge directive 由 SafeLoader flatten_mapping 處理；其來源 key
            # 碰撞屬合法 precedence，不是同一 mapping 的 explicit duplicate。
            if key_node.tag == "tag:yaml.org,2002:merge":
                continue
            key = self.construct_object(key_node, deep=deep)
            try:
                duplicate = key in seen
                seen.add(key)
            except TypeError:
                # 非 hashable key 仍交由 SafeLoader 原生驗證 fail closed。
                continue
            if duplicate:
                raise _DuplicateMappingKeyError(
                    "while constructing a mapping",
                    node.start_mark,
                    f"found duplicate key {key!r}",
                    key_node.start_mark,
                )
        return super().construct_mapping(node, deep=deep)


def load_yaml_mapping(path: str | Path) -> dict[str, object]:
    """以 safe_load 讀取單一 mapping document；不寫檔、不改變任何 authority。"""

    source = Path(path)
    return load_yaml_mapping_bytes(source.read_bytes(), source=str(source))


def load_yaml_mapping_bytes(data: bytes, *, source: str = "<Git blob>") -> dict[str, object]:
    """解析已驗證的 raw Git bytes；解碼失敗不回傳部分 document，沿用同一 SafeLoader。"""
    if type(data) is not bytes:
        raise AutomationYamlError("automation YAML input must be bytes")
    try:
        loaded = yaml.load(
            data.decode("utf-8"),
            Loader=_UniqueKeySafeLoader,
        )
    except UnicodeDecodeError as exc:
        raise AutomationYamlError(f"invalid UTF-8 YAML document: {source}") from exc
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


__all__ = ["AutomationYamlError", "load_yaml_contract", "load_yaml_mapping", "load_yaml_mapping_bytes"]

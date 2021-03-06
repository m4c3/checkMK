# Stubs for kubernetes.client.models.v1_label_selector_requirement (Python 2)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

from typing import Any, Optional

class V1LabelSelectorRequirement:
    swagger_types: Any = ...
    attribute_map: Any = ...
    discriminator: Any = ...
    key: Any = ...
    operator: Any = ...
    values: Any = ...
    def __init__(self, key: Optional[Any] = ..., operator: Optional[Any] = ..., values: Optional[Any] = ...) -> None: ...
    @property
    def key(self): ...
    @key.setter
    def key(self, key: Any) -> None: ...
    @property
    def operator(self): ...
    @operator.setter
    def operator(self, operator: Any) -> None: ...
    @property
    def values(self): ...
    @values.setter
    def values(self, values: Any) -> None: ...
    def to_dict(self): ...
    def to_str(self): ...
    def __eq__(self, other: Any): ...
    def __ne__(self, other: Any): ...

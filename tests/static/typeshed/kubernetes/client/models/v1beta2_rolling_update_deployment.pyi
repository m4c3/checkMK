# Stubs for kubernetes.client.models.v1beta2_rolling_update_deployment (Python 2)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

from typing import Any, Optional

class V1beta2RollingUpdateDeployment:
    swagger_types: Any = ...
    attribute_map: Any = ...
    discriminator: Any = ...
    max_surge: Any = ...
    max_unavailable: Any = ...
    def __init__(self, max_surge: Optional[Any] = ..., max_unavailable: Optional[Any] = ...) -> None: ...
    @property
    def max_surge(self): ...
    @max_surge.setter
    def max_surge(self, max_surge: Any) -> None: ...
    @property
    def max_unavailable(self): ...
    @max_unavailable.setter
    def max_unavailable(self, max_unavailable: Any) -> None: ...
    def to_dict(self): ...
    def to_str(self): ...
    def __eq__(self, other: Any): ...
    def __ne__(self, other: Any): ...

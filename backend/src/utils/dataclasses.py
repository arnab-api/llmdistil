from dataclasses import dataclass
from typing import Any, Optional, Union

from dataclasses_json import DataClassJsonMixin
from src.utils.typing import Layer


@dataclass(frozen=True)
class PredictedToken(DataClassJsonMixin):
    """A predicted token and its probability."""

    token: str
    prob: float

    def __str__(self) -> str:
        return f'"{self.token}" (p={self.prob:.3f})'

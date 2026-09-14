"""World state contract."""

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict


class WorldState(BaseModel):
    """Full environment state for one episode step."""

    model_config = ConfigDict(frozen=False)

    schema_version: str
    episode_id: str
    step: int
    session_id: str
    random_seed: int
    public: dict[str, Any]
    private: dict[str, Any]
    hidden: dict[str, Any]
    audit_log: list[dict[str, Any]]

    def model_copy_deep(self) -> "WorldState":
        """Return a deep copy of this state."""
        return self.model_copy(deep=True)

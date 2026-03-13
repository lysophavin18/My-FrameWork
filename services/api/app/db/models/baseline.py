from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.models._mixins import CreatedAtMixin, UUIDPrimaryKeyMixin


class DeltaBaseline(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    __tablename__ = "delta_baselines"

    root_domain: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)


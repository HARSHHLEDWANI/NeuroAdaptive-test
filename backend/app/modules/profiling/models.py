from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # ── Legacy archetype system (kept for backward compat) ───────────────────
    primary_archetype = Column(String, default="THE_PIONEER")
    visual_affinity = Column(Integer, default=0)
    textual_affinity = Column(Integer, default=0)
    depth_preference = Column(Integer, default=0)
    logic_preference = Column(Integer, default=0)
    total_engagement_time = Column(Integer, default=0)
    raw_scores = Column(JSON, default=dict)

    # ── FSLSM continuous vector system (Phase 1) ─────────────────────────────
    # Range: -1.0 to +1.0, default 0.0 (neutral)
    #
    # fslsm_processing:    -1.0 = Active  |  +1.0 = Reflective
    # fslsm_perception:    -1.0 = Sensing |  +1.0 = Intuitive
    # fslsm_reception:     -1.0 = Visual  |  +1.0 = Verbal
    # fslsm_understanding: -1.0 = Sequential | +1.0 = Global
    fslsm_processing    = Column(Float, default=0.0, nullable=False)
    fslsm_perception    = Column(Float, default=0.0, nullable=False)
    fslsm_reception     = Column(Float, default=0.0, nullable=False)
    fslsm_understanding = Column(Float, default=0.0, nullable=False)

    last_active = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user = relationship("User", back_populates="profile")

    @property
    def fslsm_vectors(self) -> dict:
        """Return FSLSM dimensions as a dict for use in adaptation engine."""
        return {
            "processing":    self.fslsm_processing,
            "perception":    self.fslsm_perception,
            "reception":     self.fslsm_reception,
            "understanding": self.fslsm_understanding,
        }

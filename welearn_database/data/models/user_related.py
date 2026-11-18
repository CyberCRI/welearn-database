from datetime import datetime
from uuid import UUID

from sqlalchemy import Computed, ForeignKey, Index, func, text, types
from sqlalchemy.dialects.postgresql import ENUM, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from welearn_database.data.enumeration import DbSchemaEnum, FilterType, QuestionType
from welearn_database.data.models.document_related import WeLearnDocument

from . import Base

schema_name = DbSchemaEnum.USER_RELATED.value


class UserProfile(Base):
    __tablename__ = "user_profile"
    __table_args__ = {"schema": DbSchemaEnum.USER_RELATED.value}

    id: Mapped[UUID] = mapped_column(
        types.Uuid, primary_key=True, nullable=False, server_default="gen_random_uuid()"
    )
    username: Mapped[str]
    email: Mapped[str]
    password_digest: Mapped[bytes]
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default=func.localtimestamp(),
        server_default="NOW()",
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default=func.localtimestamp(),
        server_default="NOW()",
        onupdate=func.localtimestamp(),
    )


class Bookmark(Base):
    __tablename__ = "bookmark"
    __table_args__ = {"schema": DbSchemaEnum.USER_RELATED.value}

    id: Mapped[UUID] = mapped_column(
        types.Uuid, primary_key=True, nullable=False, server_default="gen_random_uuid()"
    )
    document_id: Mapped[UUID] = mapped_column(
        types.Uuid,
        ForeignKey(
            f"{DbSchemaEnum.DOCUMENT_RELATED.value}.welearn_document.id",
            name="state_document_id_fkey",
        ),
        nullable=False,
    )
    inferred_user_id = mapped_column(
        types.Uuid,
        ForeignKey(
            f"{DbSchemaEnum.USER_RELATED.value}.inferred_user.id",
            name="bookmark_inferred_user_id_fkey",
        ),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default=func.localtimestamp(),
        server_default="NOW()",
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default=func.localtimestamp(),
        server_default="NOW()",
        onupdate=func.localtimestamp(),
    )
    inferred_user: Mapped["InferredUser"] = relationship()
    welearn_document: Mapped["WeLearnDocument"] = relationship()


class ChatMessage(Base):
    __tablename__ = "chat_message"
    __table_args__ = {"schema": DbSchemaEnum.USER_RELATED.value}

    id: Mapped[UUID] = mapped_column(
        types.Uuid, primary_key=True, nullable=False, server_default="gen_random_uuid()"
    )
    inferred_user_id = mapped_column(
        types.Uuid,
        ForeignKey(f"{DbSchemaEnum.USER_RELATED.value}.inferred_user.id"),
        nullable=False,
    )
    conversation_id = mapped_column(
        types.Uuid,
        nullable=False,
    )
    role: Mapped[str]
    textual_content: Mapped[str]
    is_retrieved_by_user: Mapped[bool] = mapped_column(
        default=False, server_default="False"
    )
    original_feature_name: Mapped[str | None]

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default=func.localtimestamp(),
        server_default="NOW()",
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default=func.localtimestamp(),
        server_default="NOW()",
        onupdate=func.localtimestamp(),
    )
    inferred_user: Mapped["InferredUser"] = relationship()


class ReturnedDocument(Base):
    __tablename__ = "returned_document"
    __table_args__ = {"schema": DbSchemaEnum.USER_RELATED.value}

    id: Mapped[UUID] = mapped_column(
        types.Uuid, primary_key=True, nullable=False, server_default="gen_random_uuid()"
    )
    message_id = mapped_column(
        types.Uuid,
        ForeignKey(f"{DbSchemaEnum.USER_RELATED.value}.chat_message.id"),
        nullable=False,
    )
    document_id: Mapped[UUID] = mapped_column(
        types.Uuid,
        ForeignKey(
            f"{DbSchemaEnum.DOCUMENT_RELATED.value}.welearn_document.id",
            name="state_document_id_fkey",
        ),
        nullable=False,
    )
    is_clicked: Mapped[bool] = mapped_column(default=False)

    welearn_document: Mapped["WeLearnDocument"] = relationship()
    chat_message: Mapped["ChatMessage"] = relationship()


class APIKeyManagement(Base):
    __tablename__ = "api_key_management"
    __table_args__ = {"schema": DbSchemaEnum.USER_RELATED.value}

    id: Mapped[UUID] = mapped_column(
        types.Uuid, primary_key=True, nullable=False, server_default="gen_random_uuid()"
    )
    title: Mapped[str | None]
    register_email: Mapped[str]
    digest: Mapped[bytes]
    is_active: Mapped[bool]
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default=func.localtimestamp(),
        server_default="NOW()",
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default=func.localtimestamp(),
        server_default="NOW()",
        onupdate=func.localtimestamp(),
    )


class DataCollectionCampaignManagement(Base):
    __tablename__ = "data_collection_campaign_management"
    __table_args__ = {"schema": DbSchemaEnum.USER_RELATED.value}

    id: Mapped[UUID] = mapped_column(
        types.Uuid, primary_key=True, nullable=False, server_default="gen_random_uuid()"
    )
    is_active: Mapped[bool]
    end_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default=func.localtimestamp(),
        server_default="NOW()",
    )


class Session(Base):
    __tablename__ = "session"
    __table_args__ = {"schema": "user_related"}
    id: Mapped[UUID] = mapped_column(
        types.Uuid, primary_key=True, nullable=False, server_default="gen_random_uuid()"
    )
    inferred_user_id: Mapped[UUID] = mapped_column(
        types.Uuid,
        ForeignKey("user_related.inferred_user.id"),
        nullable=False,
    )
    origin_referrer: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default=func.localtimestamp(),
        server_default="NOW()",
    )
    end_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=False), nullable=False)
    host: Mapped[str | None]
    user = relationship("InferredUser", foreign_keys=[inferred_user_id])


class InferredUser(Base):
    __tablename__ = "inferred_user"
    __table_args__ = {"schema": "user_related"}
    id: Mapped[UUID] = mapped_column(
        types.Uuid, primary_key=True, nullable=False, server_default="gen_random_uuid()"
    )
    keycloak_id: Mapped[UUID] = mapped_column(types.Uuid, nullable=True)
    origin_referrer: Mapped[str | None]
    university_title: Mapped[str | None]
    role: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default=func.localtimestamp(),
        server_default="NOW()",
    )


class EndpointRequest(Base):
    __tablename__ = "endpoint_request"
    __table_args__ = {"schema": "user_related"}
    id: Mapped[UUID] = mapped_column(
        types.Uuid, primary_key=True, nullable=False, server_default="gen_random_uuid()"
    )
    session_id: Mapped[UUID] = mapped_column(
        types.Uuid,
        ForeignKey("user_related.session.id"),
        nullable=False,
    )
    endpoint_name: Mapped[str]
    http_code: Mapped[int]
    message: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default=func.localtimestamp(),
        server_default="NOW()",
    )
    session = relationship("Session", foreign_keys=[session_id])


class FilterUsedInQuery(Base):
    __tablename__ = "filter_used_in_query"
    __table_args__ = {"schema": DbSchemaEnum.USER_RELATED.value}

    id: Mapped[UUID] = mapped_column(
        types.Uuid, primary_key=True, nullable=False, server_default="gen_random_uuid()"
    )
    message_id = mapped_column(
        types.Uuid,
        ForeignKey(f"{DbSchemaEnum.USER_RELATED.value}.chat_message.id"),
        nullable=False,
    )
    filter_type: Mapped[str] = mapped_column(
        ENUM(
            *(e.value.lower() for e in FilterType),
            name="filter_type",
            schema=DbSchemaEnum.USER_RELATED.value,
        ),
    )
    filter_value: Mapped[str]

    chat_message: Mapped["ChatMessage"] = relationship()


class AnalyticForm(Base):
    __tablename__ = "analytic_form"
    __table_args__ = {"schema": DbSchemaEnum.USER_RELATED.value}

    id: Mapped[UUID] = mapped_column(
        types.Uuid, primary_key=True, nullable=False, server_default="gen_random_uuid()"
    )
    form_name: Mapped[str] = mapped_column(nullable=False)
    question: Mapped[str] = mapped_column(nullable=False)
    answer: Mapped[str] = mapped_column(nullable=False)
    answer_type: Mapped[str] = mapped_column(
        ENUM(
            *(e.value.lower() for e in QuestionType),
            name="answer_type",
            schema=DbSchemaEnum.USER_RELATED.value,
        ),
        nullable=False,
    )
    session_id: Mapped[UUID] = mapped_column(
        types.Uuid,
        ForeignKey(f"{DbSchemaEnum.USER_RELATED.value}.session.id"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default=func.localtimestamp(),
        server_default="NOW()",
    )
    session = relationship("Session", foreign_keys=[session_id])


class Feature(Base):
    """
    A WeLearn feature a user can start runs of (chat, microlearning...). Rows are
    created by the migrations, and code finds a feature by its unique title.
    """

    __tablename__ = "feature"
    __table_args__ = {"schema": DbSchemaEnum.USER_RELATED.value}

    id: Mapped[UUID] = mapped_column(
        types.Uuid, primary_key=True, nullable=False, server_default="gen_random_uuid()"
    )
    title: Mapped[str] = mapped_column(nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default=func.localtimestamp(),
        server_default="NOW()",
    )


class Thread(Base):
    """
    One run of a feature by a user: a chat conversation, a microlearning... For a
    chat, the id is the agent's thread id. is_finished is computed by Postgres
    from current_step and max_step, so it can't be written; a thread without
    steps is never finished.
    """

    __tablename__ = "thread"
    __table_args__ = (
        Index(
            "thread_user_feature_updated_idx",
            "inferred_user_id",
            "feature_id",
            text("updated_at DESC"),
        ),
        {"schema": DbSchemaEnum.USER_RELATED.value},
    )

    id: Mapped[UUID] = mapped_column(
        types.Uuid, primary_key=True, nullable=False, server_default="gen_random_uuid()"
    )
    inferred_user_id: Mapped[UUID] = mapped_column(
        types.Uuid,
        ForeignKey(
            f"{DbSchemaEnum.USER_RELATED.value}.inferred_user.id",
            name="thread_inferred_user_id_fkey",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    feature_id: Mapped[UUID] = mapped_column(
        types.Uuid,
        ForeignKey(
            f"{DbSchemaEnum.USER_RELATED.value}.feature.id",
            name="thread_feature_id_fkey",
        ),
        nullable=False,
    )
    title: Mapped[str | None]
    current_step: Mapped[int | None]
    max_step: Mapped[int | None]
    is_finished: Mapped[bool] = mapped_column(
        Computed("COALESCE(current_step >= max_step, false)", persisted=True)
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default=func.localtimestamp(),
        server_default="NOW()",
    )

    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default=func.localtimestamp(),
        server_default="NOW()",
        onupdate=func.localtimestamp(),
    )
    inferred_user: Mapped["InferredUser"] = relationship()
    feature: Mapped["Feature"] = relationship()


class GuestFeatureUsage(Base):
    """
    One limited action of a guest within a feature: a chat question, a syllabus
    generated, feedback sent on it, course files read... The API counts a
    guest's rows of the last 24h for one (feature, action) against its daily
    quota, deletes the latest one to refund a failed use, and can purge older
    rows.
    """

    __tablename__ = "guest_feature_usage"
    __table_args__ = (
        Index(
            "guest_feature_usage_user_feature_action_created_idx",
            "inferred_user_id",
            "feature_id",
            "action",
            "created_at",
        ),
        {"schema": DbSchemaEnum.USER_RELATED.value},
    )

    id: Mapped[UUID] = mapped_column(
        types.Uuid, primary_key=True, nullable=False, server_default="gen_random_uuid()"
    )
    inferred_user_id: Mapped[UUID] = mapped_column(
        types.Uuid,
        ForeignKey(
            f"{DbSchemaEnum.USER_RELATED.value}.inferred_user.id",
            name="guest_feature_usage_inferred_user_id_fkey",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    feature_id: Mapped[UUID] = mapped_column(
        types.Uuid,
        ForeignKey(
            f"{DbSchemaEnum.USER_RELATED.value}.feature.id",
            name="guest_feature_usage_feature_id_fkey",
        ),
        nullable=False,
    )
    action: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default=func.localtimestamp(),
        server_default="NOW()",
    )
    inferred_user: Mapped["InferredUser"] = relationship()
    feature: Mapped["Feature"] = relationship()

import uuid
from datetime import datetime

from sqlalchemy import UUID
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from welearn_database.data.enumeration import DbSchemaEnum, Step
from welearn_database.data.models import Base

schema_name = DbSchemaEnum.GRAFANA.value


class ActiveUserDay(Base):
    __tablename__ = "active_user_day"
    __table_args__ = {"schema": schema_name}
    __read_only__ = True

    day: Mapped[datetime] = mapped_column(primary_key=True)
    inferred_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True
    )
    user_kind: Mapped[str] = mapped_column()
    requests: Mapped[int] = mapped_column()


class ActiveUsersDaily(Base):
    __tablename__ = "active_users_daily"
    __table_args__ = {"schema": schema_name}
    __read_only__ = True

    day: Mapped[datetime] = mapped_column(primary_key=True)
    user_kind: Mapped[str] = mapped_column(primary_key=True)
    active_users: Mapped[int] = mapped_column()
    requests: Mapped[int] = mapped_column()


class AuthEvent(Base):
    __tablename__ = "auth_event"
    __table_args__ = {"schema": schema_name}
    __read_only__ = True

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    inferred_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    event_type: Mapped[str] = mapped_column()
    identity_provider: Mapped[str | None] = mapped_column(nullable=True)
    is_limited_access: Mapped[bool] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()
    host: Mapped[str | None] = mapped_column(nullable=True)


class AuthEventDaily(Base):
    __tablename__ = "auth_event_daily"
    __table_args__ = {"schema": schema_name}
    __read_only__ = True

    # the view has no id: its grouping columns identify a row
    day: Mapped[datetime] = mapped_column(primary_key=True)
    event_type: Mapped[str] = mapped_column(primary_key=True)
    provider: Mapped[str] = mapped_column(primary_key=True)
    is_limited_access: Mapped[bool] = mapped_column(primary_key=True)
    identity_provider: Mapped[str | None] = mapped_column(nullable=True)
    events: Mapped[int] = mapped_column()
    users: Mapped[int] = mapped_column()


class Corpus(Base):
    __tablename__ = "corpus"
    __table_args__ = {"schema": schema_name}
    __read_only__ = True

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    parent_corpus_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True))
    source_name: Mapped[str]
    main_url: Mapped[str | None] = mapped_column(nullable=True)
    is_fix: Mapped[bool]
    is_active: Mapped[bool]
    category_id: Mapped[UUID | None] = mapped_column(UUID(as_uuid=True))


class DocumentLatestState(Base):
    __tablename__ = "document_latest_state"
    __table_args__ = {"schema": schema_name}
    __read_only__ = True

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    corpus_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    lang: Mapped[str | None] = mapped_column(nullable=True)
    title: Mapped[str] = mapped_column(
        ENUM(*(e.value.lower() for e in Step), name="step", schema="document_related"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column()
    operation_order: Mapped[int] = mapped_column()


class DocumentStateSummary(Base):
    __tablename__ = "document_state_summary"
    __table_args__ = {"schema": schema_name}
    __read_only__ = True

    source_name: Mapped[str] = mapped_column(primary_key=True)

    url_retrieved_count: Mapped[int] = mapped_column()
    document_scraped_count: Mapped[int] = mapped_column()
    document_is_irretrievable_count: Mapped[int] = mapped_column()
    document_vectorized_count: Mapped[int] = mapped_column()
    document_classified_sdg_count: Mapped[int] = mapped_column()
    document_classified_non_sdg_count: Mapped[int] = mapped_column()
    document_in_qdrant_count: Mapped[int] = mapped_column()
    kept_for_trace_count: Mapped[int] = mapped_column()
    no_state_count: Mapped[int] = mapped_column()
    total_documents: Mapped[int] = mapped_column()


class EndpointFeature(Base):
    __tablename__ = "endpoint_feature"
    __table_args__ = {"schema": schema_name}
    __read_only__ = True

    endpoint_pattern: Mapped[str] = mapped_column(primary_key=True)
    feature: Mapped[str] = mapped_column()


class EndpointRequest(Base):
    __tablename__ = "endpoint_request"
    __table_args__ = {"schema": schema_name}
    __read_only__ = True

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    endpoint_name: Mapped[str] = mapped_column()
    http_code: Mapped[int | None] = mapped_column(nullable=True)
    message: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column()


class FeatureRequest(Base):
    __tablename__ = "feature_request"
    __table_args__ = {"schema": schema_name}
    __read_only__ = True

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    inferred_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    user_kind: Mapped[str] = mapped_column()
    feature: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()


class FeatureUsageDaily(Base):
    __tablename__ = "feature_usage_daily"
    __table_args__ = {"schema": schema_name}
    __read_only__ = True

    day: Mapped[datetime] = mapped_column(primary_key=True)
    feature: Mapped[str] = mapped_column(primary_key=True)
    user_kind: Mapped[str] = mapped_column(primary_key=True)
    users: Mapped[int] = mapped_column()
    requests: Mapped[int] = mapped_column()


class GuestLimitHit(Base):
    __tablename__ = "guest_limit_hit"
    __table_args__ = {"schema": schema_name}
    __read_only__ = True

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    inferred_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    feature: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column()


class GuestLimitHitsDaily(Base):
    __tablename__ = "guest_limit_hits_daily"
    __table_args__ = {"schema": schema_name}
    __read_only__ = True

    day: Mapped[datetime] = mapped_column(primary_key=True)
    feature: Mapped[str] = mapped_column(primary_key=True)
    users: Mapped[int] = mapped_column()
    refusals: Mapped[int] = mapped_column()


class InferredUser(Base):
    __tablename__ = "inferred_user"
    __table_args__ = {"schema": schema_name}
    __read_only__ = True

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    created_at: Mapped[datetime] = mapped_column()


class NewUsersDaily(Base):
    __tablename__ = "new_users_daily"
    __table_args__ = {"schema": schema_name}
    __read_only__ = True

    day: Mapped[datetime] = mapped_column(primary_key=True)
    new_users: Mapped[int] = mapped_column()
    with_account: Mapped[int] = mapped_column()


class ProcessState(Base):
    __tablename__ = "process_state"
    __table_args__ = {"schema": schema_name}
    __read_only__ = True

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    title: Mapped[str] = mapped_column(
        ENUM(*(e.value.lower() for e in Step), name="step", schema="document_related"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column()
    operation_order: Mapped[int] = mapped_column()


class QtyEndpointsPerUser(Base):
    __tablename__ = "qty_endpoints_per_user"
    __table_args__ = {"schema": schema_name}
    __read_only__ = True

    count: Mapped[int] = mapped_column(primary_key=True)


class QtySessionEndpointPerUser(Base):
    __tablename__ = "qty_session_endpoint_per_user"
    __table_args__ = {"schema": schema_name}
    __read_only__ = True

    inferred_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True
    )
    host: Mapped[str] = mapped_column(primary_key=True)
    count_sessions: Mapped[int] = mapped_column()
    count_endpoints: Mapped[int] = mapped_column()


class QtySessionUserPerHost(Base):
    __tablename__ = "qty_session_user_per_host"
    __table_args__ = {"schema": schema_name}
    __read_only__ = True

    host: Mapped[str] = mapped_column(primary_key=True)
    count_sessions: Mapped[int] = mapped_column()
    count_users: Mapped[int] = mapped_column()


class Session(Base):
    __tablename__ = "session"
    __table_args__ = {"schema": schema_name}
    __read_only__ = True

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    inferred_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column()
    end_at: Mapped[datetime | None] = mapped_column(nullable=True)
    host: Mapped[str | None] = mapped_column(nullable=True)


class UsedFeaturePerSession(Base):
    __tablename__ = "used_feature_per_session"
    __table_args__ = {"schema": schema_name}
    __read_only__ = True

    inferred_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True
    )
    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    feature_name: Mapped[str] = mapped_column(primary_key=True)
    cnt: Mapped[int] = mapped_column()
    is_feature_used: Mapped[bool] = mapped_column()
    session_created_at: Mapped[datetime] = mapped_column()

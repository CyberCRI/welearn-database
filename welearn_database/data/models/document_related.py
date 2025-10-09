from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import types, ForeignKey, UniqueConstraint, func, LargeBinary
from sqlalchemy.dialects.postgresql import TIMESTAMP, ENUM
from sqlalchemy.orm import mapped_column, Mapped, relationship

from . import Base
from welearn_database.data.enumeration import DbSchemaEnum, Step, Counter
from welearn_database.data.models.corpus_related import Corpus, NClassifierModel, BiClassifierModel, EmbeddingModel

schema_name = DbSchemaEnum.DOCUMENT_RELATED.value


class WeLearnDocument(Base):
    __tablename__ = "welearn_document"
    __table_args__ = (
        UniqueConstraint("url", name="welearn_document_url_key"),
        {"schema": schema_name},
    )

    id: Mapped[UUID] = mapped_column(
        types.Uuid, primary_key=True, nullable=False, server_default="gen_random_uuid()"
    )
    url: Mapped[str] = mapped_column(nullable=False)
    title: Mapped[str | None]
    lang: Mapped[str | None]
    description: Mapped[str | None]
    full_content: Mapped[str | None]
    details: Mapped[dict[str, Any] | None]
    trace: Mapped[int | None] = mapped_column(types.BIGINT)
    corpus_id: Mapped[UUID] = mapped_column(
        types.Uuid,
        ForeignKey(f"{DbSchemaEnum.CORPUS_RELATED.value}.corpus.id"),
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

    corpus: Mapped["Corpus"] = relationship("Corpus")


class ProcessState(Base):
    __tablename__ = "process_state"
    __table_args__ = {"schema": DbSchemaEnum.DOCUMENT_RELATED.value}

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
    title: Mapped[str] = mapped_column(
        ENUM(*(e.value.lower() for e in Step), name="step", schema="document_related"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default=func.localtimestamp(),
        server_default="NOW()",
    )
    operation_order = mapped_column(
        types.BIGINT,
        server_default="nextval('document_related.process_state_operation_order_seq'",
        nullable=False,
    )
    document: Mapped["WeLearnDocument"] = relationship()


class Keyword(Base):
    __tablename__ = "keyword"
    __table_args__ = (
        UniqueConstraint("keyword", name="keyword_unique"),
        {"schema": DbSchemaEnum.DOCUMENT_RELATED.value},
    )

    id: Mapped[UUID] = mapped_column(
        types.Uuid, primary_key=True, nullable=False, server_default="gen_random_uuid()"
    )
    keyword: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default=func.localtimestamp(),
        server_default="NOW()",
    )


class WeLearnDocumentKeyword(Base):
    __tablename__ = "welearn_document_keyword"
    __table_args__ = (
        UniqueConstraint(
            "welearn_document_id",
            "keyword_id",
            name="unique_welearn_document_keyword_association",
        ),
        {"schema": DbSchemaEnum.DOCUMENT_RELATED.value},
    )
    id: Mapped[UUID] = mapped_column(
        types.Uuid, primary_key=True, nullable=False, server_default="gen_random_uuid()"
    )
    welearn_document_id: Mapped[UUID] = mapped_column(
        types.Uuid,
        ForeignKey(
            f"{DbSchemaEnum.DOCUMENT_RELATED.value}.welearn_document.id",
            name="state_document_id_fkey",
        ),
        nullable=False,
    )
    keyword_id: Mapped[UUID] = mapped_column(
        types.Uuid,
        ForeignKey(f"{DbSchemaEnum.DOCUMENT_RELATED.value}.keyword.id"),
        nullable=False,
    )


class ErrorRetrieval(Base):
    __tablename__ = "error_retrieval"
    __table_args__ = ({"schema": DbSchemaEnum.DOCUMENT_RELATED.value},)

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
    http_error_code: Mapped[int | None]
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
    error_info: Mapped[str]

    document: Mapped["WeLearnDocument"] = relationship()


class DocumentSlice(Base):
    __tablename__ = "document_slice"
    __table_args__ = {"schema": DbSchemaEnum.DOCUMENT_RELATED.value}

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
    embedding: Mapped[bytes | None] = mapped_column(LargeBinary)
    body: Mapped[str | None]
    order_sequence: Mapped[int]
    embedding_model_name: Mapped[str]

    embedding_model_id = mapped_column(
        types.Uuid,
        ForeignKey(f"{DbSchemaEnum.CORPUS_RELATED.value}.embedding_model.id"),
        nullable=False,
    )

    document: Mapped["WeLearnDocument"] = relationship()
    embedding_model: Mapped["EmbeddingModel"] = relationship()


class AnalyticCounter(Base):
    __tablename__ = "analytic_counter"
    __table_args__ = {
        "schema": DbSchemaEnum.DOCUMENT_RELATED.value,
    }

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
    counter_name: Mapped[Counter]
    counter_value: Mapped[int]
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
    document: Mapped["WeLearnDocument"] = relationship()



class CorpusEmbeddingModel(Base):
    __tablename__ = "corpus_embedding_model"
    __table_args__ = (
        UniqueConstraint(
            "corpus_id",
            "embedding_model_id",
            name="unique_corpus_embedding_association",
        ),
        {"schema": DbSchemaEnum.CORPUS_RELATED.value},
    )

    corpus_id = mapped_column(
        types.Uuid,
        ForeignKey(f"{DbSchemaEnum.CORPUS_RELATED.value}.corpus.id"),
        primary_key=True,
    )
    embedding_model_id = mapped_column(
        types.Uuid,
        ForeignKey(f"{DbSchemaEnum.CORPUS_RELATED.value}.embedding_model.id"),
        primary_key=True,
    )

    used_since: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default=func.localtimestamp(),
        server_default="NOW()",
    )

    embedding_model: Mapped["EmbeddingModel"] = relationship()
    corpus: Mapped["Corpus"] = relationship()


class CorpusNClassifierModel(Base):
    __tablename__ = "corpus_n_classifier_model"
    __table_args__ = (
        UniqueConstraint(
            "corpus_id",
            "n_classifier_model_id",
            name="unique_corpus_n_classifier_association",
        ),
        {"schema": DbSchemaEnum.CORPUS_RELATED.value},
    )

    corpus_id = mapped_column(
        types.Uuid,
        ForeignKey(f"{DbSchemaEnum.CORPUS_RELATED.value}.corpus.id"),
        primary_key=True,
    )
    n_classifier_model_id = mapped_column(
        types.Uuid,
        ForeignKey(f"{DbSchemaEnum.CORPUS_RELATED.value}.n_classifier_model.id"),
        primary_key=True,
    )

    used_since: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default=func.localtimestamp(),
        server_default="NOW()",
    )

    n_classifier_model: Mapped["NClassifierModel"] = relationship()
    corpus: Mapped["Corpus"] = relationship()


class CorpusBiClassifierModel(Base):
    __tablename__ = "corpus_bi_classifier_model"
    __table_args__ = (
        UniqueConstraint(
            "corpus_id",
            "bi_classifier_model_id",
            name="unique_corpus_bi_classifier_association",
        ),
        {"schema": DbSchemaEnum.CORPUS_RELATED.value},
    )

    corpus_id = mapped_column(
        types.Uuid,
        ForeignKey(f"{DbSchemaEnum.CORPUS_RELATED.value}.corpus.id"),
        primary_key=True,
    )
    bi_classifier_model_id = mapped_column(
        types.Uuid,
        ForeignKey(f"{DbSchemaEnum.CORPUS_RELATED.value}.bi_classifier_model.id"),
        primary_key=True,
    )
    used_since: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default=func.localtimestamp(),
        server_default="NOW()",
    )

    bi_classifier_model: Mapped["BiClassifierModel"] = relationship()
    corpus: Mapped["Corpus"] = relationship()


class Sdg(Base):
    __tablename__ = "sdg"
    __table_args__ = {"schema": DbSchemaEnum.DOCUMENT_RELATED.value}

    id: Mapped[UUID] = mapped_column(
        types.Uuid,
        primary_key=True,
        nullable=False,
        server_default="gen_random_uuid()",
    )
    slice_id = mapped_column(
        types.Uuid,
        ForeignKey(
            f"{DbSchemaEnum.DOCUMENT_RELATED.value}.document_slice.id",
            name="sdg_slice_id_fkey2",
        ),
        nullable=False,
    )
    sdg_number: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        nullable=False,
        default=func.localtimestamp(),
        server_default="NOW()",
    )

    bi_classifier_model_id = mapped_column(
        types.Uuid,
        ForeignKey(f"{DbSchemaEnum.CORPUS_RELATED.value}.bi_classifier_model.id"),
    )
    n_classifier_model_id = mapped_column(
        types.Uuid,
        ForeignKey(f"{DbSchemaEnum.CORPUS_RELATED.value}.n_classifier_model.id"),
    )
    bi_classifier_model: Mapped["BiClassifierModel"] = relationship()
    n_classifier_model: Mapped["NClassifierModel"] = relationship()
    slice: Mapped["DocumentSlice"] = relationship()
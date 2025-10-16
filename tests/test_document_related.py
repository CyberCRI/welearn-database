import uuid
from unittest import TestCase
from zlib import adler32

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from tests.helpers import handle_schema_with_sqlite
from welearn_database.data.enumeration import Step
from welearn_database.data.models import Base, QtyDocumentInQdrant
from welearn_database.data.models.corpus_related import Category, Corpus
from welearn_database.data.models.document_related import ProcessState, WeLearnDocument
from welearn_database.exceptions import InvalidURLScheme


class TestWeLearnDocument(TestCase):
    def test_validate_url(self):
        test_doc = WeLearnDocument(
            title="Test Document",
            url="https://example.com/test-document",
            full_content="This is a test document, used for unit testing, please ignore. Thank you!",
            description="A short description of the test document.",
            lang="en",
            corpus="Test Corpus",
            details={"author": "Test Author"},
        )

        self.assertEqual(test_doc.url, "https://example.com/test-document")

    def test_validate_wrong_scheme_url(self):
        with self.assertRaises(InvalidURLScheme):
            WeLearnDocument(
                title="Test Document",
                url="http://example.com/test-document",
                full_content="This is a test document, used for unit testing, please ignore. Thank you!",
                description="A short description of the test document.",
                lang="en",
                corpus="Test Corpus",
                details={"author": "Test Author"},
            )

    def test_validate_wrong_url(self):
        with self.assertRaises(InvalidURLScheme):
            WeLearnDocument(
                title="Test Document",
                url="john.doe@example.org",
                full_content="This is a test document, used for unit testing, please ignore. Thank you!",
                description="A short description of the test document.",
                lang="en",
                corpus="Test Corpus",
                details={"author": "Test Author"},
            )

    def test_validate_full_content(self):
        test_doc = WeLearnDocument(
            title="Test Document",
            url="https://example.com/test-document",
            full_content="This is a test document, used for unit testing, please ignore. Thank you!",
            description="A short description of the test document.",
            lang="en",
            corpus="Test Corpus",
            details={"author": "Test Author"},
        )

        self.assertEqual(
            test_doc.full_content,
            "This is a test document, used for unit testing, please ignore. Thank you!",
        )

    def test_validate_too_short_full_content(self):
        with self.assertRaises(ValueError):
            WeLearnDocument(
                title="Test Document",
                url="https://example.com/test-document",
                full_content="Too short",
                description="A short description of the test document.",
                lang="en",
                corpus="Test Corpus",
                details={"author": "Test Author"},
            )

    def test_full_content(self):
        test_doc = WeLearnDocument(
            title="Test Document",
            url="https://example.com/test-document",
            full_content="<p>This is a test document, used for unit testing, please ignore. Thank you!</p>",
            description="A short description of the test document.",
            lang="en",
            corpus="Test Corpus",
            details={"author": "Test Author"},
        )

        self.assertEqual(
            test_doc.full_content,
            "This is a test document, used for unit testing, please ignore. Thank you!",
        )

    def test_description(self):
        test_doc = WeLearnDocument(
            title="Test Document",
            url="https://example.com/test-document",
            full_content="This is a test document, used for unit testing, please ignore. Thank you!",
            description="<p>A short description &nbsp of the   test document.</p>",
            lang="en",
            corpus="Test Corpus",
            details={"author": "Test Author"},
        )

        self.assertEqual(
            test_doc.description, "A short description of the test document."
        )

    def test_trace(self):
        content = (
            "This is a test document, used for unit testing, please ignore. Thank you!"
        )
        expected_trace = adler32(bytes(content, "utf-8"))
        test_doc = WeLearnDocument(
            title="Test Document",
            url="https://example.com/test-document",
            full_content="This is a test document, used for unit testing, please ignore. Thank you!",
            description="A short description of the test document.",
            lang="en",
            corpus="Test Corpus",
            details={"author": "Test Author"},
        )

        self.assertEqual(test_doc.trace, expected_trace)

    def test_trace_in_db(self):
        engine = create_engine("sqlite://")
        s_maker = sessionmaker(engine)
        handle_schema_with_sqlite(engine)

        test_session = s_maker()
        Base.metadata.create_all(test_session.get_bind())

        content = (
            "This is a test document, used for unit testing, please ignore. Thank you!"
        )
        expected_trace = adler32(bytes(content, "utf-8"))
        corpus_id = uuid.uuid4()
        test_category = Category(
            id=uuid.uuid4(),
            title="Test Category",
        )
        test_session.add(test_category)
        test_session.commit()
        test_corpus = Corpus(
            id=corpus_id,
            source_name="Test Corpus",
            is_fix=True,
            is_active=True,
            binary_treshold=0.5,
            category_id=test_category.id,
        )
        test_session.add(test_corpus)
        test_session.commit()

        test_doc = WeLearnDocument(
            id=uuid.uuid4(),
            title="Test Document",
            url="https://example.com/test-document",
            full_content=content,
            description="A short description of the test document.",
            lang="en",
            corpus_id=test_corpus.id,
            details={"author": "Test Author"},
        )
        test_session.add(test_doc)
        test_session.commit()

        doc_from_db = (
            test_session.query(WeLearnDocument)
            .filter(WeLearnDocument.id == test_doc.id)
            .first()
        )
        self.assertIsNotNone(doc_from_db)
        self.assertEqual(doc_from_db.trace, expected_trace)

    def test_none_trace_in_db(self):
        engine = create_engine("sqlite://")
        s_maker = sessionmaker(engine)
        handle_schema_with_sqlite(engine)

        test_session = s_maker()
        Base.metadata.create_all(test_session.get_bind())

        corpus_id = uuid.uuid4()
        test_category = Category(
            id=uuid.uuid4(),
            title="Test Category",
        )
        test_session.add(test_category)
        test_session.commit()
        test_corpus = Corpus(
            id=corpus_id,
            source_name="Test Corpus",
            is_fix=True,
            is_active=True,
            binary_treshold=0.5,
            category_id=test_category.id,
        )
        test_session.add(test_corpus)
        test_session.commit()

        test_doc = WeLearnDocument(
            id=uuid.uuid4(),
            title="Test Document",
            url="https://example.com/test-document",
            full_content=None,
            description="A short description of the test document.",
            lang="en",
            corpus_id=test_corpus.id,
            details={"author": "Test Author"},
        )
        test_session.add(test_doc)
        test_session.commit()

        doc_from_db = (
            test_session.query(WeLearnDocument)
            .filter(WeLearnDocument.id == test_doc.id)
            .first()
        )
        self.assertIsNotNone(doc_from_db)
        self.assertEqual(doc_from_db.trace, None)

    def test_view_qty_document(self):
        engine = create_engine("sqlite://")
        s_maker = sessionmaker(engine)
        handle_schema_with_sqlite(engine)

        test_session = s_maker()
        Base.metadata.create_all(test_session.get_bind())

        corpus_id = uuid.uuid4()
        test_category = Category(
            id=uuid.uuid4(),
            title="Test Category",
        )
        test_session.add(test_category)
        test_session.commit()
        test_corpus = Corpus(
            id=corpus_id,
            source_name="Test Corpus",
            is_fix=True,
            is_active=True,
            binary_treshold=0.5,
            category_id=test_category.id,
        )
        test_session.add(test_corpus)
        test_session.commit()

        for i in range(5):
            test_doc = WeLearnDocument(
                id=uuid.uuid4(),
                title=f"Test Document {i}",
                url=f"https://example.com/test-document-{i}",
                full_content="This is a test document, used for unit testing, please ignore. Thank you!",
                description="A short description of the test document.",
                lang="en",
                corpus_id=test_corpus.id,
                details={"author": "Test Author"},
            )
            test_session.add(test_doc)
            test_process_state = ProcessState(
                id=uuid.uuid4(),
                document_id=test_doc.id,
                title=Step.DOCUMENT_IN_QDRANT.value.lower(),
            )
            test_session.add(test_process_state)
            test_session.commit()

        test_session.execute(text("DROP TABLE IF EXISTS qty_document_in_qdrant"))
        test_session.commit()

        test_session.execute(
            text(
                """
            CREATE VIEW document_related.qty_document_in_qdrant AS
            SELECT COUNT(1) AS document_in_qdrant
            FROM (
                SELECT document_id, MAX(operation_order) AS max_order
                FROM document_related.process_state
                WHERE title = 'document_in_qdrant'
                GROUP BY document_id
            ) latest;
        """
            )
        )
        test_session.commit()

        result = test_session.query(QtyDocumentInQdrant).first()
        self.assertIsNotNone(result)
        self.assertEqual(result.document_in_qdrant, 5)

        with self.assertRaises(ValueError):
            result.document_in_qdrant = 10

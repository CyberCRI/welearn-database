from unittest import TestCase

from welearn_database.data.models.document_related import WeLearnDocument
from welearn_database.exceptions import InvalidURLScheme


class TestWeLearnDocument(TestCase):
    def setUp(self):
        pass
        # self.engine = create_engine("sqlite://")
        # s_maker = sessionmaker(self.engine)
        # handle_schema_with_sqlite(self.engine)
        # self.test_session = s_maker()
        # Base.metadata.create_all(self.test_session.get_bind())

    def test_validate_url(self):
        test_doc = WeLearnDocument(
            title="Test Document",
            url="https://example.com/test-document",
            full_content="This is a test document, used for unit testing, please ignore. Thank you!",
            description="A short description of the test document.",
            lang="en",
            corpus="Test Corpus",
            details={"author": "Test Author"}
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
                details={"author": "Test Author"}
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
                details={"author": "Test Author"}
            )

    def test_validate_full_content(self):
        test_doc = WeLearnDocument(
            title="Test Document",
            url="https://example.com/test-document",
            full_content="This is a test document, used for unit testing, please ignore. Thank you!",
            description="A short description of the test document.",
            lang="en",
            corpus="Test Corpus",
            details={"author": "Test Author"}
        )

        self.assertEqual(test_doc.full_content, "This is a test document, used for unit testing, please ignore. Thank you!")

    def test_validate_too_short_full_content(self):
        with self.assertRaises(ValueError):
            WeLearnDocument(
                title="Test Document",
                url="https://example.com/test-document",
                full_content="Too short",
                description="A short description of the test document.",
                lang="en",
                corpus="Test Corpus",
                details={"author": "Test Author"}
            )

    def test_validate_no_full_content(self):
        with self.assertRaises(ValueError):
            WeLearnDocument(
                title="Test Document",
                url="https://example.com/test-document",
                full_content=None,
                description="A short description of the test document.",
                lang="en",
                corpus="Test Corpus",
                details={"author": "Test Author"}
            )


    def test_full_content(self):
        test_doc = WeLearnDocument(
            title="Test Document",
            url="https://example.com/test-document",
            full_content="<p>This is a test document, used for unit testing, please ignore. Thank you!</p>",
            description="A short description of the test document.",
            lang="en",
            corpus="Test Corpus",
            details={"author": "Test Author"}
        )

        self.assertEqual(test_doc.full_content, "This is a test document, used for unit testing, please ignore. Thank you!")

    def test_description(self):
        test_doc = WeLearnDocument(
            title="Test Document",
            url="https://example.com/test-document",
            full_content="This is a test document, used for unit testing, please ignore. Thank you!",
            description="<p>A short description &nbsp of the   test document.</p>",
            lang="en",
            corpus="Test Corpus",
            details={"author": "Test Author"}
        )

        self.assertEqual(test_doc.description,
                         "A short description of the test document.")

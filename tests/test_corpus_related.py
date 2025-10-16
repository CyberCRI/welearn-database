import uuid
from unittest import TestCase

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tests.helpers import handle_schema_with_sqlite
from welearn_database.data.models import Base
from welearn_database.data.models.corpus_related import (
    BiClassifierModel,
    Category,
    Corpus,
    EmbeddingModel,
    NClassifierModel,
)


class TestDatabaseCRUD(TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")
        handle_schema_with_sqlite(self.engine)

        self.s_maker = sessionmaker(self.engine)
        Base.metadata.create_all(self.engine)
        self.session = self.s_maker()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_creates_and_reads_corpus(self):
        category = Category(id=uuid.uuid4(), title="Category Test")
        self.session.add(category)
        self.session.commit()
        corpus = Corpus(
            id=uuid.uuid4(),
            source_name="Corpus Test",
            is_fix=True,
            is_active=True,
            binary_treshold=0.7,
            category_id=category.id,
        )
        self.session.add(corpus)
        self.session.commit()
        result = self.session.query(Corpus).filter_by(source_name="Corpus Test").first()
        self.assertIsNotNone(result)
        self.assertEqual(float(result.binary_treshold), 0.7)

    def test_updates_corpus_binary_treshold(self):
        category = Category(id=uuid.uuid4(), title="Category Test")
        self.session.add(category)
        self.session.commit()
        corpus = Corpus(
            id=uuid.uuid4(),
            source_name="Corpus Test",
            is_fix=True,
            is_active=True,
            binary_treshold=0.7,
            category_id=category.id,
        )
        self.session.add(corpus)
        self.session.commit()
        corpus.binary_treshold = 0.9
        self.session.commit()
        updated_corpus = (
            self.session.query(Corpus).filter_by(source_name="Corpus Test").first()
        )
        self.assertIsNotNone(updated_corpus)
        self.assertEqual(float(updated_corpus.binary_treshold), 0.9)

    def test_deletes_corpus(self):
        category = Category(id=uuid.uuid4(), title="Category Test")
        self.session.add(category)
        self.session.commit()
        corpus = Corpus(
            id=uuid.uuid4(),
            source_name="Corpus Test",
            is_fix=True,
            is_active=True,
            binary_treshold=0.7,
            category_id=category.id,
        )
        self.session.add(corpus)
        self.session.commit()
        self.session.delete(corpus)
        self.session.commit()
        result = self.session.query(Corpus).filter_by(source_name="Corpus Test").first()
        self.assertIsNone(result)

    def test_creates_and_reads_embedding_model(self):
        embedding_model = EmbeddingModel(
            id=uuid.uuid4(),
            title="Embedding Model Test",
            lang="en",
        )
        self.session.add(embedding_model)
        self.session.commit()
        result = (
            self.session.query(EmbeddingModel)
            .filter_by(title="Embedding Model Test")
            .first()
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.lang, "en")

    def test_creates_and_reads_bi_classifier_model(self):
        bi_classifier = BiClassifierModel(
            id=uuid.uuid4(),
            title="BiClassifier Test",
            binary_treshold=0.8,
            lang="fr",
        )
        self.session.add(bi_classifier)
        self.session.commit()
        result = (
            self.session.query(BiClassifierModel)
            .filter_by(title="BiClassifier Test")
            .first()
        )
        self.assertIsNotNone(result)
        self.assertEqual(float(result.binary_treshold), 0.8)

    def test_creates_and_reads_n_classifier_model(self):
        n_classifier = NClassifierModel(
            id=uuid.uuid4(),
            title="NClassifier Test",
            lang="es",
            treshold_sdg_1=0.6,
            treshold_sdg_2=0.7,
        )
        self.session.add(n_classifier)
        self.session.commit()
        result = (
            self.session.query(NClassifierModel)
            .filter_by(title="NClassifier Test")
            .first()
        )
        self.assertIsNotNone(result)
        self.assertEqual(float(result.treshold_sdg_1), 0.6)
        self.assertEqual(float(result.treshold_sdg_2), 0.7)

import uuid
from unittest import TestCase

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tests.helpers import handle_schema_with_sqlite
from welearn_database.data.models import Base, InferredUser
from welearn_database.data.models.corpus_related import Category, Corpus
from welearn_database.data.models.document_related import WeLearnDocument
from welearn_database.data.models.user_related import Bookmark, UserProfile


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

    def test_create_and_read_category(self):
        category = Category(id=uuid.uuid4(), title="Catégorie Test")
        self.session.add(category)
        self.session.commit()
        result = self.session.query(Category).filter_by(title="Catégorie Test").first()
        self.assertIsNotNone(result)
        self.assertEqual(result.title, "Catégorie Test")

    def test_update_category(self):
        category = Category(id=uuid.uuid4(), title="Ancien Titre")
        self.session.add(category)
        self.session.commit()
        category.title = "Nouveau Titre"
        self.session.commit()
        result = self.session.query(Category).filter_by(title="Nouveau Titre").first()
        self.assertIsNotNone(result)
        self.assertEqual(result.title, "Nouveau Titre")

    def test_delete_category(self):
        category = Category(id=uuid.uuid4(), title="À Supprimer")
        self.session.add(category)
        self.session.commit()
        self.session.delete(category)
        self.session.commit()
        result = self.session.query(Category).filter_by(title="À Supprimer").first()
        self.assertIsNone(result)

    def test_crud_user_profile(self):
        user = UserProfile(
            id=uuid.uuid4(),
            username="testuser",
            email="test@example.com",
            password_digest=b"secret",
        )
        self.session.add(user)
        self.session.commit()
        user_from_db = (
            self.session.query(UserProfile).filter_by(username="testuser").first()
        )
        self.assertIsNotNone(user_from_db)
        self.assertEqual(user_from_db.email, "test@example.com")
        user_from_db.email = "new@example.com"
        self.session.commit()
        updated_user = (
            self.session.query(UserProfile).filter_by(email="new@example.com").first()
        )
        self.assertIsNotNone(updated_user)
        self.session.delete(updated_user)
        self.session.commit()
        deleted_user = (
            self.session.query(UserProfile).filter_by(username="testuser").first()
        )
        self.assertIsNone(deleted_user)

    def test_crud_document_and_bookmark(self):
        category = Category(id=uuid.uuid4(), title="Catégorie")
        self.session.add(category)
        self.session.commit()
        corpus = Corpus(
            id=uuid.uuid4(),
            source_name="Corpus Test",
            is_fix=True,
            is_active=True,
            binary_treshold=0.5,
            category_id=category.id,
        )
        self.session.add(corpus)
        self.session.commit()
        doc = WeLearnDocument(
            id=uuid.uuid4(),
            title="Document Test",
            url="https://exemple.com/doc",
            full_content="Contenu de test pour le document, assez long pour valider.",
            description="Description test",
            lang="fr",
            corpus_id=corpus.id,
            details={"auteur": "Testeur"},
        )
        self.session.add(doc)
        self.session.commit()
        user = InferredUser(
            id=uuid.uuid4(),
        )
        self.session.add(user)
        self.session.commit()
        bookmark = Bookmark(
            id=uuid.uuid4(), document_id=doc.id, inferred_user_id=user.id
        )
        self.session.add(bookmark)
        self.session.commit()
        bookmark_from_db = (
            self.session.query(Bookmark).filter_by(inferred_user_id=user.id).first()
        )
        self.assertIsNotNone(bookmark_from_db)
        self.assertEqual(bookmark_from_db.welearn_document.title, "Document Test")
        self.session.delete(bookmark_from_db)
        self.session.commit()
        self.assertIsNone(
            self.session.query(Bookmark).filter_by(inferred_user_id=user.id).first()
        )

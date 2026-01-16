import uuid
from datetime import datetime, timedelta
from unittest import TestCase

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tests.helpers import handle_schema_with_sqlite
from welearn_database.data.models import Base
from welearn_database.data.models.user_related import (
    APIKeyManagement,
    Bookmark,
    ChatMessage,
    DataCollectionCampaignManagement,
    EndpointRequest,
    InferredUser,
    ReturnedDocument,
)
from welearn_database.data.models.user_related import Session as UserSession
from welearn_database.data.models.user_related import (
    UserProfile,
)


class TestUserRelatedCRUD(TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")
        handle_schema_with_sqlite(self.engine)
        self.s_maker = sessionmaker(self.engine)
        Base.metadata.create_all(self.engine)
        self.session = self.s_maker()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_create_and_read_user_profile(self):
        user = UserProfile(
            id=uuid.uuid4(),
            username="testuser",
            email="test@example.com",
            password_digest=b"hashed",
        )
        self.session.add(user)
        self.session.commit()
        result = self.session.query(UserProfile).filter_by(username="testuser").first()
        self.assertIsNotNone(result)
        self.assertEqual(result.email, "test@example.com")

    def test_create_and_read_inferred_user(self):
        inferred_user = InferredUser(
            id=uuid.uuid4(),
            origin_referrer="test_ref",
        )
        self.session.add(inferred_user)
        self.session.commit()
        result = (
            self.session.query(InferredUser)
            .filter_by(origin_referrer="test_ref")
            .first()
        )
        self.assertIsNotNone(result)

    def test_create_and_read_session(self):
        inferred_user = InferredUser(id=uuid.uuid4())
        self.session.add(inferred_user)
        self.session.commit()
        session = UserSession(
            id=uuid.uuid4(),
            inferred_user_id=inferred_user.id,
            origin_referrer="ref",
            end_at=datetime.now() + timedelta(hours=1),
            host="localhost",
        )
        self.session.add(session)
        self.session.commit()
        result = self.session.query(UserSession).filter_by(host="localhost").first()
        self.assertIsNotNone(result)

    def test_create_and_read_api_key_management(self):
        api_key = APIKeyManagement(
            id=uuid.uuid4(),
            title="key1",
            register_email="reg@example.com",
            digest=b"digest",
            is_active=True,
        )
        self.session.add(api_key)
        self.session.commit()
        result = self.session.query(APIKeyManagement).filter_by(title="key1").first()
        self.assertIsNotNone(result)
        self.assertTrue(result.is_active)
        self.assertEqual(result.digest, b"digest")

    def test_create_and_read_data_collection_campaign_management(self):
        campaign = DataCollectionCampaignManagement(
            id=uuid.uuid4(),
            is_active=True,
            end_at=datetime.now() + timedelta(days=1),
        )
        self.session.add(campaign)
        self.session.commit()
        result = self.session.query(DataCollectionCampaignManagement).first()
        self.assertIsNotNone(result)
        self.assertTrue(result.is_active)

    def test_create_and_read_chat_message(self):
        inferred_user = InferredUser(id=uuid.uuid4())
        self.session.add(inferred_user)
        self.session.commit()
        chat = ChatMessage(
            id=uuid.uuid4(),
            inferred_user_id=inferred_user.id,
            conversation_id=uuid.uuid4(),
            role="user",
            textual_content="Bonjour",
        )
        self.session.add(chat)
        self.session.commit()
        result = self.session.query(ChatMessage).filter_by(role="user").first()
        self.assertIsNotNone(result)
        self.assertEqual(result.textual_content, "Bonjour")

    def test_create_and_read_bookmark(self):
        inferred_user = InferredUser(id=uuid.uuid4())
        self.session.add(inferred_user)
        self.session.commit()
        # On suppose que le document existe déjà, sinon il faut mocker ou ignorer la FK
        bookmark = Bookmark(
            id=uuid.uuid4(),
            document_id=uuid.uuid4(),
            inferred_user_id=inferred_user.id,
        )
        self.session.add(bookmark)
        self.session.commit()
        result = (
            self.session.query(Bookmark)
            .filter_by(inferred_user_id=inferred_user.id)
            .first()
        )
        self.assertIsNotNone(result)

    def test_create_and_read_returned_document(self):
        inferred_user = InferredUser(id=uuid.uuid4())
        self.session.add(inferred_user)
        self.session.commit()
        chat = ChatMessage(
            id=uuid.uuid4(),
            inferred_user_id=inferred_user.id,
            conversation_id=uuid.uuid4(),
            role="user",
            textual_content="test",
        )
        self.session.add(chat)
        self.session.commit()
        returned_doc = ReturnedDocument(
            id=uuid.uuid4(),
            message_id=chat.id,
            document_id=uuid.uuid4(),
            is_clicked=True,
        )
        self.session.add(returned_doc)
        self.session.commit()
        result = self.session.query(ReturnedDocument).filter_by(is_clicked=True).first()
        self.assertIsNotNone(result)

    def test_create_and_read_endpoint_request(self):
        inferred_user = InferredUser(id=uuid.uuid4())
        self.session.add(inferred_user)
        self.session.commit()
        session = UserSession(
            id=uuid.uuid4(),
            inferred_user_id=inferred_user.id,
            origin_referrer="ref",
            end_at=datetime.now() + timedelta(hours=1),
            host="localhost",
        )
        self.session.add(session)
        self.session.commit()
        endpoint = EndpointRequest(
            id=uuid.uuid4(),
            session_id=session.id,
            endpoint_name="test_endpoint",
            http_code=200,
            message="ok",
        )
        self.session.add(endpoint)
        self.session.commit()
        result = (
            self.session.query(EndpointRequest)
            .filter_by(endpoint_name="test_endpoint")
            .first()
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.http_code, 200)

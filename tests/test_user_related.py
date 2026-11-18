import uuid
from datetime import datetime, timedelta
from unittest import TestCase

from sqlalchemy import create_engine, func, inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from tests.helpers import handle_schema_with_sqlite
from welearn_database.data.enumeration import FilterType, QuestionType
from welearn_database.data.models import Base
from welearn_database.data.models.user_related import (
    AnalyticForm,
    APIKeyManagement,
    Bookmark,
    ChatMessage,
    DataCollectionCampaignManagement,
    EndpointRequest,
    Feature,
    FilterUsedInQuery,
    GuestFeatureUsage,
    InferredUser,
    ReturnedDocument,
)
from welearn_database.data.models.user_related import Session as UserSession
from welearn_database.data.models.user_related import Thread, UserProfile


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

    def test_create_and_read_inferred_user_with_university_data(self):
        inferred_user = InferredUser(
            id=uuid.uuid4(),
            origin_referrer="test_ref",
            university_title="test_university",
            role="student",
        )
        self.session.add(inferred_user)
        self.session.commit()
        result = (
            self.session.query(InferredUser)
            .filter_by(origin_referrer="test_ref")
            .first()
        )
        self.assertEqual(result.university_title, "test_university")
        self.assertEqual(result.role, "student")

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
            original_feature_name="chat",
        )
        self.session.add(chat)
        self.session.commit()
        result = self.session.query(ChatMessage).filter_by(role="user").first()
        self.assertIsNotNone(result)
        self.assertEqual(result.textual_content, "Bonjour")
        self.assertFalse(result.is_retrieved_by_user)

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
            original_feature_name="chat",
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

    def test_create_and_read_filter_used_in_query(self):
        inferred_user = InferredUser(id=uuid.uuid4())
        self.session.add(inferred_user)
        self.session.commit()
        chat = ChatMessage(
            id=uuid.uuid4(),
            inferred_user_id=inferred_user.id,
            conversation_id=uuid.uuid4(),
            role="user",
            original_feature_name="chat",
            textual_content="test",
        )
        self.session.add(chat)
        self.session.commit()
        filter_used = FilterUsedInQuery(
            id=uuid.uuid4(),
            message_id=chat.id,
            filter_type=FilterType.SDG.value,
            filter_value="13",
        )
        self.session.add(filter_used)
        self.session.commit()
        result = (
            self.session.query(FilterUsedInQuery).filter_by(filter_value="13").first()
        )
        self.assertIsNotNone(result)

    def test_create_and_read_analytic_form(self):
        inferred_user = InferredUser(id=uuid.uuid4())
        self.session.add(inferred_user)
        self.session.commit()

        user_session = UserSession(
            id=uuid.uuid4(),
            inferred_user_id=inferred_user.id,
            origin_referrer="ref",
            end_at=datetime.now() + timedelta(hours=1),
            host="localhost",
        )
        self.session.add(user_session)
        self.session.commit()

        analytic_form = AnalyticForm(
            id=uuid.uuid4(),
            form_name="feedback_form",
            question="Comment evaluez-vous la pertinence ?",
            answer="Tres pertinente",
            answer_type=QuestionType.TEXT.value,
            session_id=user_session.id,
        )
        self.session.add(analytic_form)
        self.session.commit()

        result = (
            self.session.query(AnalyticForm)
            .filter_by(form_name="feedback_form", session_id=user_session.id)
            .first()
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.question, "Comment evaluez-vous la pertinence ?")
        self.assertEqual(result.answer, "Tres pertinente")
        self.assertEqual(result.answer_type, QuestionType.TEXT.value)
        self.assertEqual(result.session_id, user_session.id)

    def test_analytic_form_session_relationship(self):
        inferred_user = InferredUser(id=uuid.uuid4())
        self.session.add(inferred_user)
        self.session.commit()

        user_session = UserSession(
            id=uuid.uuid4(),
            inferred_user_id=inferred_user.id,
            origin_referrer="ref",
            end_at=datetime.now() + timedelta(hours=1),
            host="localhost",
        )
        self.session.add(user_session)
        self.session.commit()

        analytic_form = AnalyticForm(
            id=uuid.uuid4(),
            form_name="feedback_form",
            question="Question test",
            answer="Reponse test",
            answer_type=QuestionType.PREDEFINED_TEXT.value,
            session_id=user_session.id,
        )
        self.session.add(analytic_form)
        self.session.commit()

        result = self.session.query(AnalyticForm).filter_by(id=analytic_form.id).first()
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.session)
        self.assertEqual(result.session.id, user_session.id)

    def _add_user_and_feature(self, title="chat"):
        inferred_user = InferredUser(id=uuid.uuid4())
        feature = Feature(id=uuid.uuid4(), title=title)
        self.session.add_all([inferred_user, feature])
        self.session.commit()
        return inferred_user, feature

    def test_create_and_read_thread(self):
        inferred_user, feature = self._add_user_and_feature()
        thread = Thread(
            id=uuid.uuid4(),
            inferred_user_id=inferred_user.id,
            feature_id=feature.id,
            title="What is a carbon budget?",
        )
        self.session.add(thread)
        self.session.commit()

        result = self.session.query(Thread).filter_by(id=thread.id).first()
        self.assertEqual(result.title, "What is a carbon budget?")
        self.assertEqual(result.feature.title, "chat")
        self.assertEqual(result.inferred_user.id, inferred_user.id)
        self.assertFalse(result.is_finished)
        self.assertIsNone(result.current_step)
        self.assertIsNotNone(result.created_at)
        self.assertIsNotNone(result.updated_at)

    def test_thread_with_steps(self):
        inferred_user, feature = self._add_user_and_feature("microlearning")
        thread = Thread(
            id=uuid.uuid4(),
            inferred_user_id=inferred_user.id,
            feature_id=feature.id,
            current_step=2,
            max_step=5,
        )
        self.session.add(thread)
        self.session.commit()

        thread.current_step = 5
        thread.is_finished = True
        self.session.commit()

        result = self.session.query(Thread).filter_by(id=thread.id).first()
        self.assertEqual((result.current_step, result.max_step), (5, 5))
        self.assertTrue(result.is_finished)

    def test_thread_title_is_optional(self):
        inferred_user, feature = self._add_user_and_feature()
        thread = Thread(
            id=uuid.uuid4(), inferred_user_id=inferred_user.id, feature_id=feature.id
        )
        self.session.add(thread)
        self.session.commit()
        self.assertIsNone(self.session.get(Thread, thread.id).title)

    def test_thread_requires_a_feature(self):
        inferred_user, _ = self._add_user_and_feature()
        self.session.add(Thread(id=uuid.uuid4(), inferred_user_id=inferred_user.id))
        with self.assertRaises(IntegrityError):
            self.session.commit()

    def test_feature_title_is_unique(self):
        self._add_user_and_feature("chat")
        self.session.add(Feature(id=uuid.uuid4(), title="chat"))
        with self.assertRaises(IntegrityError):
            self.session.commit()

    def test_thread_list_index(self):
        indexes = inspect(self.engine).get_indexes("thread", schema="user_related")
        index = next(
            i for i in indexes if i["name"] == "thread_user_feature_updated_idx"
        )
        self.assertEqual(index["column_names"][:2], ["inferred_user_id", "feature_id"])

    def _add_guest_features(self):
        features = {
            title: Feature(id=uuid.uuid4(), title=title)
            for title in ("chat", "syllabus")
        }
        self.session.add_all(features.values())
        self.session.commit()
        return features

    def _add_usage(self, user_id, feature, action, created_at):
        usage = GuestFeatureUsage(
            id=uuid.uuid4(),
            inferred_user_id=user_id,
            feature_id=feature.id,
            action=action,
            created_at=created_at,
        )
        self.session.add(usage)
        return usage

    def test_create_and_read_guest_feature_usage(self):
        features = self._add_guest_features()
        inferred_user = InferredUser(id=uuid.uuid4())
        self.session.add(inferred_user)
        self.session.commit()
        usage = GuestFeatureUsage(
            id=uuid.uuid4(),
            inferred_user_id=inferred_user.id,
            feature_id=features["chat"].id,
            action="question",
        )
        self.session.add(usage)
        self.session.commit()

        result = self.session.get(GuestFeatureUsage, usage.id)
        self.assertEqual(result.feature.title, "chat")
        self.assertEqual(result.action, "question")
        self.assertEqual(result.inferred_user.id, inferred_user.id)
        self.assertIsNotNone(result.created_at)

    def test_guest_feature_usage_counts_one_action_in_window(self):
        syllabus = self._add_guest_features()["syllabus"]
        guest = InferredUser(id=uuid.uuid4())
        other_guest = InferredUser(id=uuid.uuid4())
        self.session.add_all([guest, other_guest])
        self.session.commit()
        now = datetime.now()
        self._add_usage(guest.id, syllabus, "feedback", now - timedelta(hours=25))
        oldest_in_window = now - timedelta(hours=20)
        self._add_usage(guest.id, syllabus, "feedback", oldest_in_window)
        self._add_usage(guest.id, syllabus, "feedback", now - timedelta(minutes=5))
        # same feature, other quotas
        self._add_usage(guest.id, syllabus, "generate", now)
        self._add_usage(guest.id, syllabus, "files", now)
        self._add_usage(other_guest.id, syllabus, "feedback", now)
        self.session.commit()

        count, oldest = (
            self.session.query(
                func.count(GuestFeatureUsage.id), func.min(GuestFeatureUsage.created_at)
            )
            .join(Feature)
            .filter(
                GuestFeatureUsage.inferred_user_id == guest.id,
                Feature.title == "syllabus",
                GuestFeatureUsage.action == "feedback",
                GuestFeatureUsage.created_at > now - timedelta(hours=24),
            )
            .one()
        )
        self.assertEqual(count, 2)
        self.assertEqual(oldest, oldest_in_window)

    def test_guest_feature_usage_requires_a_user(self):
        features = self._add_guest_features()
        self.session.add(
            GuestFeatureUsage(
                id=uuid.uuid4(), feature_id=features["chat"].id, action="question"
            )
        )
        with self.assertRaises(IntegrityError):
            self.session.commit()

    def test_guest_feature_usage_requires_a_feature(self):
        inferred_user = InferredUser(id=uuid.uuid4())
        self.session.add(inferred_user)
        self.session.commit()
        self.session.add(
            GuestFeatureUsage(
                id=uuid.uuid4(), inferred_user_id=inferred_user.id, action="question"
            )
        )
        with self.assertRaises(IntegrityError):
            self.session.commit()

    def test_guest_feature_usage_requires_an_action(self):
        features = self._add_guest_features()
        inferred_user = InferredUser(id=uuid.uuid4())
        self.session.add(inferred_user)
        self.session.commit()
        self.session.add(
            GuestFeatureUsage(
                id=uuid.uuid4(),
                inferred_user_id=inferred_user.id,
                feature_id=features["chat"].id,
            )
        )
        with self.assertRaises(IntegrityError):
            self.session.commit()

    def test_guest_feature_usage_index(self):
        indexes = inspect(self.engine).get_indexes(
            "guest_feature_usage", schema="user_related"
        )
        index = next(
            i
            for i in indexes
            if i["name"] == "guest_feature_usage_user_feature_action_created_idx"
        )
        self.assertEqual(
            index["column_names"],
            ["inferred_user_id", "feature_id", "action", "created_at"],
        )

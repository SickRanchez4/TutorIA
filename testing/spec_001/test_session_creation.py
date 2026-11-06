"""A-3 / RF-3, RF-6: original view body, not decorators or real SQL."""
from datetime import datetime
import inspect
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from testing.support import isolated_backend


class SessionCreationTests(unittest.TestCase):
    def setUp(self):
        self.backend = self.enterContext(isolated_backend())
        self.module = self.backend.student
        self.user_id = "00000000-0000-0000-0000-000000000010"
        self.course_id = 7
        self.session = Mock()
        self.enrollment_query = Mock()
        self.enrollment_query.filter_by.return_value.first.return_value = SimpleNamespace(is_active=True)
        self.session_model = Mock(side_effect=self.module.SesionChat)
        self.enterContext(patch.object(self.module, "db", SimpleNamespace(session=self.session)))
        self.enterContext(patch.object(self.module, "EstudianteCurso", SimpleNamespace(query=self.enrollment_query)))
        self.enterContext(patch.object(self.module, "SesionChat", self.session_model))
        self.enterContext(patch.object(self.module, "get_jwt_identity", return_value=self.user_id))
        self.enterContext(patch.object(self.module, "logger", Mock()))
        self.session.commit.side_effect = self.simulate_insert_defaults
        self.view = inspect.unwrap(self.module.create_sesion)

    def simulate_insert_defaults(self):
        """Provide insertion defaults for the real model's serialization only."""
        entity = self.session.add.call_args.args[0]
        entity.id = "00000000-0000-0000-0000-000000000020"
        entity.is_active = True
        entity.created_at = entity.updated_at = datetime(2026, 9, 30, 12)

    def request(self, body):
        with self.backend.flask_app.test_request_context(
            "/api/estudiante/chat/sesiones", method="POST", json=body,
        ):
            response, status = self.view()
            return response.get_json(), status

    def assert_no_creation(self):
        self.session_model.assert_not_called()
        self.session.add.assert_not_called()
        self.session.commit.assert_not_called()
        self.session.rollback.assert_not_called()

    def test_A3_P1_missing_course(self):
        """Missing course returns the existing validation contract."""
        self.assertEqual(self.request({}), ({"message": "curso_id es requerido"}, 400))
        self.enrollment_query.filter_by.assert_not_called()
        self.assert_no_creation()

    def test_A3_P2_invalid_course_conversion(self):
        """A nonconvertible course returns 400 before enrollment lookup."""
        self.assertEqual(self.request({"curso_id": "not-an-integer"}),
                         ({"message": "curso_id debe ser un número"}, 400))
        self.enrollment_query.filter_by.assert_not_called()
        self.assert_no_creation()

    def test_A3_P3_missing_active_enrollment(self):
        """Use the real enrollment helper with a simulated empty query."""
        self.enrollment_query.filter_by.return_value.first.return_value = None
        self.assertEqual(self.request({"curso_id": self.course_id}),
                         ({"message": "No estás inscrito en este curso"}, 403))
        self.enrollment_query.filter_by.assert_called_once_with(
            user_id=self.user_id, curso_id=self.course_id, is_active=True,
        )
        self.assert_no_creation()

    def test_A3_P4_persistence_failure(self):
        """Failure before commit completion rolls back and hides internals."""
        self.session.commit.side_effect = RuntimeError("controlled persistence failure")
        body, status = self.request({"curso_id": self.course_id})
        self.assertEqual(status, 500)
        self.assertEqual(body, {"message": "Error al crear la sesión"})
        self.assertNotIn("controlled persistence failure", str(body))
        self.session.add.assert_called_once()
        self.session.commit.assert_called_once_with()
        self.session.rollback.assert_called_once_with()
        self.module.logger.exception.assert_called_once()

    def test_A3_P5_create_with_default_title(self):
        """Observe identity/course, default title, serialization and commit."""
        body, status = self.request({"curso_id": self.course_id})
        self.assertEqual(status, 201)
        self.assertEqual(body["sesion"]["user_id"], self.user_id)
        self.assertEqual(body["sesion"]["curso_id"], self.course_id)
        self.assertEqual(body["sesion"]["titulo"], "Nueva Conversación")
        self.session_model.assert_called_once_with(
            user_id=self.user_id, curso_id=self.course_id, titulo="Nueva Conversación",
        )
        self.session.add.assert_called_once()
        self.session.commit.assert_called_once_with()
        self.session.rollback.assert_not_called()
        self.enrollment_query.filter_by.assert_called_once_with(
            user_id=self.user_id, curso_id=self.course_id, is_active=True,
        )

    def test_A3_V4_explicit_title(self):
        """A supplied title is trimmed without changing the creation path."""
        body, status = self.request({"curso_id": self.course_id, "titulo": "  Test conversation  "})
        self.assertEqual(status, 201)
        self.assertEqual(body["sesion"]["titulo"], "Test conversation")
        self.session.commit.assert_called_once_with()
        self.session.rollback.assert_not_called()
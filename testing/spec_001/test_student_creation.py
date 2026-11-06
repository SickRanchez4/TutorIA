"""A-2 / RF-3, RF-5: reuse, creation and essential rejection paths."""
import secrets
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from testing.support import isolated_backend


class StudentCreationTests(unittest.TestCase):
    def setUp(self):
        self.backend = self.enterContext(isolated_backend())
        self.module = self.backend.coordinator
        self.tenant_id = "00000000-0000-0000-0000-000000000001"
        self.email = "student@example.invalid"
        self.password = secrets.token_urlsafe(16) + "Aa1!"
        self.student_role = self.module.Role(name="estudiante")
        # Keep the real ORM constructor, but replace the query boundary.
        self.user_model = Mock(side_effect=self.module.User)
        self.user_model.query.filter_by.return_value.first.return_value = None
        self.role_query = Mock()
        self.role_query.filter_by.return_value.first.return_value = self.student_role
        self.session = Mock()
        self.capacity = Mock(return_value=(True, None))
        self.enterContext(patch.object(self.module, "User", self.user_model))
        self.enterContext(patch.object(self.module, "Role", SimpleNamespace(query=self.role_query)))
        self.enterContext(patch.object(self.module, "db", SimpleNamespace(session=self.session)))
        self.enterContext(patch.object(self.module, "account_creation_allowed", self.capacity))
        self.enterContext(patch.object(self.module, "generate_password_hash", return_value="isolated-hash"))

    def create(self, email=None, password=None):
        return self.module._get_or_create_estudiante(
            self.email if email is None else email,
            "Test", "Student", "", self.password if password is None else password,
            self.tenant_id,
        )

    def assert_no_creation(self):
        self.user_model.assert_not_called()
        self.session.add.assert_not_called()
        self.session.flush.assert_not_called()
        self.session.commit.assert_not_called()

    def existing(self, tenant_id=None, roles=None):
        user = SimpleNamespace(
            id="00000000-0000-0000-0000-000000000010",
            institucion_id=tenant_id or self.tenant_id,
            roles=[self.student_role] if roles is None else roles,
        )
        self.user_model.query.filter_by.return_value.first.return_value = user
        return user

    def test_A2_P1_invalid_email(self):
        """The existing validator rejects invalid email before account lookup."""
        with self.assertRaisesRegex(ValueError, "Email inválido"):
            self.create(email="invalid-email")
        self.user_model.query.filter_by.assert_not_called()
        self.assert_no_creation()

    def test_A2_P2_other_tenant(self):
        """A globally unique email must not reuse another tenant's account."""
        user = self.existing(tenant_id="00000000-0000-0000-0000-000000000002")
        with self.assertRaises(self.module.StudentTenantConflict):
            self.create()
        self.assertEqual(user.institucion_id, "00000000-0000-0000-0000-000000000002")
        self.capacity.assert_not_called()
        self.assert_no_creation()

    def test_A2_P3_incompatible_role(self):
        """Same tenant is insufficient when the existing role is incompatible."""
        self.existing(roles=[SimpleNamespace(name="coordinador")])
        with self.assertRaisesRegex(ValueError, "no tiene rol de estudiante"):
            self.create()
        self.capacity.assert_not_called()
        self.assert_no_creation()

    def test_A2_P4_reuse_normalized_email(self):
        """Reuse the identical account after real email normalization."""
        existing = self.existing()
        user, created = self.create(email="  STUDENT@EXAMPLE.INVALID  ")
        self.assertIs(user, existing)
        self.assertFalse(created)
        self.user_model.query.filter_by.assert_called_once_with(email=self.email)
        self.capacity.assert_not_called()
        self.assert_no_creation()

    def test_A2_P5_invalid_password(self):
        """One invalid-password representative exercises the validator outcome."""
        with self.assertRaisesRegex(ValueError, "al menos 8 caracteres"):
            self.create(password="x")
        self.capacity.assert_not_called()
        self.assert_no_creation()

    def test_A2_P6_capacity_denied(self):
        """New valid accounts must respect the shared capacity decision."""
        self.capacity.return_value = (False, "Límite de cuentas alcanzado para el plan asignado")
        with self.assertRaises(self.module.AccountLimitReached):
            self.create()
        self.capacity.assert_called_once_with(self.tenant_id)
        self.role_query.filter_by.assert_not_called()
        self.assert_no_creation()

    def test_A2_P7_missing_configured_role(self):
        """Simulate missing configuration without deleting any real role."""
        self.role_query.filter_by.return_value.first.return_value = None
        with self.assertRaisesRegex(RuntimeError, "Rol estudiante no configurado"):
            self.create()
        self.role_query.filter_by.assert_called_once_with(name="estudiante")
        self.assert_no_creation()

    def test_A2_P8_create_student(self):
        """Create a real model object and observe add/flush, never commit."""
        user, created = self.create()
        self.assertTrue(created)
        self.assertEqual(user.email, self.email)
        self.assertEqual(user.institucion_id, self.tenant_id)
        self.assertEqual((user.first_name, user.last_name, user.phone), ("Test", "Student", ""))
        self.assertTrue(user.is_active)
        self.assertEqual(user.roles, [self.student_role])
        self.assertEqual(user.password_hash, "isolated-hash")
        self.capacity.assert_called_once_with(self.tenant_id)
        self.session.add.assert_called_once_with(user)
        self.session.flush.assert_called_once_with()
        self.session.commit.assert_not_called()
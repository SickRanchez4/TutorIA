"""A-1 / RF-3, RF-4: essential capacity paths with simulated queries."""
from datetime import datetime, timedelta
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from testing.support import isolated_backend


class AccountCapacityTests(unittest.TestCase):
    def setUp(self):
        self.backend = self.enterContext(isolated_backend())
        self.module = self.backend.quota
        self.reference = datetime(2026, 9, 30, 12)
        self.tenant_id = "00000000-0000-0000-0000-000000000001"
        self.plan = SimpleNamespace(max_cuentas=2, is_active=True)
        self.subscription = SimpleNamespace(
            plan=self.plan, is_active=True,
            fecha_inicio=self.reference - timedelta(days=1),
            fecha_fin=self.reference + timedelta(days=1),
        )
        self.subscription_query = Mock()
        self.subscription_query.filter_by.return_value.first.return_value = self.subscription
        self.user_query = Mock()
        self.user_query.filter_by.return_value.count.return_value = 1
        self.enterContext(patch.object(
            self.module, "Suscripcion", SimpleNamespace(query=self.subscription_query),
        ))
        self.enterContext(patch.object(
            self.module, "User", SimpleNamespace(query=self.user_query),
        ))

    def allowed(self):
        return self.module.account_creation_allowed(self.tenant_id, self.reference)

    def test_A1_P1_missing_subscription(self):
        """Reject unconfigured subscriptions before any capacity query."""
        self.subscription_query.filter_by.return_value.first.return_value = None
        self.assertEqual(self.allowed(), (False, "La institución no tiene una suscripción configurada"))
        self.subscription_query.filter_by.assert_called_once_with(institucion_id=self.tenant_id)
        self.user_query.filter_by.assert_not_called()

    def test_A1_P2_inactive_subscription(self):
        """An inactive subscription cannot authorize an account."""
        self.subscription.is_active = False
        self.assertEqual(self.allowed(), (False, "La suscripción de la institución no está activa o vigente"))
        self.user_query.filter_by.assert_not_called()

    def test_A1_P3_unlimited_capacity(self):
        """Unlimited capacity bypasses the active-account count."""
        self.plan.max_cuentas = None
        self.assertEqual(self.allowed(), (True, None))
        self.user_query.filter_by.assert_not_called()

    def test_A1_P4_capacity_reached(self):
        """The exact finite limit rejects another account."""
        self.user_query.filter_by.return_value.count.return_value = 2
        self.assertEqual(self.allowed(), (False, "Límite de cuentas alcanzado para el plan asignado"))

    def test_A1_P5_capacity_available(self):
        """Available capacity queries only active accounts in this tenant."""
        self.assertEqual(self.allowed(), (True, None))
        self.user_query.filter_by.assert_called_once_with(institucion_id=self.tenant_id, is_active=True)
        self.user_query.filter_by.return_value.count.assert_called_once_with()

    def test_A1_V1_missing_plan(self):
        """Model a missing relation safely, without corrupting SQL foreign keys."""
        self.subscription.plan = None
        self.assertEqual(self.allowed(), (False, "La institución no tiene una suscripción configurada"))
        self.user_query.filter_by.assert_not_called()

    def test_A1_V2_invalid_validity_or_plan(self):
        """Future, expired and inactive-plan variants share rejection path P2."""
        for variant in ("future", "expired", "inactive_plan"):
            with self.subTest(case=variant):
                self.subscription.fecha_inicio = self.reference - timedelta(days=1)
                self.subscription.fecha_fin = self.reference + timedelta(days=1)
                self.plan.is_active = variant != "inactive_plan"
                if variant == "future":
                    self.subscription.fecha_inicio = self.reference + timedelta(seconds=1)
                elif variant == "expired":
                    self.subscription.fecha_fin = self.reference - timedelta(seconds=1)
                self.assertEqual(self.allowed(), (False, "La suscripción de la institución no está activa o vigente"))
        self.user_query.filter_by.assert_not_called()

    def test_A1_V3_inclusive_date_boundaries(self):
        """The implemented start/end boundaries are inclusive."""
        for boundary in ("fecha_inicio", "fecha_fin"):
            with self.subTest(case=boundary):
                self.subscription.fecha_inicio = self.reference - timedelta(days=1)
                self.subscription.fecha_fin = self.reference + timedelta(days=1)
                setattr(self.subscription, boundary, self.reference)
                self.assertEqual(self.allowed(), (True, None))

    def test_A1_V4_capacity_exceeded(self):
        """An already exceeded finite limit also rejects creation."""
        self.user_query.filter_by.return_value.count.return_value = 3
        self.assertEqual(self.allowed(), (False, "Límite de cuentas alcanzado para el plan asignado"))
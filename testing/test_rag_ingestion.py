"""Focused RAG contract tests with network, SQL and dotenv access blocked."""
import importlib
import json
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from testing.support import isolated_backend


class RagIngestionTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(isolated_backend())
        self.module = importlib.import_module("services.rag_ingestion")
        self.session = Mock()
        self.enterContext(patch.object(self.module, "db", SimpleNamespace(session=self.session)))
        self.post = self.enterContext(patch.object(self.module.requests, "post"))
        self.enterContext(patch.dict(self.module.os.environ, {
            "N8N_EMBEDDINGS_WEBHOOK_URL": "https://processor.invalid/upload",
            "N8N_KNOWLEDGE_ADMIN_WEBHOOK_URL": "https://processor.invalid/admin",
            "N8N_KNOWLEDGE_ADMIN_TOKEN": "test-token-not-a-real-credential",
        }))
        self.cleanup = self.enterContext(patch.object(self.module, "_remove_local_job_files"))
        self.enterContext(patch.object(self.module, "_job_files", return_value=[]))
        self.job = SimpleNamespace(
            id="job-test", curso_id=405, institucion_id="tenant-test",
            coordinador_id="coordinator-test", documents=lambda: [{"archivo": "fisica.pdf"}],
        )

    def test_ingestion_requires_explicit_complete_confirmation(self):
        for response in ({}, {"success": False}, {"success": True, "data": {"archivos_procesados": 0}}):
            with self.subTest(response=response):
                self.post.return_value = Mock(status_code=200, json=Mock(return_value=response))
                with self.assertRaises(self.module.RagIngestionError):
                    self.module.dispatch_ingestion_job(self.job)
                self.assertEqual(self.job.estado, "unknown")
                self.cleanup.assert_not_called()

    def test_ingestion_retains_sources_when_n8n_returns_non_json(self):
        self.post.return_value = Mock(status_code=200, json=Mock(side_effect=ValueError("not JSON")))
        with self.assertRaises(self.module.RagIngestionError):
            self.module.dispatch_ingestion_job(self.job)
        self.assertEqual(self.job.estado, "unknown")
        self.cleanup.assert_not_called()

    def test_confirmed_ingestion_completes_and_removes_temporary_sources(self):
        self.post.return_value = Mock(status_code=200, json=Mock(return_value={
            "success": True, "data": {"archivos_procesados": 1, "chunks_indexados": 4},
        }))
        self.module.dispatch_ingestion_job(self.job)
        self.assertEqual(self.job.estado, "completed")
        self.assertEqual(self.job.chunks_indexados, 4)
        self.cleanup.assert_called_once_with(self.job)

    def test_ingestion_persists_only_profiles_for_received_documents(self):
        self.post.return_value = Mock(status_code=200, json=Mock(return_value={
            "success": True, "data": {
                "archivos_procesados": 1,
                "document_catalog": [
                    {"archivo": "fisica.pdf", "titulo": "Física", "paginas": 42, "extracto_inicial": "Newton"},
                    {"archivo": "otro.pdf", "titulo": "No pertenece al trabajo"},
                ],
            },
        }))
        self.module.dispatch_ingestion_job(self.job)
        self.assertEqual(json.loads(self.job.documentos_json), [{
            "archivo": "fisica.pdf", "titulo": "Física", "paginas": 42, "extracto_inicial": "Newton",
        }])

    def test_catalog_uses_all_completed_course_jobs_and_keeps_latest_document_profile(self):
        model = Mock()
        filtered = model.query.filter_by.return_value
        filtered.order_by.return_value.all.return_value = [
            SimpleNamespace(documents=lambda: [{"archivo": "fisica.pdf", "titulo": "Edición actual"}]),
            SimpleNamespace(documents=lambda: [{"archivo": "fisica.pdf", "titulo": "Edición antigua"}]),
            *[SimpleNamespace(documents=lambda n=n: [{"archivo": f"libro-{n}.pdf"}]) for n in range(7)],
        ]
        with patch.object(self.module, "RagIngestionJob", model):
            catalog = self.module.course_material_catalog(SimpleNamespace(id=405, institucion_id="tenant-test"))
        self.assertEqual(len(catalog), 8)
        self.assertEqual(catalog[0]["titulo"], "Edición actual")
        model.query.filter_by.assert_called_once_with(
            curso_id=405, institucion_id="tenant-test", estado="completed",
        )
        filtered.order_by.return_value.limit.assert_not_called()

    def test_chat_payload_scopes_recent_history_and_materials_to_validated_session(self):
        student = importlib.import_module("routes.estudiante")
        course = SimpleNamespace(id=405, institucion_id="tenant-test", nombre="Biología")
        messages = Mock()
        messages.query.filter_by.return_value.order_by.return_value.limit.return_value.all.return_value = [
            SimpleNamespace(rol="assistant", contenido="La selección natural"),
            SimpleNamespace(rol="user", contenido="¿Cuál es el tema?"),
        ]
        with (
            patch.object(student, "Curso", SimpleNamespace(query=Mock(get=Mock(return_value=course)))),
            patch.object(student, "ConfiguracionIA", SimpleNamespace(query=Mock(get=Mock(return_value=None)))),
            patch.object(student, "MensajeChat", messages),
            patch.object(student, "course_material_catalog", return_value=[{"archivo": "darwin.pdf"}]) as catalog,
        ):
            payload = student._build_n8n_chat_payload(
                SimpleNamespace(id="session-405", curso_id=405), "Explica eso", "chat", "student", 1024,
            )
        self.assertEqual(payload["pinecone_namespace"], "inst_tenant-test_curso_405")
        self.assertEqual(payload["recent_history"][0]["role"], "user")
        self.assertEqual(payload["course_materials"], [{"archivo": "darwin.pdf"}])
        messages.query.filter_by.assert_called_once_with(sesion_chat_id="session-405")
        catalog.assert_called_once_with(course)

    def test_cleanup_authenticates_and_checks_exact_namespace(self):
        payload = {"institucion_id": "tenant-test", "curso_id": 405}
        self.post.return_value.json.return_value = {
            "success": True, "action": "clear_course", "namespace": "inst_tenant-test_curso_405",
        }
        self.module._call_knowledge_admin_webhook("clear_course", payload)
        self.assertEqual(self.post.call_args.kwargs["headers"], {"X-TutorIA-Token": "test-token-not-a-real-credential"})
        self.post.return_value.json.return_value["namespace"] = "inst_other_curso_405"
        with self.assertRaises(self.module.RagIngestionError):
            self.module._call_knowledge_admin_webhook("clear_course", payload)

    def test_cleanup_failure_does_not_remove_local_history(self):
        course = SimpleNamespace(id=405, institucion_id="tenant-test")
        self.enterContext(patch.object(self.module, "get_managed_course", return_value=course))
        jobs = Mock()
        jobs.query.filter_by.return_value.all.return_value = [self.job]
        self.enterContext(patch.object(self.module, "RagIngestionJob", jobs))
        self.post.return_value.json.return_value = {}
        with self.assertRaises(self.module.RagIngestionError):
            self.module.clear_course_knowledge(SimpleNamespace(), 405)
        self.cleanup.assert_not_called()
        self.session.delete.assert_not_called()
        self.session.commit.assert_not_called()

    def test_cleanup_rejects_missing_token_before_network_call(self):
        with patch.dict(self.module.os.environ, {"N8N_KNOWLEDGE_ADMIN_TOKEN": ""}):
            with self.assertRaises(self.module.RagIngestionError) as error:
                self.module._call_knowledge_admin_webhook("clear_course", {})
        self.assertEqual(error.exception.status_code, 503)
        self.post.assert_not_called()

# -*- coding: utf-8 -*-
"""Testes (stdlib unittest) das funcoes novas do server.py. Rodar: python3 -m unittest"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # datacamp/
import server


class ServerProgressTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        server.DB_PATH = d / "test.db"
        server.SAVED_DIR = d / "saved_code"
        server.init_db()

    def tearDown(self):
        self.tmp.cleanup()

    def test_progress_default_is_zero(self):
        got = server.get_course_progress()
        self.assertEqual(got["pages_done"], 0)
        self.assertEqual(got["pct"], 0)
        self.assertEqual(got["pages_progress"], {})

    def test_progress_roundtrip(self):
        server.save_course_progress("PageA", {"PageA": {"step_name": "s1"}}, "x=1", 3, 10)
        got = server.get_course_progress()
        self.assertEqual(got["page_slug"], "PageA")
        self.assertEqual(got["pages_done"], 3)
        self.assertEqual(got["pages_total"], 10)
        self.assertEqual(got["pct"], 30)
        self.assertEqual(got["pages_progress"]["PageA"]["step_name"], "s1")
        self.assertEqual(got["editor_content"], "x=1")

    def test_save_code_writes_file(self):
        res, code = server.save_code("MyPage", "print('oi')\n")
        self.assertEqual(code, 200)
        self.assertTrue(res["ok"])
        p = server.SAVED_DIR / "MyPage.py"
        self.assertTrue(p.exists())
        self.assertEqual(p.read_text(encoding="utf-8"), "print('oi')\n")

    def test_save_code_blocks_path_traversal(self):
        res, code = server.save_code("../../etc/passwd", "x = 1")
        self.assertEqual(code, 200)
        files = list(server.SAVED_DIR.glob("*.py"))
        self.assertEqual(len(files), 1)
        self.assertTrue(str(files[0].resolve()).startswith(str(server.SAVED_DIR.resolve())))

    def test_save_code_empty_rejected(self):
        res, code = server.save_code("Page", "   ")
        self.assertEqual(code, 400)
        self.assertFalse(res["ok"])

    def test_tutor_invalid_backend_rejected(self):
        # tutor desconhecido nao deve tentar rodar nenhuma CLI
        res, code = server.run_tutor("inexistente", "ctx", "duvida", "x = 1")
        self.assertEqual(code, 400)
        self.assertFalse(res["ok"])

    def test_tutor_prompt_includes_rules_context_and_code(self):
        prompt = server.build_tutor_prompt("Aula X", "o que e isso?", "y = 2")
        self.assertIn("NUNCA escreva a solucao completa", prompt)  # regra do CLAUDE.md
        self.assertIn("Aula X", prompt)        # contexto
        self.assertIn("y = 2", prompt)         # codigo do aluno
        self.assertIn("o que e isso?", prompt) # pergunta


if __name__ == "__main__":
    unittest.main()

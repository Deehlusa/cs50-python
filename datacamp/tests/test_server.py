# -*- coding: utf-8 -*-
"""Testes (stdlib unittest) das funcoes novas do server.py. Rodar: python3 -m unittest"""
import json
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

    def test_practice_progress_default_empty(self):
        got = server.get_practice_progress()
        self.assertEqual(got["count"], 0)
        self.assertEqual(got["xp"], 0)
        self.assertEqual(got["items"], [])

    def test_practice_progress_roundtrip_and_upsert(self):
        res, code = server.save_practice_progress("functions-n1-greet", 10, "write_code")
        self.assertEqual(code, 200)
        self.assertTrue(res["ok"])
        got = server.get_practice_progress()
        self.assertEqual(got["count"], 1)
        self.assertEqual(got["xp"], 10)
        self.assertEqual(got["items"][0]["exercise_id"], "functions-n1-greet")
        # mesmo id de novo -> upsert (nao duplica, atualiza xp)
        server.save_practice_progress("functions-n1-greet", 30, "write_test")
        got = server.get_practice_progress()
        self.assertEqual(got["count"], 1)
        self.assertEqual(got["xp"], 30)
        self.assertEqual(got["items"][0]["mode"], "write_test")

    def test_practice_progress_missing_id_rejected(self):
        res, code = server.save_practice_progress("", 10, "write_code")
        self.assertEqual(code, 400)
        self.assertFalse(res["ok"])

    def test_practice_progress_persists_code_checkpoint(self):
        # GAP-5: o código que passou é guardado no servidor e volta no GET (sobrevive ao
        # localStorage limpo). Atualiza a cada conclusão (mantém o último código que passou).
        src = "def greet(name):\n    return 'Olá ' + name"
        res, code = server.save_practice_progress("functions-n1-greet", 10, "write_code", src)
        self.assertEqual(code, 200)
        got = server.get_practice_progress()
        item = next(i for i in got["items"] if i["exercise_id"] == "functions-n1-greet")
        self.assertEqual(item["code"], src)
        # nova versão que passou sobrescreve o checkpoint
        src2 = src + "  # refinado"
        server.save_practice_progress("functions-n1-greet", 10, "write_code", src2)
        got2 = server.get_practice_progress()
        item2 = next(i for i in got2["items"] if i["exercise_id"] == "functions-n1-greet")
        self.assertEqual(item2["code"], src2)
        # chamada antiga sem code (compat) num exercício NOVO: aceita string vazia
        res3, code3 = server.save_practice_progress("functions-n2-other", 5, "write_code")
        self.assertEqual(code3, 200)
        got3 = server.get_practice_progress()
        item3 = next(i for i in got3["items"] if i["exercise_id"] == "functions-n2-other")
        self.assertEqual(item3["code"], "")
        # hardening: chamada antiga (3 args, sem code) num exercício que JÁ TEM checkpoint
        # NÃO pode apagar o código salvo (CASE WHEN excluded.code != '').
        server.save_practice_progress("functions-n1-greet", 10, "write_code")
        got4 = server.get_practice_progress()
        item4 = next(i for i in got4["items"] if i["exercise_id"] == "functions-n1-greet")
        self.assertEqual(item4["code"], src2)

    # --- Athena AI Learning OS (agent_runs / SDD §A3) ---
    def test_agent_runs_default_empty(self):
        got = server.get_agent_runs()
        self.assertEqual(got["count"], 0)
        self.assertEqual(got["items"], [])

    def test_agent_run_roundtrip(self):
        res, code = server.record_agent_run(
            "exercise_generator", "gerar nivel 1 cap dict", "agy",
            status="ok", tokens=1200, notes="3 exercicios",
        )
        self.assertEqual(code, 200)
        self.assertTrue(res["ok"])
        self.assertIsInstance(res["id"], int)
        got = server.get_agent_runs()
        self.assertEqual(got["count"], 1)
        item = got["items"][0]
        self.assertEqual(item["agent"], "exercise_generator")
        self.assertEqual(item["provider"], "agy")
        self.assertEqual(item["tokens"], 1200)

    def test_agent_run_missing_agent_rejected(self):
        res, code = server.record_agent_run("", "tarefa", "agy")
        self.assertEqual(code, 400)
        self.assertFalse(res["ok"])

    def test_agent_runs_ordered_newest_first(self):
        server.record_agent_run("a1", "t1", "agy")
        server.record_agent_run("a2", "t2", "subagent")
        got = server.get_agent_runs()
        self.assertEqual(got["count"], 2)
        self.assertEqual(got["items"][0]["agent"], "a2")  # mais recente primeiro

    def test_learner_seeded_on_init(self):
        conn = server.db()
        row = conn.execute("SELECT id, level, xp FROM learner WHERE id=1").fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row["level"], 0)

    def test_plan_has_backlog_and_progress(self):
        plan = server.get_plan()
        n = len(plan["backlog"])
        self.assertEqual(plan["progress"]["total"], n)
        # MVP P0+P1+P2 concluído nesta sessão -> tudo done, sem próximo
        self.assertEqual(plan["progress"]["done"], n)
        self.assertEqual(plan["next"], {})

    def test_content_queue_seeded(self):
        from athena import MVP_BACKLOG
        conn = server.db()
        n = conn.execute("SELECT COUNT(*) c FROM content_queue").fetchone()["c"]
        conn.close()
        self.assertEqual(n, len(MVP_BACKLOG))

    # --- Athena Progress Analyst (#9) + Mastery Tracker (#8) ---
    def test_next_is_first_concept_when_empty(self):
        nxt = server.get_next()
        self.assertEqual(nxt["concept"], "shell_print_vars")
        self.assertEqual(nxt["level"], 0)

    def test_mastery_roundtrip_and_advances_next(self):
        # 3 acertos no 1º conceito -> domina -> próximo conceito muda
        for _ in range(3):
            res, code = server.record_mastery("shell_print_vars", True)
            self.assertEqual(code, 200)
        self.assertTrue(res["mastered"])
        nxt = server.get_next()
        self.assertEqual(nxt["concept"], "types_cast_conditionals")  # avançou um nível

    def test_mastery_wrong_answer_lowers_strength(self):
        server.record_mastery("loops", True)   # sobe
        res, _ = server.record_mastery("loops", False)  # erro derruba
        self.assertLess(res["strength"], 0.34)

    def test_mastery_missing_concept_rejected(self):
        res, code = server.record_mastery("", True)
        self.assertEqual(code, 400)
        self.assertFalse(res["ok"])

    # --- Iteração A: prática real liga ao Mastery Tracker ---
    def test_practice_completion_bumps_mastery_once(self):
        # 1a conclusão de um exercício de funções sobe o domínio de pure_functions
        res, code = server.save_practice_progress("functions-n1-greet", 10, "write_code")
        self.assertEqual(code, 200)
        self.assertEqual(res["mastery_bumped"], "pure_functions")
        m = {i["concept"]: i["strength"] for i in server.get_mastery()["items"]}
        self.assertGreater(m["pure_functions"], 0)
        first = m["pure_functions"]
        # refazer o MESMO exercício não refarma (idempotente)
        res2, _ = server.save_practice_progress("functions-n1-greet", 10, "write_code")
        self.assertIsNone(res2["mastery_bumped"])
        m2 = {i["concept"]: i["strength"] for i in server.get_mastery()["items"]}
        self.assertEqual(m2["pure_functions"], first)

    def test_write_test_bumps_qa_concept(self):
        res, _ = server.save_practice_progress("functions-n3-discount-test", 30, "write_test")
        self.assertEqual(res["mastery_bumped"], "pytest_aaa")

    def test_practice_to_next_end_to_end(self):
        # Fluxo real: concluir prática -> sobe mastery -> /api/next usa o mastery ATUALIZADO.
        self.assertEqual(server.get_next()["concept"], "shell_print_vars")  # começo
        for ex in ("shell-n1-calc-total", "shell-n2-result-type", "shell-n3-safe-divide"):
            server.save_practice_progress(ex, 10, "write_code")
        # 3 conclusões distintas de shell dominam o conceito (curva 0.45 -> ~0.83)
        m = {i["concept"]: i for i in server.get_mastery()["items"]}
        self.assertTrue(m["shell_print_vars"]["mastered"])
        # get_next agora pula o conceito dominado e sugere o seguinte
        self.assertEqual(server.get_next()["concept"], "types_cast_conditionals")

    def test_practice_unknown_prefix_does_not_bump(self):
        # exercício cujo prefixo não mapeia a conceito não mexe no mastery
        res, _ = server.save_practice_progress("zzz-desconhecido-1", 10, "write_code")
        self.assertIsNone(res["mastery_bumped"])
        self.assertEqual(server.get_mastery()["mastered"], 0)

    # --- Spaced repetition: agendar e priorizar revisões vencidas ---
    def test_record_mastery_schedules_next_review(self):
        # toda tentativa agenda a próxima revisão (next_review deixa de ser vazio)
        res, code = server.record_mastery("strings", True)
        self.assertEqual(code, 200)
        self.assertTrue(res["next_review"])
        conn = server.db()
        nr = conn.execute(
            "SELECT next_review FROM mastery WHERE concept=?", ("strings",)
        ).fetchone()["next_review"]
        conn.close()
        self.assertTrue(nr)  # gravado no banco, não só na resposta

    def test_overdue_review_prioritized_in_next(self):
        # domina um conceito; a revisão fica no futuro -> next sugere um conceito NOVO
        for _ in range(3):
            server.record_mastery("loops", True)
        self.assertNotEqual(server.get_next()["concept"], "loops")
        # força a revisão de loops a vencer no passado -> next prioriza a revisão
        conn = server.db()
        conn.execute(
            "UPDATE mastery SET next_review=? WHERE concept=?",
            ("2000-01-01 00:00:00", "loops"),
        )
        conn.commit()
        conn.close()
        nxt = server.get_next()
        self.assertEqual(nxt["concept"], "loops")
        self.assertTrue(nxt.get("review"))

    def test_concept_for_exercise_prefixes(self):
        from athena import concept_for_exercise
        self.assertEqual(concept_for_exercise("loops-for-n1-sum", "write_code"), "loops")
        self.assertEqual(concept_for_exercise("dict-n2-x", "write_code"), "collections")
        self.assertEqual(concept_for_exercise("strings-n1-x", "write_code"), "strings")
        self.assertIsNone(concept_for_exercise("desconhecido-x", "write_code"))

    def test_get_mastery_lists_all_concepts(self):
        got = server.get_mastery()
        self.assertEqual(got["total"], len(server._pedagogy.CONCEPTS))
        self.assertEqual(got["mastered"], 0)
        self.assertEqual(got["items"][0]["concept"], "shell_print_vars")


class AthenaPedagogyTest(unittest.TestCase):
    def test_update_strength_correct_rises_wrong_falls(self):
        from athena import update_strength
        self.assertGreater(update_strength(0.0, True), 0.0)
        self.assertEqual(update_strength(0.8, False), 0.4)
        self.assertLessEqual(update_strength(1.0, True), 1.0)  # clamp

    def test_suggest_next_skips_mastered(self):
        from athena import suggest_next
        nxt = suggest_next({"shell_print_vars": 0.9, "types_cast_conditionals": 0.95})
        self.assertEqual(nxt["concept"], "loops")

    def test_suggest_next_empty_when_all_mastered(self):
        from athena import suggest_next, CONCEPTS
        all_mastered = {c["key"]: 1.0 for c in CONCEPTS}
        self.assertEqual(suggest_next(all_mastered), {})

    def test_concept_for_chapter_dashboard_titles(self):
        from athena import concept_for_chapter
        self.assertEqual(concept_for_chapter("7. Funções"), "pure_functions")
        self.assertEqual(concept_for_chapter("3. Loops"), "loops")
        self.assertEqual(concept_for_chapter("6. Dicionários, sets e tuplas"), "collections")
        self.assertEqual(concept_for_chapter("8. Exceções"), "exceptions")
        self.assertEqual(concept_for_chapter("9. JSON (API testing)"), "files_json_oop")
        self.assertEqual(concept_for_chapter("11. Escrever testes (pytest)"), "pytest_aaa")
        self.assertEqual(concept_for_chapter("1. Tipos e variáveis"), "types_cast_conditionals")
        # write_test em qualquer capítulo reforça a skill de QA
        self.assertEqual(concept_for_chapter("5. Listas", "write_test"), "pytest_aaa")
        self.assertIsNone(concept_for_chapter("Capítulo inexistente"))

    # --- Spaced repetition (funções puras) ---
    def test_review_interval_grows_with_strength(self):
        from athena import review_interval_days, MASTERED
        self.assertEqual(review_interval_days(0.0), 1)          # fraco -> amanhã
        self.assertEqual(review_interval_days(MASTERED), 2)     # acabou de dominar
        self.assertEqual(review_interval_days(1.0), 7)          # domínio pleno -> mais espaçado
        self.assertGreaterEqual(review_interval_days(1.0), review_interval_days(MASTERED))

    def test_is_due(self):
        from athena import is_due
        self.assertFalse(is_due("", "2026-06-27 10:00:00"))                      # sem agendamento
        self.assertTrue(is_due("2026-06-26 10:00:00", "2026-06-27 10:00:00"))    # venceu
        self.assertFalse(is_due("2026-06-28 10:00:00", "2026-06-27 10:00:00"))   # futuro

    def test_pick_review_most_overdue_first(self):
        from athena import pick_review
        rows = [
            {"concept": "a", "label": "A", "strength": 0.9, "next_review": "2021-01-01 00:00:00"},
            {"concept": "b", "label": "B", "strength": 0.9, "next_review": "2020-01-01 00:00:00"},
        ]
        self.assertEqual(pick_review(rows, "2026-06-27 10:00:00")["concept"], "b")
        # nenhuma vencida -> None
        self.assertIsNone(pick_review(
            [{"concept": "a", "next_review": "2099-01-01 00:00:00"}], "2026-06-27 10:00:00"))

    def test_next_action_prioritizes_overdue_review(self):
        from athena import next_action
        rows = [
            {"concept": "shell_print_vars", "label": "Shell", "level": 0,
             "strength": 0.9, "next_review": "2020-01-01 00:00:00"},
            {"concept": "loops", "label": "Loops", "level": 2, "strength": 0.0, "next_review": ""},
        ]
        nxt = next_action(rows, "2026-06-27 10:00:00")
        self.assertEqual(nxt["concept"], "shell_print_vars")
        self.assertTrue(nxt["review"])

    def test_next_action_falls_back_to_new_concept(self):
        from athena import next_action
        rows = [{"concept": "shell_print_vars", "label": "Shell", "level": 0,
                 "strength": 0.9, "next_review": "2099-01-01 00:00:00"}]
        nxt = next_action(rows, "2026-06-27 10:00:00")
        self.assertEqual(nxt["concept"], "types_cast_conditionals")  # próximo não dominado
        self.assertFalse(nxt.get("review", False))


class AthenaAgentsTest(unittest.TestCase):
    def test_registry_has_13_agents(self):
        from athena import AGENTS
        self.assertEqual(len(AGENTS), 13)

    def test_router_routes_heavy_work_to_agy(self):
        from athena import route, Provider
        for work in ("research", "translation", "curation", "content_qa", "content_review"):
            self.assertEqual(route(work), Provider.AGY)

    def test_router_tutor_is_claude_impl_is_subagent(self):
        from athena import route, Provider
        self.assertEqual(route("tutor"), Provider.CLAUDE)
        self.assertEqual(route("implementation"), Provider.SUBAGENT)
        self.assertEqual(route("verification"), Provider.SUBAGENT)

    def test_router_unknown_raises(self):
        from athena import route
        with self.assertRaises(ValueError):
            route("nope")

    def test_heavy_cognition_agents_use_agy(self):
        from athena.agents import heavy_cognition_agents, AGENTS, AGY
        for key in heavy_cognition_agents():
            self.assertEqual(AGENTS[key].provider, AGY)


class AthenaExerciseGenTest(unittest.TestCase):
    def test_coverage_gaps_detects_missing_chapter(self):
        from athena import exercise_generator as gen
        ex = {"_meta": "x", "Cap A": {"exercises": [{"level": 1}, {"level": 2}, {"level": 3}]}}
        chapters = [{"title": "Cap A"}, {"title": "Cap B"}]
        gaps = gen.coverage_gaps(ex, chapters)
        self.assertEqual(len(gaps), 1)
        self.assertEqual(gaps[0]["title"], "Cap B")

    def test_validate_chapter_accepts_good_write_code(self):
        from athena import exercise_generator as gen
        ch = {"title": "T", "exercises": [
            {"id": "t-n1", "level": 1, "mode": "write_code",
             "solution": "def f(n):\n    return [n, n+1]\n",
             "tests": [{"call": "f(1)", "expect": [1, 2]}]},
            {"id": "t-n2", "level": 2, "mode": "write_code",
             "solution": "def g(n):\n    return n*2\n",
             "tests": [{"call": "g(3)", "expect": 6}]},
            {"id": "t-n3", "level": 3, "mode": "write_test",
             "reference_impl": "def h(a, b):\n    return a + b\n",
             "mutants": ["def h(a, b):\n    return a - b\n",
                         "def h(a, b):\n    return a * b\n",
                         "def h(a, b):\n    return a\n"]},
        ]}
        ok, errors, sols = gen.validate_chapter(ch)
        self.assertTrue(ok, errors)
        self.assertEqual(set(sols), {"t-n1", "t-n2"})  # write_test não vai pro sidecar

    def test_validate_chapter_rejects_tuple_return(self):
        from athena import exercise_generator as gen
        ch = {"title": "T", "exercises": [
            {"id": "t-n1", "level": 1, "mode": "write_code",
             "solution": "def f(n):\n    return (n, n)\n",
             "tests": [{"call": "f(1)", "expect": [1, 1]}]},
            {"id": "t-n2", "level": 2, "mode": "write_code",
             "solution": "def g(n):\n    return n\n", "tests": [{"call": "g(1)", "expect": 1}]},
            {"id": "t-n3", "level": 3, "mode": "write_test",
             "reference_impl": "def h(a):\n    return a\n",
             "mutants": ["def h(a):\n    return -a\n", "def h(a):\n    return 0\n", "def h(a):\n    return a+1\n"]},
        ]}
        ok, errors, _ = gen.validate_chapter(ch)
        self.assertFalse(ok)
        self.assertTrue(any("TUPLA" in e for e in errors))

    def test_loops_nested_chapter_was_merged(self):
        # P2-7: o gap "Loops Aninhadas" foi preenchido e está no bundle
        from pathlib import Path
        ex_file = Path(server.__file__).resolve().parent / "futurecoder-patches/frontend/src/exercises_br.json"
        data = json.loads(ex_file.read_text(encoding="utf-8"))
        self.assertIn("Loops Aninhadas", data)
        levels = sorted({e["level"] for e in data["Loops Aninhadas"]["exercises"]})
        self.assertEqual(levels, [1, 2, 3])


class AthenaLibrarianTest(unittest.TestCase):
    def test_recall_ranks_by_term_overlap(self):
        from athena import recall
        entries = [
            {"title": "Modo Foco", "body": "fullscreen esconde distrações", "tags": "ui"},
            {"title": "Roteamento de custo", "body": "agy 0-quota nunca Claude", "tags": "spec custo"},
        ]
        hits = recall("custo agy", entries)
        self.assertEqual(hits[0]["title"], "Roteamento de custo")

    def test_recall_empty_query_returns_nothing(self):
        from athena import recall
        self.assertEqual(recall("", [{"title": "x", "body": "y"}]), [])

    def test_score_title_weighs_more_than_body(self):
        from athena import score
        in_title = score("mastery", {"title": "mastery", "body": "", "tags": ""})
        in_body = score("mastery", {"title": "", "body": "mastery", "tags": ""})
        self.assertGreater(in_title, in_body)


class ServerDashboardMasteryTest(unittest.TestCase):
    """Dashboard /api/grade (record_attempt) alimenta a MESMA curva de mastery da prática."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        server.DB_PATH = Path(self.tmp.name) / "test.db"
        server.SAVED_DIR = Path(self.tmp.name) / "saved_code"
        server.init_db()
        # não chamar agy/rede: força aprovado
        self._orig = server.grade_with_agy
        server.grade_with_agy = lambda ex, code, tp: {"ok": True, "feedback": "ok", "passed": True}

    def tearDown(self):
        server.grade_with_agy = self._orig
        self.tmp.cleanup()

    def _exercise_id_in_chapter(self, like):
        conn = server.db()
        row = conn.execute(
            "SELECT id FROM exercises WHERE chapter LIKE ? ORDER BY id LIMIT 1", (f"%{like}%",)
        ).fetchone()
        conn.close()
        return row["id"] if row else None

    def test_grade_first_pass_bumps_mastery_dashboard(self):
        eid = self._exercise_id_in_chapter("Funções")
        self.assertIsNotNone(eid, "exercício de Funções deve existir no curriculum")
        res, code = server.record_attempt(eid, "def f(): pass", True)
        self.assertEqual(code, 200)
        self.assertTrue(res["passed"])
        self.assertEqual(res.get("mastery_bumped"), "pure_functions")
        m = {i["concept"]: i["strength"] for i in server.get_mastery()["items"]}
        self.assertGreater(m["pure_functions"], 0)

    def test_grade_repeat_does_not_refarm(self):
        eid = self._exercise_id_in_chapter("Funções")
        server.record_attempt(eid, "def f(): pass", True)        # 1ª vez -> bump
        before = {i["concept"]: i["strength"] for i in server.get_mastery()["items"]}["pure_functions"]
        res2, _ = server.record_attempt(eid, "def f(): pass", True)  # já done -> sem bump
        self.assertIsNone(res2.get("mastery_bumped"))
        after = {i["concept"]: i["strength"] for i in server.get_mastery()["items"]}["pure_functions"]
        self.assertEqual(after, before)

    def test_grade_concurrent_double_submit_awards_once(self):
        # 2 submits simultâneos do MESMO exercício: BEGIN IMMEDIATE serializa →
        # só o 1º vê already_done=False, então XP e mastery sobem UMA vez (sem dobro).
        import threading
        eid = self._exercise_id_in_chapter("Funções")
        self.assertIsNotNone(eid)
        results = []
        def submit():
            results.append(server.record_attempt(eid, "def f(): pass", True)[0])
        threads = [threading.Thread(target=submit) for _ in range(2)]
        for t in threads: t.start()
        for t in threads: t.join()
        awarded = [r for r in results if r.get("xp_awarded", 0) > 0]
        bumped = [r for r in results if r.get("mastery_bumped")]
        self.assertEqual(len(awarded), 1, "XP só pode ser premiado uma vez")
        self.assertEqual(len(bumped), 1, "mastery só pode subir uma vez")

    def test_grade_advances_next_consistent_with_practice(self):
        # dashboard e prática movem o MESMO domínio -> /api/next reflete em qualquer superfície
        eid = self._exercise_id_in_chapter("Loops")
        self.assertIsNotNone(eid)
        for _ in range(3):  # 3 aprovações de Loops dominam o conceito
            conn = server.db()
            conn.execute("UPDATE progress SET status='todo' WHERE exercise_id=?", (eid,))
            conn.commit(); conn.close()
            server.record_attempt(eid, "x", True)
        m = {i["concept"]: i for i in server.get_mastery()["items"]}
        self.assertTrue(m["loops"]["mastered"])


class ServerMemoryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        server.DB_PATH = Path(self.tmp.name) / "test.db"
        server.SAVED_DIR = Path(self.tmp.name) / "saved_code"
        server.init_db()

    def tearDown(self):
        self.tmp.cleanup()

    def test_index_and_recall_memory(self):
        res, code = server.index_memory("decision", "Futurecoder é a base",
                                        "UI só em futurecoder-patches, nunca index.html", "alvo spec")
        self.assertEqual(code, 200)
        self.assertIsInstance(res["id"], int)
        got = server.recall_memory("futurecoder alvo")
        self.assertGreaterEqual(got["count"], 1)
        self.assertEqual(got["items"][0]["title"], "Futurecoder é a base")

    def test_index_memory_empty_rejected(self):
        res, code = server.index_memory("decision", "", "", "")
        self.assertEqual(code, 400)
        self.assertFalse(res["ok"])


class ServerEventsTest(unittest.TestCase):
    """Loop 1: instrumentação da tabela `events` (log append-only para badges)."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        server.DB_PATH = Path(self.tmp.name) / "test.db"
        server.init_db()

    def tearDown(self):
        self.tmp.cleanup()

    def test_events_empty_initially(self):
        self.assertEqual(server.get_events()["count"], 0)

    def test_record_mastery_logs_event_with_source(self):
        server.record_mastery("loops", True, source="api")
        ev = server.get_events()["items"]
        self.assertEqual(len(ev), 1)
        self.assertEqual(ev[0]["kind"], "mastery")
        self.assertEqual(ev[0]["ref"], "loops")
        self.assertEqual(ev[0]["source"], "api")
        self.assertIn("strength", ev[0]["payload"])
        self.assertIn("review", ev[0]["payload"])

    def test_practice_logs_practice_and_mastery(self):
        server.save_practice_progress("functions-n1-greet", 10, "write_code")
        kinds = [e["kind"] for e in server.get_events()["items"]]
        self.assertIn("practice", kinds)   # conta toda 1ª conclusão
        self.assertIn("mastery", kinds)    # + bump do conceito mapeado
        m = next(e for e in server.get_events()["items"] if e["kind"] == "mastery")
        self.assertEqual(m["source"], "practice")
        self.assertEqual(m["ref"], "pure_functions")

    def test_practice_idempotent_no_duplicate_events(self):
        server.save_practice_progress("functions-n1-greet", 10, "write_code")
        n1 = server.get_events()["count"]
        server.save_practice_progress("functions-n1-greet", 10, "write_code")  # refazer
        self.assertEqual(server.get_events()["count"], n1)  # nada novo (idempotente)

    def test_practice_unmapped_still_logs_practice_only(self):
        # exercício sem conceito mapeado: emite SÓ o evento practice (sem mastery)
        server.save_practice_progress("zzz-desconhecido-1", 5, "write_code")
        ev = server.get_events()["items"]
        self.assertEqual(len(ev), 1)
        self.assertEqual(ev[0]["kind"], "practice")

    def test_page_event_only_on_increase(self):
        server.save_course_progress("p1", {}, "", 1, 10)
        self.assertEqual(server.get_events()["count"], 1)            # subiu 0->1
        server.save_course_progress("p1", {}, "", 1, 10)            # mesmo done
        self.assertEqual(server.get_events()["count"], 1)            # sem evento novo
        server.save_course_progress("p2", {}, "", 2, 10)            # subiu 1->2
        ev = server.get_events()["items"]
        self.assertEqual(server.get_events()["count"], 2)
        self.assertEqual(ev[0]["kind"], "page")
        self.assertEqual(ev[0]["source"], "course")

    def test_get_events_respects_limit_and_order(self):
        for i in range(3):
            server.record_mastery("loops", True, source="api")
        got = server.get_events(2)
        self.assertEqual(got["count"], 2)                # respeita limit
        self.assertGreater(got["items"][0]["id"], got["items"][1]["id"])  # mais recente 1º


class ServerBadgesTest(unittest.TestCase):
    """Loop 2: MVP de badges persistidos (user_badges + evaluate_badges + /api/badges)."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        server.DB_PATH = Path(self.tmp.name) / "test.db"
        server.init_db()

    def tearDown(self):
        self.tmp.cleanup()

    def test_badge_rules_are_pure(self):
        from athena import badges
        empty = {"rows": [], "strength": {}, "pages_done": 0}
        self.assertEqual(badges.evaluate(empty), [])
        ctx = {"rows": [{"concept": "loops", "strength": 0.9, "level": 2, "mastered": True}],
               "strength": {"loops": 0.9}, "pages_done": 1}
        ids = badges.evaluate(ctx)
        self.assertIn("first_step", ids)      # pages_done>=1
        self.assertIn("first_mastery", ids)   # algum mastered

    def test_badges_empty_initially(self):
        got = server.get_badges()
        self.assertEqual(got["unlocked"], 0)
        self.assertEqual(got["total"], len(server._badges.BADGE_DEFS))

    def test_first_mastery_unlocks_via_record_mastery(self):
        for _ in range(3):
            server.record_mastery("loops", True, source="api")  # domina loops
        got = {b["id"]: b for b in server.get_badges()["items"]}
        self.assertTrue(got["first_mastery"]["unlocked"])
        self.assertTrue(got["first_mastery"]["unlocked_at"])

    def test_first_step_unlocks_via_course_progress(self):
        server.save_course_progress("p1", {}, "", 1, 10)
        got = {b["id"]: b for b in server.get_badges()["items"]}
        self.assertTrue(got["first_step"]["unlocked"])

    def test_qa_and_bughunter_unlock(self):
        # prática de write_test mapeia pytest_aaa -> bug_hunter; e qa_initiate a 50%
        server.record_mastery("pytest_aaa", True, source="practice")  # strength 0.45
        server.record_mastery("pytest_aaa", True, source="practice")  # 0.70 (>=0.5)
        got = {b["id"]: b for b in server.get_badges()["items"]}
        self.assertTrue(got["bug_hunter"]["unlocked"])   # pytest_aaa > 0
        self.assertTrue(got["qa_initiate"]["unlocked"])  # nível>=8 e strength>=0.5

    def test_evaluate_badges_idempotent(self):
        server.record_mastery("loops", True, source="api")
        n1 = server.get_badges()["unlocked"]
        first = server.get_badges()
        at1 = {b["id"]: b["unlocked_at"] for b in first["items"] if b["unlocked"]}
        server.evaluate_badges()  # reavaliar não re-grava nem muda unlocked_at
        second = server.get_badges()
        at2 = {b["id"]: b["unlocked_at"] for b in second["items"] if b["unlocked"]}
        self.assertEqual(server.get_badges()["unlocked"], n1)
        self.assertEqual(at1, at2)  # timestamp preservado (INSERT OR IGNORE)


class ServerSyncRobustnessTest(unittest.TestCase):
    """Melhoria de produto: robustez do fluxo prática→mastery (race + idempotência)."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        server.DB_PATH = Path(self.tmp.name) / "test.db"
        server.init_db()

    def tearDown(self):
        self.tmp.cleanup()

    def test_concurrent_submits_bump_mastery_only_once(self):
        # 2 submits simultâneos do MESMO exercício: BEGIN IMMEDIATE serializa →
        # só 1 sobe mastery, só 1 evento de mastery (corrige a race de double-click).
        import threading
        results = []
        def submit():
            res, _ = server.save_practice_progress("functions-n1-greet", 10, "write_code")
            results.append(res)
        threads = [threading.Thread(target=submit) for _ in range(2)]
        for t in threads: t.start()
        for t in threads: t.join()
        bumped = sum(1 for r in results if r.get("mastery_bumped"))
        self.assertEqual(bumped, 1)
        mastery_events = [e for e in server.get_events()["items"] if e["kind"] == "mastery"]
        self.assertEqual(len(mastery_events), 1)

    def test_transaction_path_still_bumps_and_persists(self):
        # caminho normal (1 submit) com a transação BEGIN IMMEDIATE continua funcionando
        res, code = server.save_practice_progress("functions-n1-greet", 10, "write_code")
        self.assertEqual(code, 200)
        self.assertEqual(res["mastery_bumped"], "pure_functions")
        conn = server.db()
        row = conn.execute("SELECT 1 FROM practice_progress WHERE exercise_id=?",
                           ("functions-n1-greet",)).fetchone()
        conn.close()
        self.assertIsNotNone(row)


class PracticeTrailIntegrityTest(unittest.TestCase):
    """Curadoria: a trilha de prática (exercises_br.json) tem que ficar limpa e coerente.

    Guard de regressão para a classe de bug 'chave órfã' (chave que não casa com
    chapters.json -> capítulo perde a prática) e 'id sem conceito' (prefixo de id que
    não mapeia mastery). Lê os assets do frontend; pula se não estiverem presentes.
    """
    SRC = Path(__file__).resolve().parent.parent / "futurecoder-patches/frontend/src"

    def _load(self, name):
        path = self.SRC / name
        if not path.exists():
            self.skipTest(f"{name} ausente (build do frontend não aplicado)")
        return json.loads(path.read_text(encoding="utf-8"))

    def test_no_orphan_exercise_chapters(self):
        # toda chave de exercises_br.json (menos _meta) tem que casar com um título de chapters.json
        ex = self._load("exercises_br.json")
        chapters = {c["title"] for c in self._load("chapters.json")}
        orphans = [k for k in ex if k != "_meta" and k not in chapters]
        self.assertEqual(orphans, [], f"chaves órfãs sem capítulo: {orphans}")

    def test_loops_exercises_map_to_a_concept(self):
        # todo exercício de prática precisa subir mastery (write_test->pytest_aaa; senão prefixo)
        from athena import pedagogy
        ex = self._load("exercises_br.json")
        blk = ex.get("Loops Aninhadas", {}).get("exercises", [])
        self.assertTrue(blk, "capítulo Loops Aninhadas deve ter exercícios")
        for e in blk:
            concept = pedagogy.concept_for_exercise(e["id"], e.get("mode", ""))
            self.assertIsNotNone(concept, f"{e['id']} não mapeia conceito (sem mastery)")

    def test_early_chapters_have_concept_intro(self):
        # Anti "conceito jogado": capítulos críticos pré-Funções trazem ao menos um
        # 'concept_intro' (🧩 nomeia o conceito antecipado antes do editor, sem dar a solução).
        # Cobre Shell/Strings/Variáveis (sessões anteriores) + Loops For/Instruções If/Listas (GAP-2).
        ex = self._load("exercises_br.json")
        for chap in ("O Shell", "Básicos de Strings", "Variáveis",
                     "Loops For", "Instruções If", "Listas"):
            blk = ex.get(chap, {})
            exs = blk.get("exercises", []) if isinstance(blk, dict) else blk
            self.assertTrue(exs, f"{chap} deve ter exercícios")
            intros = [e for e in exs if (e.get("concept_intro") or "").strip()]
            self.assertTrue(intros, f"{chap} precisa de pelo menos 1 primer (concept_intro)")
        # O primeiríssimo contato (Shell n1) explica a FUNÇÃO (def/return).
        shell1 = ex["O Shell"]["exercises"][0]
        intro = (shell1.get("concept_intro") or "").lower()
        self.assertTrue("função" in intro or "func" in intro or "return" in intro,
                        "Shell n1 deve introduzir o conceito de função (def/return)")

    def test_last_hint_is_not_a_solution_spoiler(self):
        # Regra pedagógica do dono: a dica nunca pode ser a solução pronta. Guard: o ÚLTIMO
        # hint de cada exercício não pode conter uma linha-chave da solução literalmente
        # (return/atribuição/append com conteúdo real). Cobre todos os 12 capítulos.
        import re
        ex = self._load("exercises_br.json")
        try:
            sol = json.loads((self.SRC.parent.parent / "docs/exercises_solutions.json").read_text(encoding="utf-8"))
        except FileNotFoundError:
            sol = {}

        def norm(s):
            return re.sub(r"\s+", " ", s).strip()

        money_re = re.compile(r"\s*(return |[a-zA-Z_][\w\.\[\]]*\s*(=|\+=)|.*\.append\()")
        leaks = []
        for chap, blk in ex.items():
            if chap == "_meta":
                continue
            exs = blk.get("exercises", []) if isinstance(blk, dict) else blk
            for e in exs:
                src = sol.get(e["id"]) or e.get("reference_impl") or ""
                money = [l.strip() for l in src.splitlines()
                         if money_re.match(l) and len(l.strip()) > 8 and not l.strip().startswith("def ")]
                hints = e.get("hints", [])
                if not hints or not money:
                    continue
                last = norm(hints[-1])
                if any(norm(l) in last for l in money):
                    leaks.append(e["id"])
        self.assertEqual(leaks, [], f"último hint entrega a solução (spoiler): {leaks}")


class LearningModeTest(unittest.TestCase):
    """Modo de aprendizado: 'python' (suave, só base) vs 'qa' (puxa QA cedo)."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        server.DB_PATH = Path(self.tmp.name) / "test.db"
        server.init_db()

    def tearDown(self):
        self.tmp.cleanup()

    BASE_TO_BRIDGE = ["shell_print_vars", "types_cast_conditionals", "loops",
                      "strings", "collections", "pure_functions"]

    def _master(self, *concepts):
        for k in concepts:
            for _ in range(3):
                server.record_mastery(k, True)

    # --- perfil ---
    def test_default_mode_is_python(self):
        self.assertEqual(server.get_learner()["mode"], "python")

    def test_set_mode_roundtrip_and_invalid_rejected(self):
        res, code = server.set_learner_mode("qa")
        self.assertEqual(code, 200)
        self.assertEqual(server.get_learner()["mode"], "qa")
        bad, c = server.set_learner_mode("hacker")
        self.assertEqual(c, 400)
        self.assertFalse(bad["ok"])
        self.assertEqual(server.get_learner()["mode"], "qa")  # inalterado

    # --- planner puro (rotas concretas) ---
    def test_python_route_stays_on_base_after_bridge(self):
        from athena import suggest_next
        mastered = {k: 0.9 for k in self.BASE_TO_BRIDGE}
        # python: depois de pure_functions(5) vem exceptions(6), NÃO pytest
        self.assertEqual(suggest_next(mastered, "python")["concept"], "exceptions")

    def test_qa_route_pulls_qa_after_bridge(self):
        from athena import suggest_next
        mastered = {k: 0.9 for k in self.BASE_TO_BRIDGE}
        # qa: dominada a ponte (pure_functions), puxa pytest_aaa(8) ANTES de exceptions(6)
        self.assertEqual(suggest_next(mastered, "qa")["concept"], "pytest_aaa")

    def test_python_mode_never_pushes_qa(self):
        from athena import suggest_next
        all_base = {k: 0.9 for k in
                    ["shell_print_vars", "types_cast_conditionals", "loops", "strings",
                     "collections", "pure_functions", "exceptions", "files_json_oop"]}
        # base inteira dominada no modo python -> nada a sugerir (não empurra QA)
        self.assertEqual(suggest_next(all_base, "python"), {})

    def test_default_arg_equals_python_and_not_more_aggressive(self):
        from athena import suggest_next
        # sem modo == python; e do zero sugere o 1º conceito base (não fica mais agressivo)
        self.assertEqual(suggest_next({}), suggest_next({}, "python"))
        self.assertEqual(suggest_next({})["concept"], "shell_print_vars")

    # --- integração com /api/next via learner.mode ---
    def test_get_next_qa_mode_surfaces_pytest(self):
        self._master(*self.BASE_TO_BRIDGE)
        server.set_learner_mode("qa")
        self.assertEqual(server.get_next()["concept"], "pytest_aaa")

    def test_get_next_python_mode_surfaces_exceptions(self):
        self._master(*self.BASE_TO_BRIDGE)
        server.set_learner_mode("python")
        self.assertEqual(server.get_next()["concept"], "exceptions")


if __name__ == "__main__":
    unittest.main()

# -*- coding: utf-8 -*-
"""Exercise Generator (agente #4, SDD §A2).

Funções puras de apoio à geração de exercícios 3-níveis para o futurecoder:
- coverage_gaps: quais capítulos faltam (ou têm níveis incompletos).
- build_prompt: o prompt PT-BR/QA para o agy gerar no schema exato.
- validate_chapter: NÃO confia no LLM — roda o código em Python e confirma que:
    * write_code: a solução fornecida passa em TODOS os casos {call, expect};
    * write_test: a reference_impl é válida e cada mutante DIFERE dela (é matável).

Cognição pesada (gerar o conteúdo) vai por agy (0-quota), NUNCA Workflow/Agent do Claude.
Este módulo é só o andaime determinístico + validação.
"""
import json
from typing import Dict, List, Tuple


def coverage_gaps(ex_data: Dict, chapters: List[Dict]) -> List[Dict]:
    """Capítulos do futurecoder sem exercícios ou sem os 3 níveis.

    ex_data: conteúdo de exercises_br.json. chapters: chapters.json (lista de {title,...}).
    Retorna [{title, missing_levels}] em ordem do currículo.
    """
    gaps = []
    keys = {k for k in ex_data if k != "_meta"}
    for c in chapters:
        title = c["title"]
        if title not in keys:
            gaps.append({"title": title, "missing_levels": [1, 2, 3]})
            continue
        levels = {e.get("level") for e in ex_data[title].get("exercises", [])}
        missing = [lv for lv in (1, 2, 3) if lv not in levels]
        if missing:
            gaps.append({"title": title, "missing_levels": missing})
    return gaps


def build_prompt(chapter_title: str, concept_hint: str, example_json: str) -> str:
    """Prompt para o agy gerar o capítulo no schema exato (PT-BR + QA, dicas em escada)."""
    return f"""Gere exercícios de prática para o capítulo "{chapter_title}" de um curso de Python
em PT-BR voltado a QA Automation. Conceito do capítulo: {concept_hint}.

REGRAS:
- Exatamente 3 exercícios: N1 (write_code, aquecimento), N2 (write_code, combina com o anterior),
  N3 (write_test, mutation testing — o aluno escreve testes).
- PT-BR na prosa, inglês no código. Cada exercício planta uma semente de QA (edge case / caso negativo).
- write_code DEVE ter um campo extra "solution" (código Python correto) — será usado só para validar e
  removido do bundle (não vaza pro aluno). Os "tests" são [{{"call": "...", "expect": <valor>}}].
- write_test DEVE ter "reference_impl" (correta) e "mutants" (3 impls com bugs plantados, cada uma
  matável por um bom teste) e "min_tests".
- "hints" SEMPRE em escada (sutil → mais claro → quase-esqueleto), NUNCA a solução literal completa.
- ids no padrão "{_id_prefix(chapter_title)}-n1-...", "...-n2-...", "...-n3-...".

Responda APENAS com JSON válido neste formato (sem markdown, sem comentários), espelhando este exemplo:
{example_json}

Gere agora o objeto JSON para "{chapter_title}" (uma única chave de capítulo)."""


def _id_prefix(chapter_title: str) -> str:
    """Prefixo de id sugerido a partir do título (heurística)."""
    t = chapter_title.lower()
    if "aninhad" in t:
        return "loops-nested"
    if "loop" in t:
        return "loops"
    return "".join(ch for ch in t if ch.isalnum())[:10] or "ex"


def _run(code: str, expr: str):
    """Executa `code` num namespace fresco e avalia `expr`. Levanta em erro."""
    ns: Dict = {}
    exec(code, ns)  # conteúdo gerado por nós, validação local
    return eval(expr, ns)


def _has_tuple(value) -> bool:
    """True se value é/contém uma tupla (incompatível com a comparação JSON do runner)."""
    if isinstance(value, tuple):
        return True
    if isinstance(value, list):
        return any(_has_tuple(v) for v in value)
    if isinstance(value, dict):
        return any(_has_tuple(v) for v in value.values())
    return False


def validate_chapter(chapter_obj: Dict) -> Tuple[bool, List[str], Dict[str, str]]:
    """Valida um objeto de capítulo. Retorna (ok, erros, solutions_sidecar).

    solutions_sidecar = {exercise_id: solution_code} a gravar fora do bundle.
    """
    errors: List[str] = []
    solutions: Dict[str, str] = {}
    exs = chapter_obj.get("exercises", [])
    levels = sorted({e.get("level") for e in exs})
    if levels != [1, 2, 3]:
        errors.append(f"níveis presentes {levels}, esperado [1,2,3]")
    for e in exs:
        eid = e.get("id", "?")
        mode = e.get("mode")
        if mode == "write_code":
            sol = e.get("solution")
            if not sol:
                errors.append(f"{eid}: write_code sem 'solution' para validar")
                continue
            for case in e.get("tests", []):
                # Fidelidade ao runner (PyodideRunner.js:76): `actual == expect`, onde expect
                # chega como JSON (arrays/dicts — SEM tuplas). Uma função que retorna tupla
                # falharia contra a lista. Então normalizamos expect como o runner faria e
                # exigimos que o retorno da solução seja JSON-nativo (sem tuplas).
                try:
                    expect_runner = json.loads(json.dumps(case["expect"]))
                except (TypeError, ValueError):
                    errors.append(f"{eid}: expect de {case.get('call')!r} não é JSON-serializável")
                    continue
                try:
                    got = _run(sol, case["call"])
                except Exception as ex:  # noqa
                    errors.append(f"{eid}: erro ao rodar {case.get('call')!r}: {ex}")
                    continue
                if _has_tuple(got):
                    errors.append(f"{eid}: {case['call']} retorna TUPLA — o runner compara contra "
                                  f"array JSON; use list. (got={got!r})")
                elif got != expect_runner:
                    errors.append(f"{eid}: {case['call']} -> {got!r} != {expect_runner!r}")
            solutions[eid] = sol
        elif mode == "write_test":
            ref = e.get("reference_impl", "")
            muts = e.get("mutants", [])
            if not ref or len(muts) < 3:
                errors.append(f"{eid}: write_test precisa de reference_impl + >=3 mutants")
                continue
            # cada mutante deve DIFERIR da referência em ao menos 1 input de sondagem
            fname = _func_name(ref)
            probes = ["(0, 0)", "(1, 2)", "(2, 3)", "(10, 5)", "(3,)", "(0,)", "(5,)"]
            for i, mut in enumerate(muts):
                if not _mutant_is_killable(ref, mut, fname, probes):
                    errors.append(f"{eid}: mutante #{i} indistinguível da referência (não matável)")
        else:
            errors.append(f"{eid}: mode inválido {mode!r}")
    return (len(errors) == 0, errors, solutions)


def _func_name(code: str) -> str:
    import re
    m = re.search(r"def\s+([a-zA-Z_]\w*)\s*\(", code)
    return m.group(1) if m else ""


def _mutant_is_killable(ref: str, mut: str, fname: str, probes: List[str]) -> bool:
    """True se existe ao menos um input onde mutante != referência (ou um levanta e o outro não)."""
    if not fname:
        return False
    for args in probes:
        call = f"{fname}{args}"
        try:
            a = _run(ref, call)
        except Exception:
            a = ("__exc__",)
        try:
            b = _run(mut, call)
        except Exception:
            b = ("__exc__2__",)
        if a != b:
            return True
    return False

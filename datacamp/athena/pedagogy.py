# -*- coding: utf-8 -*-
"""Pedagogy — sequência de conceitos + escolha do próximo (Progress Analyst, SDD §A2 #9).

Funções puras: recebem o estado de mastery e devolvem o próximo conceito. Sem I/O — o
server.py liga isto à tabela `mastery`. Regra do CLAUDE.md: UM conceito por vez.
"""
from typing import Dict, List, Optional

# Sequência canônica dos níveis 0–7 (SDD §B6). (key, label PT-BR, level)
CONCEPTS: List[Dict] = [
    {"key": "shell_print_vars", "label": "Shell, print e variáveis", "level": 0},
    {"key": "types_cast_conditionals", "label": "Tipos, cast e condicionais", "level": 1},
    {"key": "loops", "label": "Loops (for/range/while)", "level": 2},
    {"key": "strings", "label": "Strings (+ regex básico)", "level": 3},
    {"key": "collections", "label": "Listas, dicts, sets, tuplas", "level": 4},
    {"key": "pure_functions", "label": "Funções puras (testáveis)", "level": 5},
    {"key": "exceptions", "label": "Exceções (raise, try/except)", "level": 6},
    {"key": "files_json_oop", "label": "File I/O, JSON e OOP (base do POM)", "level": 7},
    # Trilhas QA em cima (SDD §B6)
    {"key": "pytest_aaa", "label": "pytest: AAA (escrever testes)", "level": 8},
    {"key": "pytest_raises_param", "label": "pytest: raises + parametrize", "level": 9},
    {"key": "api_requests", "label": "API testing com requests (mock local)", "level": 10},
    {"key": "playwright_pom", "label": "Playwright + Page Object Model", "level": 11},
    {"key": "ci_cd", "label": "CI/CD (GitHub Actions)", "level": 12},
]

# Limiar de domínio: strength >= MASTERED => conceito considerado dominado.
MASTERED = 0.8


def _concept(key: str) -> Optional[Dict]:
    return next((c for c in CONCEPTS if c["key"] == key), None)


# Modo de aprendizado: influencia SÓ a ordem de recomendação (não destrói conteúdo).
QA_LEVEL_MIN = 8     # conceitos das trilhas QA começam no nível 8 (pytest+)
_BRIDGE_LEVEL = 5    # pure_functions (nível 5) = ponte natural pra "escrever testes"
VALID_MODES = ("python", "qa")


def _ordered_concepts(mode: str = "python") -> List[Dict]:
    """Ordem de recomendação conforme o modo de aprendizado.

    - **python** (suave): só a BASE (níveis 0–7), em ordem. As trilhas QA NÃO são
      empurradas — quem quer só Python base não leva pytest/playwright na cara.
    - **qa**: base até a PONTE (pure_functions, nível 5) → trilhas QA (8–12) →
      resto da base (6–7). Puxa QA mais cedo (assim que dá pra testar uma função).
    """
    base = [c for c in CONCEPTS if c["level"] <= 7]
    if mode == "qa":
        qa = [c for c in CONCEPTS if c["level"] >= QA_LEVEL_MIN]
        upto_bridge = [c for c in base if c["level"] <= _BRIDGE_LEVEL]
        rest_base = [c for c in base if c["level"] > _BRIDGE_LEVEL]
        return upto_bridge + qa + rest_base
    return base   # python: só a base, ordem natural


def suggest_next(mastery: Dict[str, float], mode: str = "python") -> Dict:
    """Próximo conceito a estudar, dado {concept_key: strength} e o modo do aluno.

    Política (um conceito por vez): o primeiro conceito AINDA não dominado na ordem do
    modo (ver _ordered_concepts). Se todos os do modo já dominados, devolve {} (completo).
    """
    if mode not in VALID_MODES:
        mode = "python"
    for c in _ordered_concepts(mode):
        strength = mastery.get(c["key"], 0.0)
        if strength < MASTERED:
            seen = c["key"] in mastery
            reason = (
                f"Você ainda não começou — comece pelo nível {c['level']}."
                if not seen else
                f"Domínio em {strength:.0%} (< {MASTERED:.0%}); reforce antes de avançar."
            )
            return {"concept": c["key"], "label": c["label"], "level": c["level"],
                    "reason": reason, "mode": mode}
    return {}


# Mapa prefixo-do-exercise_id -> conceito (liga a prática real ao Mastery Tracker).
# Os ids vivem em exercises_br.json (ex.: "functions-n1-greet", "loops-for-n2-...").
_PREFIX_CONCEPT = [
    ("shell-", "shell_print_vars"),
    ("variables-", "shell_print_vars"),
    ("strings-", "strings"),
    ("if-", "types_cast_conditionals"),
    ("bool-", "types_cast_conditionals"),
    ("booleans-", "types_cast_conditionals"),
    ("loops-", "loops"),
    ("lists-", "collections"),
    ("dict-", "collections"),
    ("dictionaries-", "collections"),
    ("func-", "pure_functions"),
    ("functions-", "pure_functions"),
    ("tictactoe-", "pure_functions"),
    ("project-", "files_json_oop"),
]


def concept_for_exercise(exercise_id: str, mode: str = "") -> Optional[str]:
    """Conceito (pedagogy) associado a um exercício de prática.

    write_test sempre reforça a skill-núcleo de QA 'pytest_aaa' (escrever testes). Senão,
    devolve o conceito do tópico pelo prefixo do id. None se não casar.
    """
    if mode == "write_test":
        return "pytest_aaa"
    if not exercise_id:
        return None
    for prefix, concept in _PREFIX_CONCEPT:
        if exercise_id.startswith(prefix):
            return concept
    return None


# Mapa de palavra-chave-no-título-do-capítulo → conceito, para os exercícios do DASHBOARD
# (curriculum.py), cujos capítulos vêm como "N. Nome" (ex.: "7. Funções"). Ordem importa:
# checa do mais específico ao mais genérico.
_CHAPTER_KEYWORDS = [
    ("pytest", "pytest_aaa"),
    ("teste", "pytest_aaa"),
    ("loop", "loops"),               # ANTES de 'oop' — "loops" contém a substring "oop"!
    ("json", "files_json_oop"),
    ("oop", "files_json_oop"),
    ("exce", "exceptions"),          # exceções / excecoes
    ("funç", "pure_functions"),      # funções
    ("func", "pure_functions"),      # funcoes
    ("dicion", "collections"),       # dicionários
    ("set", "collections"),
    ("tupla", "collections"),
    ("lista", "collections"),
    ("string", "strings"),
    ("condicio", "types_cast_conditionals"),
    ("lógic", "types_cast_conditionals"),
    ("logic", "types_cast_conditionals"),
    ("tipo", "types_cast_conditionals"),
    ("variáv", "types_cast_conditionals"),
    ("variav", "types_cast_conditionals"),
]


def concept_for_chapter(chapter_title: str, mode: str = "") -> Optional[str]:
    """Conceito (pedagogy) para um exercício do dashboard, pelo título do capítulo.

    write_test reforça a skill-núcleo de QA 'pytest_aaa'. Senão, casa por palavra-chave no
    título (insensível a maiúsc.). None se não casar — o chamador não mexe no mastery.
    """
    if mode == "write_test":
        return "pytest_aaa"
    t = (chapter_title or "").lower()
    for kw, concept in _CHAPTER_KEYWORDS:
        if kw in t:
            return concept
    return None


def update_strength(current: float, correct: bool) -> float:
    """Atualiza o domínio de um conceito após uma tentativa (curva de aprendizagem simples).

    Acerto sobe rumo a 1.0; erro derruba. Clampa em [0,1]. Determinístico (testável).
    """
    if correct:
        new = current + (1.0 - current) * 0.45   # 3 acertos levam de 0 a ~0.83 (>= MASTERED)
    else:
        new = current * 0.5                       # erro corta o domínio pela metade
    return max(0.0, min(1.0, round(new, 4)))


# ---------------------------------------------------------------------------
# Repetição espaçada (spaced repetition) — fecha o ciclo de aprendizagem.
# Datas como string 'YYYY-MM-DD HH:MM:SS' (mesmo formato de datetime('now','localtime')),
# que comparam lexicograficamente == comparam cronologicamente. Tudo puro/testável.
# ---------------------------------------------------------------------------
def review_interval_days(strength: float) -> int:
    """Dias até a próxima revisão, em função do domínio.

    Quanto mais dominado, mais espaçada a revisão (você lembra melhor → revê mais tarde) —
    curva tipo SM-2 simplificada. Conceito ainda fraco volta amanhã.
    """
    if strength < MASTERED:
        return 1
    span = (strength - MASTERED) / (1.0 - MASTERED)   # 0..1 dentro da faixa já dominada
    return int(round(2 + span * 5))                   # 0.8 → 2 dias ; 1.0 → 7 dias


def is_due(next_review: str, now: str) -> bool:
    """True se há revisão agendada (next_review não-vazio) e já venceu (<= now)."""
    return bool(next_review) and next_review <= now


def pick_review(rows: List[Dict], now: str) -> Optional[Dict]:
    """A revisão MAIS vencida (menor next_review <= now), ou None.

    rows: [{concept, label, level, strength, next_review}] (next_review pode faltar/vazio).
    """
    due = [r for r in rows if is_due(r.get("next_review", ""), now)]
    if not due:
        return None
    r = min(due, key=lambda x: x["next_review"])
    label = r.get("label", "")
    return {
        "concept": r["concept"], "label": label, "level": r.get("level"),
        "strength": r.get("strength", 0.0), "review": True,
        "reason": f"Revisão espaçada vencida — reforce {label} antes de avançar.",
    }


def next_action(rows: List[Dict], now: str, mode: str = "python") -> Dict:
    """Próxima ação do aluno: revisão vencida tem prioridade; senão, conceito novo.

    1. Se há revisão espaçada vencida → devolve-a (spaced repetition fecha o ciclo).
    2. Senão, delega para suggest_next (na ordem do MODO do aluno).
    """
    review = pick_review(rows, now)
    if review:
        return review
    mastery_map = {r["concept"]: r.get("strength", 0.0) for r in rows}
    return suggest_next(mastery_map, mode)

# -*- coding: utf-8 -*-
"""Badges — regras declarativas + avaliador puro (MVP Loop 2, base persistida).

Funções puras: recebem um `ctx` (montado pelo server.py a partir de mastery + course
progress) e devolvem os ids dos badges satisfeitos. Sem I/O — a persistência (tabela
`user_badges`) e a leitura do estado moram no server.py. Os badges são ligados a EVENTOS
REAIS de aprendizagem (domínio de conceito, página concluída), não a contadores cosméticos.

Formato do `ctx` (montado por server._badge_context):
    {
      "rows":     [{"concept","strength","level","mastered"}],  # por conceito
      "strength": {concept: strength},                          # atalho concept->strength
      "pages_done": int,                                        # páginas do curso concluídas
    }
"""
from typing import Dict, List

# (o limiar de domínio vive em pedagogy.MASTERED; aqui as regras recebem `mastered`
#  já calculado no ctx, então não duplicamos a constante.)

# Cada badge: id estável, rótulo PT-BR, ícone, trilha, e um check(ctx) puro.
BADGE_DEFS: List[Dict] = [
    {"id": "first_step", "name": "Primeiro Passo", "icon": "🐣", "track": "python_core",
     "desc": "Concluiu a primeira página do curso.",
     "check": lambda c: c["pages_done"] >= 1},
    {"id": "first_mastery", "name": "Primeiro Domínio", "icon": "⭐", "track": "python_core",
     "desc": "Dominou o primeiro conceito (strength ≥ 80%).",
     "check": lambda c: any(r["mastered"] for r in c["rows"])},
    {"id": "qa_initiate", "name": "QA Iniciado", "icon": "🛡️", "track": "qa",
     "desc": "Chegou a 50% em um conceito da trilha QA (nível ≥ 8).",
     "check": lambda c: any(r["level"] >= 8 and r["strength"] >= 0.5 for r in c["rows"])},
    {"id": "bug_hunter", "name": "Caçador de Bugs", "icon": "🧪", "track": "qa",
     "desc": "Praticou escrever testes (conceito pytest: AAA).",
     "check": lambda c: c["strength"].get("pytest_aaa", 0) > 0},
    {"id": "pipeline_scout", "name": "Batedor de Pipeline", "icon": "⚙️", "track": "cicd",
     "desc": "Começou a trilha de CI/CD (GitHub Actions).",
     "check": lambda c: c["strength"].get("ci_cd", 0) > 0},
]


def evaluate(ctx: Dict) -> List[str]:
    """Ids dos badges cujo `check(ctx)` é verdadeiro. Puro e determinístico."""
    out = []
    for b in BADGE_DEFS:
        try:
            if b["check"](ctx):
                out.append(b["id"])
        except Exception:
            pass  # uma regra com bug não derruba a avaliação das outras
    return out

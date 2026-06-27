# -*- coding: utf-8 -*-
"""Orchestrator (agente #1, SDD §A2) — versão mínima.

Define o backlog MVP (espelha SDD §C3 / LOOP-CONTRACT) como dados puros e oferece o seed
do content_queue. NÃO executa agentes aqui — só descreve o plano. O /loop consome isto.
"""
from typing import Dict, List

# Backlog MVP (SDD §C3). Cada item: prioridade, capítulo/área e tipo de trabalho.
# 'kind' segue as chaves do athena.router (research/implementation/...) p/ roteamento de custo.
MVP_BACKLOG: List[Dict] = [
    {"id": "P0-1", "priority": 0, "chapter": "athena", "kind": "implementation",
     "desc": "Esqueleto athena/ (agents.py + router.py)", "state": "done"},
    {"id": "P0-2", "priority": 0, "chapter": "server", "kind": "implementation",
     "desc": "Migracao SQLite aditiva + /api/agent-run", "state": "done"},
    {"id": "P0-3", "priority": 0, "chapter": "athena", "kind": "implementation",
     "desc": "Orchestrator minimo + /api/plan", "state": "done"},
    {"id": "P1-4", "priority": 1, "chapter": "analytics", "kind": "implementation",
     "desc": "Progress Analyst + /api/next + modulo G (AthenaPanel futurecoder)", "state": "done"},
    {"id": "P1-5", "priority": 1, "chapter": "analytics", "kind": "implementation",
     "desc": "Mastery Tracker (forgetting curve) + modulo H + pratica liga ao mastery", "state": "done"},
    {"id": "P1-6", "priority": 1, "chapter": "futurecoder", "kind": "implementation",
     "desc": "Modulo I: log ao vivo do loop (agent_runs) no AthenaPanel", "state": "done"},
    {"id": "P2-7", "priority": 2, "chapter": "content", "kind": "research",
     "desc": "Exercise Generator (via agy): gerar+validar 'Loops Aninhadas' (gap)", "state": "done"},
    {"id": "P2-8", "priority": 2, "chapter": "athena", "kind": "implementation",
     "desc": "Librarian: memoria SQLite + recall (/api/memory); ruvector vetorial deferido", "state": "done"},
]


def backlog() -> List[Dict]:
    """Devolve o backlog MVP (cópia rasa, para não mutar o módulo)."""
    return [dict(item) for item in MVP_BACKLOG]


def next_todo() -> Dict:
    """Primeiro item ainda 'todo' por prioridade; {} se tudo concluído."""
    pending = [i for i in MVP_BACKLOG if i["state"] != "done"]
    if not pending:
        return {}
    return dict(sorted(pending, key=lambda i: i["priority"])[0])


def progress() -> Dict:
    """Resumo done/total do backlog MVP."""
    done = sum(1 for i in MVP_BACKLOG if i["state"] == "done")
    return {"done": done, "total": len(MVP_BACKLOG)}

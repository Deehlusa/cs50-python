# -*- coding: utf-8 -*-
"""Roteador de cognição (SDD §A4).

Decide, para um tipo de trabalho, QUAL provedor usar — garantindo a regra de ouro da SPEC:
research/tradução/curadoria/QA-de-conteúdo vão por agy (0-quota); Claude só para tutor premium
e implementação/verificação escopada. Função pura, sem efeito colateral (fácil de testar).
"""
from enum import Enum


class Provider(str, Enum):
    AGY = "agy"
    CLAUDE = "claude"
    SUBAGENT = "subagent"
    PYODIDE = "pyodide"
    RUVECTOR = "ruvector"
    SERVER = "server"


# Tipo de trabalho -> provedor. Chaves estáveis usadas pelo Orchestrator/loop.
_ROUTES = {
    "research": Provider.AGY,
    "translation": Provider.AGY,
    "curation": Provider.AGY,
    "content_qa": Provider.AGY,
    "content_review": Provider.AGY,
    "tutor": Provider.CLAUDE,          # premium, sob demanda do aluno
    "implementation": Provider.SUBAGENT,
    "verification": Provider.SUBAGENT,
    "code_execution": Provider.PYODIDE,
    "mutation": Provider.PYODIDE,
    "memory": Provider.RUVECTOR,
    "analytics": Provider.SERVER,
}

# Trabalhos onde usar Workflow/Agent do Claude é PROIBIDO (SPEC: queimou ~2M tokens).
_FORBID_CLAUDE_ORCHESTRATION = {
    "research", "translation", "curation", "content_qa", "content_review",
}


def route(work_type: str) -> Provider:
    """Provedor para o tipo de trabalho. ValueError se desconhecido."""
    try:
        return _ROUTES[work_type]
    except KeyError:
        raise ValueError(f"tipo de trabalho desconhecido: {work_type!r}")


def must_use_agy(work_type: str) -> bool:
    """True se o trabalho é cognição pesada que NÃO pode ir por Claude orchestration."""
    return work_type in _FORBID_CLAUDE_ORCHESTRATION

# -*- coding: utf-8 -*-
"""Athena — AI Learning OS. Camada de agentes (SDD-ai-learning-os.md).

Pacote aditivo: NÃO altera o comportamento atual do server.py. Expõe o registry dos
13 agentes (agents.py) e o roteador de custo (router.py) para serem orquestrados pelo /loop.
"""
from .agents import AGENTS, get_agent
from .router import route, Provider
from .orchestrator import backlog, next_todo, progress, MVP_BACKLOG
from .pedagogy import (
    CONCEPTS, suggest_next, update_strength, MASTERED,
    concept_for_exercise, concept_for_chapter,
    review_interval_days, is_due, pick_review, next_action,
    VALID_MODES,
)
from .librarian import recall, score, tokenize
from .badges import BADGE_DEFS, evaluate as evaluate_badge_rules

__all__ = [
    "AGENTS", "get_agent", "route", "Provider",
    "backlog", "next_todo", "progress", "MVP_BACKLOG",
    "CONCEPTS", "suggest_next", "update_strength", "MASTERED",
    "concept_for_exercise", "concept_for_chapter",
    "review_interval_days", "is_due", "pick_review", "next_action",
    "VALID_MODES",
    "recall", "score", "tokenize",
    "BADGE_DEFS", "evaluate_badge_rules",
]

# -*- coding: utf-8 -*-
"""Librarian / Memory (agente #13, SDD §A2) — recall por palavra-chave.

Versão honesta e funcional: indexa decisões/sessões/conteúdo numa tabela SQLite e recupera
por sobreposição de termos (TF leve + bônus por casar no título). NÃO usa embeddings — o
`ruvector.db` existente não é um SQLite acessível e o CLI `ruvector` está ausente neste host;
o upgrade para busca vetorial fica como infra futura (ver SDD §A2 #13 / §11). As funções de
scoring aqui são PURAS (fáceis de testar); o server.py liga à tabela `memory`.
"""
import re
from typing import Dict, List

_WORD = re.compile(r"[a-zA-Z0-9_áàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ]+", re.UNICODE)
_STOP = {
    "a", "o", "as", "os", "de", "da", "do", "e", "em", "no", "na", "um", "uma",
    "para", "por", "com", "que", "the", "to", "of", "in", "is", "and", "ou",
}


def tokenize(text: str) -> List[str]:
    return [w.lower() for w in _WORD.findall(text or "") if w.lower() not in _STOP and len(w) > 1]


def score(query: str, entry: Dict) -> float:
    """Relevância de uma entrada {title, body, tags} para a query (sobreposição de termos).

    Casar no título e nas tags pesa mais que no corpo.
    """
    q = set(tokenize(query))
    if not q:
        return 0.0
    title = set(tokenize(entry.get("title", "")))
    tags = set(tokenize(entry.get("tags", "")))
    body = set(tokenize(entry.get("body", "")))
    return 3.0 * len(q & title) + 2.0 * len(q & tags) + 1.0 * len(q & body)


def recall(query: str, entries: List[Dict], limit: int = 5) -> List[Dict]:
    """Top-`limit` entradas por score (>0), mais relevantes primeiro."""
    scored = [(score(query, e), e) for e in entries]
    scored = [(s, e) for s, e in scored if s > 0]
    scored.sort(key=lambda t: t[0], reverse=True)
    return [dict(e, _score=s) for s, e in scored[:limit]]

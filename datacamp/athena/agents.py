# -*- coding: utf-8 -*-
"""Registry dos 13 agentes da Athena (SDD §A2).

Estrutura de dados pura (sem efeitos colaterais) descrevendo o time. O Orchestrator (#1)
e o /loop consultam isto para saber, por agente: domínio, papel, provedor de cognição e
done-criteria. Os prompts completos vivem (futuramente) em athena/prompts/<key>.md.
"""
from dataclasses import dataclass, field
from typing import Dict, List


# Domínios (SDD §A2)
PEDAGOGY = "pedagogy"
CONTENT = "content"
ANALYTICS = "analytics"
ORCHESTRATION = "orchestration"

# Provedores de cognição (SDD §A4) — espelha athena.router.Provider
AGY = "agy"            # 0-quota: research, tradução, curadoria, QA de conteúdo
CLAUDE = "claude"      # cota: tutor premium
SUBAGENT = "subagent"  # implementação/verificação escopada
PYODIDE = "pyodide"    # execução de código no browser
RUVECTOR = "ruvector"  # memória/recall
SERVER = "server"      # lógica determinística em server.py


@dataclass(frozen=True)
class Agent:
    key: str
    name: str
    domain: str
    role: str
    provider: str
    done_criteria: str
    inputs: str = ""
    outputs: str = ""


# Ordem = numeração da SDD §A2 (1..13)
AGENTS: Dict[str, Agent] = {a.key: a for a in [
    Agent("orchestrator", "Orchestrator", ORCHESTRATION,
          "Lê a SDD, decompõe em tarefas, agenda os outros 12 no /loop, aplica gates.",
          CLAUDE, "fila vazia ou marco atingido + verificação verde",
          "SDD + LOOP-CONTRACT", "tarefas agendadas em content_queue"),
    Agent("curriculum_architect", "Curriculum Architect", PEDAGOGY,
          "Mantém o índice (níveis 0–7 + trilhas QA/CI) e o grafo de pré-requisitos.",
          AGY, "índice consistente, sem ciclo de pré-requisito",
          "estado do currículo", "índice + grafo de pré-req"),
    Agent("content_curator", "Content Curator", CONTENT,
          "Acha vídeos curtos + fontes GitHub + docs PT por módulo.",
          AGY, "todas as URLs respondem 200 via HTTP (regra durável)",
          "capítulo", "media_br.json entries"),
    Agent("exercise_generator", "Exercise Generator", CONTENT,
          "Gera exercícios 3-níveis (write_code/write_test) por capítulo.",
          AGY, "roda no Pyodide; mutantes 100% matáveis",
          "capítulo + nível", "exercises_br.json entries"),
    Agent("translator", "Translator", CONTENT,
          "Traduz teoria/UI p/ PT-BR preservando <code>.",
          AGY, "JSON válido; 0 ocorrências do inglês-fonte",
          "páginas em inglês", "pt_overrides/*.json"),
    Agent("tutor", "Tutor", PEDAGOGY,
          "Socrático, PT-BR, sem solução pronta, mentalidade QA.",
          CLAUDE, "resposta referencia o código real do aluno",
          "dúvida + código + contexto da aula", "resposta socrática"),
    Agent("assessor", "Assessor", PEDAGOGY,
          "Avalia write_code (asserts) e write_test (mutation score).",
          PYODIDE, "XP só se testes passam na ref e mutation score=100%",
          "código/teste do aluno", "veredito + XP"),
    Agent("mastery_tracker", "Mastery Tracker", ANALYTICS,
          "Modela domínio por conceito (spaced repetition / forgetting curve).",
          SERVER, "tabela mastery atualizada a cada evento",
          "eventos", "mastery por conceito"),
    Agent("progress_analyst", "Progress Analyst", ANALYTICS,
          "Detecta gaps, sugere o próximo conceito (um por vez).",
          SERVER, "/api/next retorna 1 conceito + porquê",
          "mastery + histórico", "próximo conceito"),
    Agent("gamification", "Gamification", ANALYTICS,
          "Badges (raridade), streak, XP, níveis — offline/COEP-safe.",
          SERVER, "badges reativos; contador X/N correto",
          "progresso", "badges + streak + XP"),
    Agent("verifier", "QA/Verifier", ORCHESTRATION,
          "build_ptbr.sh + unittest do server + Playwright cache-bust.",
          SUBAGENT, "build OK, testes verdes, smoke ao vivo",
          "mudança", "veredito de gate"),
    Agent("content_reviewer", "Content Reviewer", CONTENT,
          "Code-review do conteúdo gerado (vazamento de solução, contagem de assert via AST).",
          AGY, "sem solution no bundle; AST limpa",
          "conteúdo gerado", "achados de review"),
    Agent("librarian", "Librarian/Memory", ORCHESTRATION,
          "Indexa decisões/sessões/conteúdo em ruvector.db; recupera prior art.",
          RUVECTOR, "recall relevante rápido; sem duplicar",
          "artefatos", "índice vetorial + recall"),
]}


def get_agent(key: str) -> Agent:
    """Devolve o Agent pela chave; KeyError se não existir."""
    return AGENTS[key]


def agents_by_domain(domain: str) -> List[Agent]:
    return [a for a in AGENTS.values() if a.domain == domain]


def heavy_cognition_agents() -> List[str]:
    """Agentes cuja cognição pesada DEVE ir por agy (nunca Workflow/Agent do Claude)."""
    return [k for k, a in AGENTS.items() if a.provider == AGY]

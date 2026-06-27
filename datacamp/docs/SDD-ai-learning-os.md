# SDD — Athena: AI Learning OS (plataforma de estudo Python orientada a agentes)

> **Spec-Driven Development.** Documento de design master. Define O QUÊ e POR QUÊ antes do código.
> Lidera por **arquitetura + mapa de agentes** (pedido explícito do dono), depois expande os 8 blocos
> e os 6 entregáveis.
>
> - **Data:** 2026-06-26
> - **Autor:** Claude (tech lead autônomo), a pedido do Deehlusa
> - **Status:** PROPOSTA — contrato do `/loop` autônomo. Decisões de stack marcadas "(a confirmar)".
> - **Base de evidência (stack REAL, não inventado):** `datacamp/server.py` (rotas + SQLite),
>   `futurecoder-patches/frontend/src/*` (React+Pyodide), `exercises_br.json` / `media_br.json`,
>   `pt_overrides/`, `ruvector.db`, docs `SDD-curriculo-qa.md` + `SDD-pratica-3-niveis-futurecoder.md`.
> - **Codinome do produto:** **Athena** *(a confirmar com o dono — ver §11 questões abertas)*.

---

## 0. TL;DR (o que esta SDD entrega)

Evoluir o `datacamp/` de "dashboard de estudo + futurecoder em PT-BR" para um **AI Learning OS**:
uma plataforma de aprendizado de Python (nível 0 → avançado) **orientada a agentes**, onde um time
de 13 agentes especializados — dirigido por `/loop` — **cura conteúdo, gera exercícios, traduz,
tutora, avalia, mede progresso e se auto-melhora**, mantendo as regras pedagógicas do `CLAUDE.md`
(um conceito por vez, o aluno digita todo o código, mentalidade de QA desde cedo, PT-BR na prosa).

**Princípio de ouro herdado da SPEC:** cognição pesada (research, tradução, QA de conteúdo) roda por
**`agy` / `deliberation:ask-gemini` (0-quota)**; **nunca** Workflow/Agent do Claude para research
(queimou ~2M tokens); subagente Claude só para implementação bem-escopada.

---

# PARTE A — ARQUITETURA (liderar por aqui)

## A1. Arquitetura funcional (visão de camadas)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  CAMADA DE CONTEÚDO/EXECUÇÃO  (não reinventar — já existe)                │
│  futurecoder (React + Pyodide) servido em /course/ via server.py          │
│  • teoria PT-BR (pt_overrides/pages_br.json, terms_br.json)               │
│  • shell Python ao vivo (Pyodide, COOP/COEP nas rotas /course/*)          │
│  • PracticePanel (3 níveis) + write_code/write_test (mutation testing)    │
└───────────────┬───────────────────────────────────────────────────────────┘
                │  eventos de progresso (practice-updated, page state)
┌───────────────▼───────────────────────────────────────────────────────────┐
│  CAMADA DE APLICAÇÃO  (server.py + SQLite — estender no MVP)               │
│  rotas /api/{track,grade,tutor,course-progress,practice-progress,         │
│             save-code}  +  NOVAS: /api/{plan,next,report,agent-run}        │
│  progress.db: chapters, exercises, progress, course_progress,             │
│               practice_progress  +  NOVAS: learner, mastery, events,      │
│               agent_runs, content_queue                                   │
└───────────────┬───────────────────────────────────────────────────────────┘
                │  chamadas dirigidas por contrato (a SDD) + done-criteria
┌───────────────▼───────────────────────────────────────────────────────────┐
│  CAMADA DE AGENTES  (NOVO — pacote athena/, dirigido por /loop)           │
│  13 agentes (§A2) organizados em 4 domínios:                              │
│  pedagogy · content · analytics · agents(orquestração)                    │
│  Memória/recuperação: ruvector.db (vector store já existe) + SQLite       │
│  Roteamento de cognição: agy(0-quota) → research/tradução/QA;             │
│                          claude -p → tutor premium; subagente → impl.     │
└───────────────────────────────────────────────────────────────────────────┘
```

**Por que esta forma:** mantém a base que já funciona (futurecoder+Pyodide, zero custo, offline),
adiciona inteligência **na borda** (camada de agentes desacoplada) e evita acoplar o produto a um
provedor de IA. O `/loop` é o "kernel" que agenda o time de agentes contra o contrato (esta SDD).

## A2. Arquitetura multi-agente — O MAPA DE AGENTES (13 agentes)

Cada agente tem: **papel**, **entrada → saída**, **provedor de cognição** (custo) e **done-criteria**.
Domínios: **P**edagogy · **C**ontent · **A**nalytics · **O**rquestração.

| # | Agente | Dom | Papel (1 linha) | Provedor | Done-criteria |
|---|--------|-----|------------------|----------|----------------|
| 1 | **Orchestrator** | O | Lê a SDD, decompõe em tarefas, agenda os outros 12 no `/loop`, aplica gates | Claude (loop host) | fila vazia ou marco atingido + verificação verde |
| 2 | **Curriculum Architect** | P | Mantém o índice (níveis 0–7 + trilhas QA/CI) e o grafo de pré-requisitos | agy | índice consistente, sem ciclo de pré-req |
| 3 | **Content Curator** | C | Acha vídeos curtos (Fireship/Indently/TWT) + fontes GitHub + docs PT por módulo | agy + WebFetch | todas as URLs **200 via HTTP** (regra durável) |
| 4 | **Exercise Generator** | C | Gera exercícios 3-níveis (write_code/write_test) por capítulo | agy → gera; subagente → valida | roda no Pyodide; mutantes 100% matáveis |
| 5 | **Translator** | C | Traduz teoria/UI p/ PT-BR preservando `<code>` | bridge gemini (lotes ≤20) | JSON válido; 0 ocorrências do inglês-fonte |
| 6 | **Tutor** | P | Socrático, PT-BR, sem solução pronta, mentalidade QA (regras do CLAUDE.md) | agy (dia a dia) / claude -p (premium) | resposta referencia o código real do aluno |
| 7 | **Assessor** | P | Avalia write_code (asserts) e write_test (mutation score) | Pyodide + agy (qualitativo) | XP só se testes passam na ref **e** score=100% |
| 8 | **Mastery Tracker** | A | Modela domínio por conceito (spaced repetition / forgetting curve) | server.py (lógica) | `mastery` atualizada a cada evento |
| 9 | **Progress Analyst** | A | Detecta gaps, sugere o próximo conceito (um por vez) | server.py + agy | `/api/next` retorna 1 conceito + porquê |
| 10 | **Gamification** | A | Badges (raridade), streak 🔥, XP, níveis — offline/COEP-safe (emoji+CSS) | server.py + frontend | badges reativos; contador X/N correto |
| 11 | **QA/Verifier** | O | Build (`build_ptbr.sh`) + `unittest` do server + Playwright cache-bust | subagente Claude | build OK, testes verdes, smoke ao vivo |
| 12 | **Content Reviewer** | C | Code-review do conteúdo gerado (vazamento de solução, contagem de assert via AST) | agy (review) | sem `solution` no bundle; AST limpa |
| 13 | **Librarian/Memory** | O | Indexa decisões/sessões/conteúdo em `ruvector.db`; recupera prior art | ruvector | recall relevante < N ms; sem duplicar |

**Pipeline canônico do conteúdo (fan-out por capítulo):**
`Curriculum Architect → (Content Curator ∥ Exercise Generator) → Translator → Content Reviewer →
QA/Verifier → Librarian (indexa)`. Pedagogy (Tutor/Assessor) e Analytics rodam **online** (em
resposta ao aluno), não no pipeline de build.

**Anti-padrões proibidos (da SPEC):** usar Workflow/Agent do Claude para o trabalho dos agentes
2,3,5,12 (research/tradução/curadoria/review) — esses são **agy**. Claude só nos agentes 1, 4(validação),
11 (implementação/verificação escopada).

## A3. Modelo de dados (estender o SQLite atual; não quebrar nada)

**Existe hoje** (`progress.db`, ver `server.py:init_db`): `chapters`, `exercises`
(já com `type/predict/hints/video/sources/target_func/reference_impl/mutants/min_tests`),
`progress`, `course_progress`, `practice_progress`. **Regra:** conteúdo é re-semeado a cada boot;
progresso é **preservado**.

**Novas tabelas (MVP, aditivas, `CREATE TABLE IF NOT EXISTS`):**

```sql
CREATE TABLE IF NOT EXISTS learner (        -- single-user no MVP (id=1)
    id INTEGER PRIMARY KEY CHECK (id=1),
    name TEXT, level INTEGER DEFAULT 0, xp INTEGER DEFAULT 0,
    streak_days INTEGER DEFAULT 0, last_active TEXT
);
CREATE TABLE IF NOT EXISTS mastery (        -- domínio por conceito
    concept TEXT PRIMARY KEY,               -- ex.: 'dict', 'pytest.raises'
    strength REAL DEFAULT 0,                -- 0..1 (forgetting curve)
    last_seen TEXT, next_review TEXT, attempts INTEGER DEFAULT 0
);
-- COMPORTAMENTO REAL (implementado): a tabela mastery é populada por AMBAS as superfícies,
-- com a MESMA curva (update_strength: fator 0.45 → 3 acertos ≥ 0.8 = MASTERED; erro corta à metade).
--  (1) PRÁTICA no futurecoder: save_practice_progress detecta a 1ª conclusão (idempotente por
--      exercise_id) → record_mastery; conceito via athena.pedagogy.concept_for_exercise
--      (prefixo-do-id→conceito; write_test→'pytest_aaa').
--  (2) DASHBOARD: record_attempt (/api/grade), na 1ª aprovação (passed and not already_done) →
--      record_mastery; conceito via athena.pedagogy.concept_for_chapter (palavra-chave no título
--      "N. Nome"; write_test→'pytest_aaa'). Bump após fechar a conexão (evita lock).
-- get_next (/api/next) e /api/mastery releem a tabela a cada chamada → domínio único e consistente
-- em qualquer superfície. (Nota: "loops" contém "oop" — o mapa checa 'loop' antes de 'oop'.)
CREATE TABLE IF NOT EXISTS events (         -- telemetria de aprendizagem (local-only)
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT DEFAULT (datetime('now','localtime')),
    kind TEXT,                              -- attempt|done|tutor|page|practice
    ref  TEXT, payload TEXT                 -- JSON
);
CREATE TABLE IF NOT EXISTS agent_runs (     -- auditoria do /loop
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT DEFAULT (datetime('now','localtime')),
    agent TEXT, task TEXT, provider TEXT,   -- agy|claude|pyodide|subagent
    status TEXT, tokens INTEGER, notes TEXT
);
CREATE TABLE IF NOT EXISTS content_queue (  -- backlog de geração de conteúdo
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter TEXT, kind TEXT,                 -- video|exercise|translation
    state TEXT DEFAULT 'todo', priority INTEGER DEFAULT 0
);
```

`ruvector.db` (já existe) = camada vetorial do **Librarian** (memória de decisões/sessões/conteúdo).

## A4. Roteamento de cognição (a regra que controla custo)

| Tipo de trabalho | Rota | Por quê |
|------------------|------|---------|
| Research / curadoria / tradução / QA de conteúdo | **agy** (`deliberation:ask-gemini`) | 0-quota; SPEC manda |
| Tutor premium (sob demanda do aluno) | **claude -p** via `/api/tutor` | já implementado; consome cota |
| Implementação escopada / verificação | **subagente Claude** | escopo fechado, baixo custo |
| Execução de código / mutation / asserts | **Pyodide** (browser) | já roda; 0 instalação |
| Memória / recall | **ruvector.db** | já existe |

---

# PARTE B — OS 8 BLOCOS

## B1. Product vision

**Para** autodidatas de Python (começando pelo dono, mirando QA Automation) **que** não têm dinheiro
para DataCamp, **Athena é** um AI Learning OS local e gratuito **que** ensina Python do zero ao
avançado com um time de agentes que cura, gera, tutora e mede — diferente de cursos estáticos
**porque** o conteúdo se adapta ao aluno (um conceito por vez), o aluno **sempre digita o código**, e
a mentalidade de QA (escrever testes que pegam bugs) é treinada desde cedo via mutation testing.

**Não-objetivos:** não é SaaS multiusuário no MVP; não substitui o tutor humano/IA por solução pronta;
não exige nuvem nem conta paga para rodar.

## B2. Arquitetura funcional
Ver **A1**. Resumo: 3 camadas (conteúdo/execução = futurecoder+Pyodide; aplicação = server.py+SQLite;
agentes = pacote `athena/` dirigido por `/loop`), desacopladas por eventos e contratos.

## B3. Arquitetura multi-agente
Ver **A2** (mapa dos 13 agentes, pipeline, provedores, done-criteria) e **A4** (roteamento de custo).

## B4. Modelo de dados
Ver **A3**. Princípio: **aditivo** (não quebrar o schema atual), conteúdo re-semeado, progresso preservado.

## B5. UX / dashboard (módulos A–J)

> **REGRA DE SUPERFÍCIE (corrigida 2026-06-26):** a "camada superior" (analytics/agentes/dashboard)
> NÃO é um produto separado — ela vive **DENTRO do futurecoder** (`/course/`) como painéis React no
> padrão `LearnMorePanel`/`TutorPanel`, editados em `datacamp/futurecoder-patches/` → `build_ptbr.sh`
> → Playwright. **Nunca** no `index.html` (dashboard legado) nem no `.futurecoder-src/` (clone).
> Os módulos G/H/I já vivem no `AthenaPanel` (`App.js`). O backend (`athena/` + `/api/*` + SQLite) é
> superfície-agnóstico e o futurecoder o consome via `serverSync`.

| Mód | Nome | O que mostra | Estado |
|-----|------|--------------|--------|
| A | **Trilha** | mapa de níveis 0–7 + trilhas QA/CI, com checkpoints (✓/•/–) | existe (parcial) |
| B | **Aula** | teoria PT-BR + shell Pyodide ao vivo | existe (futurecoder) |
| C | **Pratique** | painel 3-níveis (write_code/write_test), dicas em escada | existe |
| D | **Tutor** | painel arrastável, agy/claude, "revisar meu código" | existe |
| E | **Conquistas** | badges com raridade + streak 🔥 + XP/nível | existe |
| F | **Modo Foco** | fullscreen, esconde distrações, Esc sai | existe (bulletproof) |
| G | **Próximo passo** | 1 conceito sugerido + porquê (Progress Analyst) | ✅ AthenaPanel |
| H | **Mastery** | mapa de domínio por conceito (forgetting curve) | ✅ AthenaPanel |
| I | **Sessão autônoma** | log ao vivo do `/loop` (agent_runs) | ✅ AthenaPanel |
| J | **Configurações** | limpar progresso, dev mode | existe |

Princípio de UI durável: **offline/COEP-safe** (sem CDN — emoji + CSS); `dark.scss` só reflete após
`build_ptbr.sh`; testar com cache-bust (`?cb=N`) ou janela anônima.

## B6. Learning system (níveis 0–7 + trilhas)

**Níveis 0–7 (Python core):**
0. Shell/print/variáveis · 1. Tipos+cast+condicionais · 2. Loops (`for`/`range`/`while`) ·
3. Strings (+regex básico) · 4. Listas/dicts/sets/tuplas · 5. **Funções puras** (âncora "testável") ·
6. Exceções (`raise`, `try/except`) · 7. File I/O + JSON + **OOP** (base do POM).

**Trilhas em cima (herdadas da `SDD-curriculo-qa.md`):**
QA-1 pytest (AAA, raises, parametrize, fixtures, cov, mock — tudo "aluno escreve o teste") →
QA-2 API (`requests`, mock local) → QA-3 Playwright+POM (fora do Pyodide) → CI-CD (GitHub Actions).

**Mecânica pedagógica:** um conceito por vez → exercício pequeno → exercício combinando com anterior →
Feynman check; mutation testing mede a skill-núcleo de QA; spaced repetition agenda revisões (`mastery`).

## B7. Roadmap (MVP / V2 / V3 + backlog + riscos + KPIs)

- **MVP (este loop):** SDD + pacote `athena/` (agentes 1,4,7,8,9,11,13) + novas tabelas + rotas
  `/api/{plan,next,report,agent-run}` + módulos G/H/I no dashboard. Stack = **server.py+SQLite**.
- **V2:** FastAPI + Postgres + Redis (fila do `/loop`); multiusuário básico; agentes 2,3,5,12 em
  pipeline agendado; observabilidade leve.
- **V3:** event-driven (mensageria), multiuser real, observabilidade completa, federação de conteúdo.

**Backlog priorizado** → ver **C3**. **Riscos** → §B7-riscos abaixo. **KPIs** → abaixo.

**Riscos:** Pyodide lento com N mutantes (mitigar: 3–5 mutantes, reusar interpretador) · empilhar
conceitos (mitigar: 1 conceito/exercício + Feynman) · cache do bundle (mitigar: `?cb=N`/anônimo) ·
queimar cota Claude (mitigar: roteamento A4) · vazamento de solução no bundle (mitigar: Content Reviewer + AST).

**KPIs:** % conceitos com `mastery.strength ≥ 0.8` · nº exercícios concluídos/semana · streak ·
mutation score médio nos write_test · custo (tokens agy vs claude por `agent_runs`) · URLs 200 no conteúdo.

## B8. Prompt pack dos 13 agentes
Esqueleto reutilizável (7 seções por agente — TASK/OUTCOME/CONTEXT/CONSTRAINTS/MUST/MUST-NOT/OUTPUT),
parametrizado pela linha do agente em **A2**. Os prompts completos serão materializados em
`athena/prompts/<agent>.md` na implementação do MVP (um arquivo por agente), todos herdando:
*PT-BR na prosa; nunca entregar solução pronta; mentalidade QA; respeitar roteamento de custo A4.*

---

# PARTE C — OS 6 ENTREGÁVEIS

## C1. PRD resumido
**Problema:** aprender Python sozinho é caro (DataCamp) e estático. **Usuário:** autodidata mirando QA.
**Solução:** AI Learning OS local/grátis com time de agentes. **Métrica de sucesso:** aluno escreve
testes que pegam bugs sem IA para o código (critério do CLAUDE.md). **Escopo MVP:** §B7. **Fora:** SaaS.

## C2. Blueprint técnico
Ver A1–A4. Entrypoints reais: `python3 datacamp/server.py` → `:8000/course/` (teoria/prática) e `:8000/`
(dashboard). Build: `datacamp/build_ptbr.sh`. Testes: `unittest` em `datacamp/tests/test_server.py`
+ Playwright cache-bust. Memória: `ruvector.db`. Novo código: pacote `datacamp/athena/`.

## C3. Backlog priorizado (MVP)
1. **[P0]** Esqueleto `athena/` + `agents.py` (registry dos 13) + roteamento A4. *(impl: subagente)*
2. **[P0]** Migração SQLite aditiva (tabelas A3) + `/api/agent-run` (grava `agent_runs`).
3. **[P0]** Orchestrator + contrato de `/loop` (lê SDD, fila `content_queue`, gates de QA).
4. **[P1]** Progress Analyst + `/api/next` (1 conceito + porquê) + módulo G.
5. **[P1]** Mastery Tracker (forgetting curve) + tabela `mastery` + módulo H.
6. **[P1]** Módulo I (log ao vivo do loop a partir de `agent_runs`).
7. **[P2]** Exercise Generator em pipeline agy→validação (reusa lógica da sessão 10).
8. **[P2]** Librarian: indexar decisões/sessões no `ruvector.db`.
Cada item: `build_ptbr.sh` OK + `unittest` verde + (se UI) Playwright cache-bust.

## C4. Mapa de agentes
Ver **A2** (tabela dos 13 + pipeline + provedores + done-criteria).

## C5. Jornada de 7 dias (do aluno)
D1 níveis 0–1 (shell, tipos, condicionais) → D2 nível 2 (loops) → D3 nível 3 (strings+regex) →
D4 nível 4 (dict/set) → D5 nível 5 (funções puras = âncora testável) → D6 nível 6 (exceções) +
1º write_test (AAA) → D7 nível 7 (JSON/OOP) + Password Validator (projeto integrador). Tutor socrático
e Próximo-passo guiam um conceito por vez; mastery agenda revisões dos dias anteriores.

## C6. Exemplo de sessão autônoma em loop
```
/loop  (contrato = esta SDD)
  Orchestrator: lê SDD → fila = [migração SQLite, /api/next, módulo G]
  → Verifier(subagente): aplica migração aditiva → unittest verde ✅
  → Progress Analyst(server+agy): implementa /api/next → smoke ✅
  → Frontend(subagente): módulo G no dashboard → build_ptbr.sh OK → Playwright(?cb) ✅
  → Librarian(ruvector): indexa o que mudou
  → Verifier: gate final (build+unittest+smoke) verde → marca item done em content_queue
  done-criteria do loop: fila vazia OU marco MVP atingido → registra no CLAUDE.md (Registro de sessões)
```

---

## §11. Questões abertas (a confirmar com o dono — não bloqueiam o loop)
1. **Nome do produto:** "Athena" (codinome) está OK, ou outro? *(default: seguir com Athena na SDD/código)*
2. **Stack MVP→V2→V3** como em B7? *(default: confirmado pela decisão registrada no /context-save)*
3. **Onde a SDD/impl vivem:** SDD na branch atual (doc, baixo risco); **implementação do loop em worktree
   isolado** `feat/ai-learning-os`. *(default: este plano)*

## §12. Fontes/base
`SDD-curriculo-qa.md`, `SDD-pratica-3-niveis-futurecoder.md`, `IMPL-pratica-3-niveis.md`,
`server.py` (schema+rotas reais), `futurecoder-patches/` (frontend real), `CLAUDE.md` (regras
pedagógicas + sessões 1–11), SPEC-skills-ptbr.md (roteamento de custo agy/Claude).

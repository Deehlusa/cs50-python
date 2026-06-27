# LOOP-CONTRACT — Athena AI Learning OS (contrato do /loop autônomo)

> Este é o **contrato operacional** que o `/loop` executa. A fonte de verdade do DESIGN é
> `SDD-ai-learning-os.md` (mesma pasta). Este arquivo diz **como rodar o loop**: backlog, ordem,
> done-criteria e verificação. Worktree isolado: `feat/ai-learning-os` (não tocar no working dir
> principal `feat/plataforma-refactor`).

## Papel
Você é **tech lead autônomo (Orchestrator, agente #1 da SDD §A2)**. A cada iteração do loop: pegue o
**próximo item P0/P1** do backlog (§C3 da SDD), implemente-o, verifique, e marque concluído. Pare quando
o backlog MVP estiver verde OU quando bater num bloqueio que exige decisão do dono.

## Regras de ouro (NÃO violar)
1. **Roteamento de custo (SDD §A4):** research/tradução/curadoria/QA-de-conteúdo → **agy**
   (`deliberation:ask-gemini`, 0-quota). **NUNCA** Workflow/Agent do Claude para research (queimou ~2M
   tokens). Subagente Claude **só** para implementação bem-escopada e verificação.
2. **Pedagogia (CLAUDE.md):** PT-BR na prosa, inglês no código; nunca entregar solução pronta de
   exercício; um conceito por vez; mentalidade QA.
3. **Aditivo:** não quebrar o schema/rotas atuais. Migrações SQLite com `CREATE TABLE IF NOT EXISTS`.
4. **Nada de commit/push sem o dono pedir.** Trabalhar na árvore; deixar pronto para review.
   Sem trailer `Co-Authored-By` (regra `no-ai-traces-in-git`).
5. **CLAUDE.md é privado/gitignored** — nunca commitar.

## Backlog (ordem de execução — SDD §C3)
- [x] **P0-1** Esqueleto `datacamp/athena/`: `agents.py` (registry dos 13) + `router.py` (roteamento §A4). ✅ 2026-06-26
- [x] **P0-2** Migração SQLite aditiva (tabelas `learner, mastery, events, agent_runs, content_queue` — SDD §A3)
      em `server.py:init_db` + rota `GET/POST /api/agent-run`. ✅ 2026-06-26 (20/20 unittest, smoke HTTP id:1)
- [x] **P0-3** Orchestrator mínimo: lê a SDD/contrato, popula `content_queue`, expõe `GET /api/plan`. ✅ 2026-06-26
- [x] **P1-4** Progress Analyst (`athena/pedagogy.py`) + `GET /api/next` + módulo G (painel futurecoder). ✅ 2026-06-26
- [x] **P1-5** Mastery Tracker (forgetting curve, fator 0.45) + `GET/POST /api/mastery` + módulo H. ✅ 2026-06-26
- [x] **P1-6** Módulo I: log ao vivo do loop lendo `agent_runs`. ✅ 2026-06-26

- [x] **Iteração A** Ligar prática real → Mastery: `save_practice_progress` sobe o domínio na 1ª
      conclusão (mapa prefixo→conceito em `pedagogy.concept_for_exercise`). ✅ 2026-06-26
- [x] **P2-7** Exercise Generator (`athena/exercise_generator.py`): gerou+validou via **agy** o
      capítulo-gap **"Loops Aninhadas"** (3 níveis); validador roda o código (rejeita tupla em
      write_code; prova mutantes matáveis); soluções no sidecar (sem vazar). ✅ 2026-06-26
- [x] **P2-8** Librarian (`athena/librarian.py`): memória SQLite + recall por palavra-chave
      (`GET/POST /api/memory`). Busca **vetorial via ruvector DEFERIDA** (db não-SQLite, CLI ausente). ✅ 2026-06-26

> **🏁 LOOP CONCLUÍDO — MVP P0+P1+P2 + Iteração A.** 42/42 unittest. UI no **futurecoder**
> (`AthenaPanel`), conteúdo gerado por **agy** e validado rodando o código, build OK, bundle confere,
> sem vazar solução. Regra de superfície respeitada (só `futurecoder-patches/`, nunca `.futurecoder-src/`
> nem `index.html`). **NADA commitado** (regra do dono).

- [x] **Iteração B** Mastery unificado: o **dashboard** (`record_attempt`/`/api/grade`) também alimenta
      a MESMA curva de mastery da prática, na 1ª aprovação (`concept_for_chapter`, idempotente). ✅ 2026-06-27
- [x] **Spaced repetition** (`mastery.next_review`): `record_mastery` agenda a próxima revisão
      (`review_interval_days`: domínio↑ → intervalo↑, 0.8→2d/1.0→7d); `get_next` prioriza revisão
      **vencida** (`pick_review`/`next_action`, puros) antes de sugerir conceito novo. Aditivo, sem
      mudar o shape da resposta de `/api/next` → sem rebuild de UI. ✅ 2026-06-27 (55/55 unittest,
      smoke: revisão vencida de `loops` priorizada com `review=true`).

> **Backlog futuro (fora deste loop):** busca vetorial real (ruvector), gerar 3-níveis para capítulos
> com cobertura parcial, tradução de páginas ainda em inglês — tudo via **agy**. Bug-fix durável:
> no mapa de capítulo→conceito, checar `loop` antes de `oop` ("loops" contém "oop"). Datas de mastery
> em string 'YYYY-MM-DD HH:MM:SS' comparam lexicograficamente == cronologicamente (spaced repetition).

## Done-criteria por item (gate de QA — agente #11)
Cada item só conta como concluído se **TODOS** verdes:
1. `python3 datacamp/server.py` sobe sem erro (matar a 8000 antes: `lsof -ti tcp:8000 | xargs kill -9`).
2. `python3 -m unittest discover datacamp/tests` → **verde** (adicionar teste novo para a feature).
3. Se mexeu em UI: `bash datacamp/build_ptbr.sh` OK **e** smoke Playwright com **cache-bust** (`/course/?cb=N`
   ou janela anônima) — senão o bundle velho engana.
4. Roteou cognição pesada para **agy**, não para Claude (registrar provider em `agent_runs`).
5. **Reviewer independente (maker ≠ checker — Osmani, bloco *Sub-agents*).** Antes de marcar DONE,
   despachar um **sub-agent reviewer read-only, SEPARADO de quem fez**, para um passe adversarial que
   **prova de forma independente** (não confia no maker):
   - **conteúdo** (write_code/write_test, `exercises_br.json`) → `.claude/agents/exercise-reviewer`;
   - **código** (`server.py`, `athena/*`, testes) → um reviewer read-only (`ecc:python-reviewer` ou
     equivalente do catálogo) — **só aponta, não edita**.
   O maker **não aprova o próprio trabalho**. Se o reviewer REJEITAR, o maker corrige e o item volta ao
   reviewer. Só conta como DONE com **VEREDITO: APROVADO** registrado na resposta do loop.
6. **Regra anti-"Ralph Wiggum" / asset real (GAP-3).** Quando o requisito usa as palavras
   **REAL / asset / arquivo / incorporado / visível / no bundle**, "inspirado em X", "no estilo de X"
   ou CSS/SVG "que lembra X" **NÃO** cumpre o requisito e **NÃO** pode ser marcado DONE. É obrigatório
   anexar **prova verificável** de que o asset real está no produto, escolhendo a forma adequada:
   - **arquivo binário/imagem** (PNG/font/áudio): `grep` do base64 ou do nome do arquivo no **bundle
     final** (`.futurecoder-src/frontend/course/...`), OU o caminho do arquivo versionado em
     `futurecoder-patches/.../assets/`;
   - **elemento visível na UI**: **screenshot** do elemento renderizado (Playwright), não descrição.
   "Citei/me inspirei/é parecido" é evidência inválida. **Caso de referência:** o loop do **Kenney
   Fantasy UI** foi marcado DONE com borda CSS/SVG "inspirada" sem usar o PNG CC0 real — reincidência
   a evitar. Fechado de fato só quando o PNG CC0 entrou no bundle (`grep` do base64 confirmou) +
   `CREDITS.txt`/`License.txt` versionados.

## Verificação do loop (a cada iteração)
1. Marcar o item no checklist acima.
2. Rodar os **6** gates de done-criteria (incluindo o passe do reviewer independente e a regra anti-"asset citado").
3. Anexar 1 linha de evidência concreta (arquivo:linha ou saída de teste) **+ o VEREDITO do reviewer
   independente** (maker ≠ checker). Sem `APROVADO`, o item NÃO é DONE.
4. Se 2 tentativas falharem no mesmo item → **PARAR** e registrar bloqueio para o dono (não insistir).

## Done-criteria do LOOP inteiro
Backlog P0+P1 verde → registrar entrada no `CLAUDE.md` (Registro de sessões) com evidências e
próximo passo → encerrar o loop. Itens P2 (Exercise Generator, Librarian) ficam para o próximo loop.

## Gotchas duráveis (das sessões 5–11)
- Cache do bundle futurecoder: testar com `?cb=N`/anônimo após `build_ptbr.sh`.
- `dark.scss` só reflete após `build_ptbr.sh` (CSS compilado).
- Matar `server.py` velho na 8000 antes de subir.
- GateGuard bloqueia 1ª escrita/bash destrutivo pedindo "fatos"; retry idêntico passa. O dono deu
  **exceção explícita** ao no-Claude-agents/GateGuard para esta entrega.
- Editar patches em `datacamp/futurecoder-patches/`, **não** no clone `.futurecoder-src/`.

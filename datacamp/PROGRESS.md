# PROGRESS — FutureCoder + Athena (estado vivo do loop)

> **Memória externa do Loop Engineering.** Atualizar ao FIM de cada loop. O próximo loop COMEÇA
> lendo este arquivo + `docs/LOOP-CONTRACT.md` + `CLAUDE.md` — não parte do zero.
> Triagem automática: `python3 datacamp/scripts_ptbr/loop_triage.py`.

## Última entrega verificada
- **2026-06-27 — Asset REAL Kenney integrado no AthenaPanel (moldura, não "inspirado"):**
  Baixado o pack OFICIAL Kenney Fantasy UI Borders (CC0) de kenney.nl; `panel-border-016.png` (48×48)
  copiado p/ `futurecoder-patches/frontend/src/assets/kenney-fantasy-ui-borders/` (+ License.txt do pack
  + CREDITS.txt com pack/arquivo/link/licença). Aplicado como **border-image 9-slice** na moldura
  principal `.athena-float` (`athena-kenney-frame`, slice 16 / border 15px), `borderImageSource` inline
  do PNG importado em App.js.
  - **Evidência (regra do dono = REALMENTE no frontend final):** o **base64 do PNG real** está embarcado
    no bundle `main.831fdf49.js` (CRA inline <10KB como data-URI; grep do fragmento do asset real = 1);
    smoke Playwright — a moldura com cantos entalhados emoldura todo o painel, conteúdo legível, 0 erro
    de console. **Checker independente: APROVADO** (asset real incorporado, licença CC0 registrada,
    escopo só App.js+dark.scss+assets). Build OK.
- **2026-06-27 — Auditoria pedagógica: anti "conceito jogado" (primers nos capítulos iniciais):**
  2 sub-agentes (Pedagogia + QA/Jornada) confirmaram o padrão sistêmico: `def`/`return` em TODA prática
  desde o cap. 0, embora Funções só seja ensinada no cap. 8; métodos (`.lower()`) e cast antes de ensinados.
  Guia de 3 regras (primer nomeia o conceito antecipado, na hora certa, sem virar solução) aplicado via
  novo campo `concept_intro` em `exercises_br.json`, renderizado ENTRE o prompt e o editor
  (`PracticePanel.jsx` + `.practice-concept-intro` no scss). 6 primers nos 3 capítulos críticos
  (O Shell, Básicos de Strings, Variáveis): função/`def`/`return`, `type().__name__`, aspas, `.lower()`, cast.
  - **Evidência:** **83/83 unittest** (+1 guard `test_early_chapters_have_concept_intro`); build
    `main.a0345c82.js` (classe + primer no bundle); smoke Playwright — primers renderizam na ordem
    prompt→intro→editor, visíveis, 0 erro de console. **Checker independente: APROVADO** (nomeia conceito,
    sem spoiler, nada removido, padrão reaplicável). Padrão pronto pra estender a outros capítulos.
- **2026-06-27 — Modo de aprendizado (Python base vs QA) — influencia só a recomendação:**
  Perfil `learner.mode` ('python'|'qa', migração ADITIVA via `ALTER TABLE ... ADD COLUMN`). Planner
  ciente do modo (`pedagogy._ordered_concepts`): **python** = só a base (níveis 0–7), QA não é
  empurrado (suave); **qa** = base até a ponte `pure_functions`(5) → trilhas QA (8–12) → resto da base.
  `get_next` lê o modo; tutor ganha framing por modo. Rotas `GET/POST /api/learner`.
  - **Evidência:** **82/82 unittest** (+8). Demo concreta (mesmo domínio base 0–5): rota PYTHON →
    `exceptions`(6); rota QA → `pytest_aaa`(8). Smoke HTTP: `/api/learner` default python, set qa ok,
    inválido 400. **Checker independente: APROVADO** (python não ficou agressivo; qa puxa QA; aditivo;
    Athena UI intocada; conteúdo íntegro).
  - **Pendência (BLOCO A — UI de onboarding NÃO construída):** o modo é settável via `/api/learner`,
    mas falta a pergunta "qual seu foco?" na 1ª visita. Recomendação: um card único no **#toc (Sumário)**
    na 1ª visita (fora da Athena UI). Aguarda decisão do dono p/ implementar.
- **2026-06-27 — Checkpoint de código na prática (F5 não perde mais o código certo):**
  Diagnóstico (repro ao vivo): o **done-mark já persistia** (localStorage `futurecoder_practice_v1`),
  mas o `ExerciseCard` iniciava o editor sempre do `starter` → no F5 o CÓDIGO que o aluno acertou
  voltava ao inicial (parecia "apagou o progresso"). Fix em `PracticePanel.jsx`: `onDone(ex, code)`
  guarda o código que passou em `progress[id].code`; o editor restaura esse checkpoint no mount;
  novo botão **"🚩 Recuperar meu código que passou"** (classe `.practice-checkpoint`, verde) aparece
  quando o código atual difere do salvo e restaura o checkpoint.
  - **Evidência:** **74/74 unittest**; build `main.64b640d0.js` (classe no JS+CSS); smoke Playwright
    ponta-a-ponta — após F5 o editor restaurou o código salvo (não o starter); ao editar, o botão
    apareceu; clicar restaurou o checkpoint. Persistência = localStorage (consistente com o design;
    server-side fica como melhoria futura). UI só em futurecoder-patches.
- **2026-06-27 — Fix: modo Foco escondia a IDE na página #ide ("Executar não fazia nada"):**
  Causa-raiz (reproduzida ao vivo): `dark.scss` escondia `.ide/.editor-buttons/.full-ide-button/
  .save-code-btn` em `body.focus-mode` — correto nas AULAS (esconder a IDE lateral pra ler), mas na
  página **#ide** a IDE É o conteúdo, então editor+Executar+shell sumiam e rodar parecia não fazer
  nada. Fix: `AppMain` marca `body.route-ide` quando `route==="ide"` (useEffect, cleanup no unmount);
  o CSS do Foco virou `body.focus-mode:not(.route-ide)`.
  - **Evidência:** `print()` roda e mostra saída no #ide (Executar nunca esteve quebrado); **smoke
    Playwright** — ANTES (com fix fora): no Foco+#ide editor/Executar/shell `display:none`; DEPOIS:
    todos `block`, e Executar em Foco mostrou `FOCO_FIX_789` no terminal visível. **Regression:** em
    página de AULA o Foco AINDA esconde a IDE (`none`) e mostra o texto — preservado. **74/74 unittest**
    (sem regressão). build `main.5d9642b3.js` (`route-ide` presente). **Checker independente: APROVADO.**
  - **Nota de ensino (não corrigido — é exercício do aluno):** o código do aluno define `build_username`
    mas NUNCA a chama no topo, então não há saída nem erro — comportamento esperado do Python. Separar
    "definir função" de "chamar função" é a lição. O bug da plataforma (Foco) era real e independente.
  - **/loop:** configurado a 12min (job 4310ccb3) e **cancelado após convergir** (regra: não manter loop
    revalidando item fechado).
- **2026-06-27 — Auditoria de hints dos 12 capítulos (anti-spoiler, problema SISTÊMICO):**
  2 sub-agentes (Pedagogia + QA) confirmaram que **TODO último hint (hint#2) entregava a solução**
  ("Esqueleto: <código>") — 26 com coverage≥0.6, 21 a 100%. **36 últimos-hints reescritos** como nudge
  conceitual (sem linha literal de solução), preservando a escada (último = empurrão forte, mas
  conceitual). Lógica dos exercícios **intocada** (só texto de hint).
  - **Evidência:** **74/74 unittest** (+1 guard permanente `test_last_hint_is_not_a_solution_spoiler`
    que reprova qualquer último hint com linha-chave da solução — cobre os 12 capítulos);
    re-scan objetivo: **0 hints com coverage≥0.6, 0 últimos-hints com money-line**; 40/40 write_code
    ainda passam (lógica intacta); `build_ptbr.sh` OK (`main.7d4a75b3.js`: 0 ocorrências de "Esqueleto:"/
    `return price * quantity`); smoke Playwright `/course/?cb=hints1` — hint de `build_username` agora é
    o nudge ("Guarde a concatenação... aplique o método que deixa minúsculo"), `anySpoiler=false`, 0 erros
    de console. **Checker independente (Explore): APROVADO** (47/47 últimos-hints sem spoiler).
  - **Lição durável:** o gerador de conteúdo (P2-7/agy) criava SEMPRE um último hint "Esqueleto:" com a
    solução — padrão sistêmico, não isolado. O guard de teste agora barra reincidência.
- **2026-06-27 — Curadoria de conteúdo: capítulo "Loops Aninhadas" (resolve a chave órfã):**
  Decisão baseada em evidência (2 sub-agentes: Pedagogia + QA): **MESCLAR** os 2 blocos (ativo 3 +
  órfão 4) num ladder de **4 sem redundância**: L1 `count_cells` (órfão, intro suave) · L2
  `faulty_sensors` (ativo, jagged/QA) · L3 `validate_grid` (órfão, mini-projeto write_code) · L3
  `matrix_overlap` (ativo, write_test). Ids órfãos renomeados `nested-loops-*`→`loops-nested-*`
  (senão `concept_for_exercise`=None → **não subia mastery**). Chave órfã "Loops Aninhados" removida;
  descartados (coordinate-finder, count-matches, sum_diagonal) **arquivados** em
  `docs/exercises_archive.json` (com solução + razão) — nada destruído. Hints que entregavam a
  solução (count_cells, faulty_sensors, validate_grid) reescritos como nudge estrutural.
  - **Evidência:** **73/73 unittest** (+2 guards: `test_no_orphan_exercise_chapters`,
    `test_loops_exercises_map_to_a_concept`); 4 write_code/write_test validados rodando (21 casos, sem
    tupla, mutantes ok); `build_ptbr.sh` OK (bundle `main.64703055.js`: 4/4 ids, 0 solução vazada);
    **12/12 capítulos com prática, 0 órfãs**. **Checker independente (Explore): REPROVOU 1ª vez**
    (hint do count_cells entregava `total += 1`; archive sem `_solution` no write_test) → **corrigido**
    → **2ª passada APROVADO**.
  - **Lições duráveis:** (1) ao iterar CONTEÚDO, rodar `build_ptbr.sh` COMPLETO (passo de cópia
    patches→clone), não `npm build` direto no clone (senão hash não muda). (2) ids de prática PRECISAM
    do prefixo que casa em `_PREFIX_CONCEPT` (`loops-`), senão não há mastery. (3) último hint da escada
    tende a virar a solução — revisar caso a caso.
  - **Pendência sinalizada (fora do escopo deste loop):** outros capítulos podem ter o mesmo padrão
    "último hint = solução completa" — auditar numa próxima curadoria.
- **2026-06-27 — Melhoria TRANSVERSAL do produto (4 frentes, FORA do Athena):**
  1. **Fluxo de estudo:** botões prev/next no `App.js` (`CourseText`) agora mostram o TÍTULO da página
     de destino (`.page-nav-dest`) — navegação deixa de ser cega.
  2. **Conteúdo/orientação:** chaves de `media_br.json` (3) e `exercises_br.json` ("Dictionaries"→
     "Dicionários") casadas com `chapters.json` — desbloqueou "Aprenda mais" e "Pratique" para os 3
     capítulos que estavam no escuro. **Cobertura: 12/12** capítulos com Aprenda mais E com prática.
  3. **UI/UX (fora do Athena):** `PracticePanel.jsx` AUTO-EXPANDE quando há exercício não feito
     (`autoOpen`/`useEffect[chapterTitle]`) — antes ficava colapsado abaixo da dobra.
  4. **QA/refactor:** `record_attempt` (server.py) usa `BEGIN IMMEDIATE` (grade_with_agy FORA da TX)
     → fim do XP/mastery em dobro em double-submit; teste novo `test_grade_concurrent_double_submit_awards_once`.
  - **Evidência:** **71/71 unittest** (+1); `build_ptbr.sh` OK (Node: `--openssl-legacy-provider`);
    smoke Playwright `/course/?cb=prod1` — prev "Combinando Strings"/next "Usando variáveis e print()",
    "🏋️ Pratique 1/3 ▲" auto-aberto, Aprenda mais presente, Athena intacto; único erro de console =
    favicon 404 pré-existente. **Checker independente (Explore read-only): VEREDITO APROVADO**, transversal,
    nenhuma frente dentro do AthenaPanel.
  - **Pendência sinalizada:** chave órfã `"Loops Aninhados"` (4 ex) em `exercises_br.json` não casa com
    nenhum capítulo — NÃO removida (não destruir conteúdo sem decisão do dono).
- **2026-06-27 — Spaced repetition (mastery.next_review):** `record_mastery` agora agenda a próxima
  revisão (intervalo cresce com o domínio: 0.8→2d, 1.0→7d); `/api/next` prioriza revisão **vencida**
  antes de sugerir conceito novo. Funções puras novas em `athena/pedagogy.py`
  (`review_interval_days`/`is_due`/`pick_review`/`next_action`); integração em `server.py`
  (`_mastery_rows`, `get_next`, `record_mastery`).
  - **Evidência:** 55/55 unittest (+7); smoke in-process — domínio de `loops` agenda `next_review`
    2026-06-30 (futuro, ignorado), e ao forçar vencimento `/api/next` devolve `loops` com
    `review=true`; HTTP ao vivo `GET /api/next` serve a nova lógica e o server sobe sem erro.
- **2026-06-27 — Iteração B (mastery unificado):** o dashboard (`/api/grade`/`record_attempt`) passou
  a alimentar a MESMA curva de mastery da prática do FutureCoder, na 1ª aprovação (idempotente, sem
  farm), via `athena.pedagogy.concept_for_chapter`.
  - **Evidência:** 48/48 unittest; demo ao vivo (Playwright) — 4 exercícios gradeados no dashboard via
    `/api/grade` real (agy) → 4 barras a 45% no painel 🦉 Athena do `/course/` (loops, strings,
    collections, pure_functions). Bug pego em teste e corrigido: `"loops"` contém `"oop"` → mapa checa
    `loop` antes de `oop`.
- **2026-06-26 — MVP P0/P1/P2 + Iteração A:** AthenaPanel (módulos G/H/I) no FutureCoder; mastery ligado
  à prática; Exercise Generator (gerou "Loops Aninhadas" via agy, validado rodando o código); Librarian
  (memória SQLite + recall `/api/memory`).

## Próximo alvo (recomendado)
- **Busca vetorial real (ruvector):** hoje o recall do Librarian é por palavra-chave (CLI ausente).
  Avaliar a integração vetorial quando o `ruvector` estiver disponível neste host.

## Backlog aberto (ver LOOP-CONTRACT.md para detalhe)
- [ ] Busca vetorial real (ruvector) — hoje recall é por palavra-chave (CLI ausente) ← próximo
- [ ] Gerar 3-níveis para capítulos com cobertura parcial (via agy)
- [ ] Traduzir páginas ainda em inglês (via agy / bridge gemini)

## Invariantes (não regredir)
- 55/55 unittest verdes (`python3 -m unittest discover -s datacamp/tests`).
- UI só em `futurecoder-patches/` → `build_ptbr.sh` → Playwright `/course/?cb=N`.
- Cognição pesada por **agy** (0-quota), nunca Workflow/Agent do Claude.
- Branch `feat/plataforma-refactor`. **Nada commitado** (aguarda o dono).

# GAPS — /goal e /loop prontos (GAP-1 a GAP-5)

> Origem: **Auditoria de produto 2026-06-27** (PEDIDO vs ENTREGUE). Cada gap abaixo tem um
> `/goal` pronto pra colar (formato completo, com sub-agents e checker) e um `/loop` curto
> (versão rápida). Regras globais valem para TODOS (não repetir em cada um):
>
> **Invariantes de todo loop deste repo** (ver `CLAUDE.md` + `LOOP-CONTRACT.md`):
> - UI **só** em `datacamp/futurecoder-patches/` → `bash datacamp/build_ptbr.sh` → smoke Playwright `/course/?cb=N`.
>   Build precisa de `NODE_OPTIONS=--openssl-legacy-provider` neste host. Rodar o `build_ptbr.sh`
>   COMPLETO (passo de cópia patches→clone), nunca `npm build` direto no clone.
> - Backend: `python3 -m unittest discover datacamp/tests` verde + adicionar teste da feature.
> - **maker ≠ checker:** todo gap fecha com **sub-agent reviewer read-only independente** (APROVADO).
> - Cognição pesada (research/tradução/curadoria) → **agy** (`deliberation:ask-gemini`, 0-quota), nunca Workflow/Agent do Claude.
> - **Nada commitado** sem o dono pedir. Branch `feat/plataforma-refactor`.
> - Migração SQLite só ADITIVA (`CREATE TABLE IF NOT EXISTS` / `ALTER TABLE ADD COLUMN`).
> - **Regra anti-"Ralph Wiggum":** requisito que diz REAL/asset/arquivo/visível exige **prova
>   verificável** (arquivo no bundle, screenshot, teste rodado) — NUNCA "citei/inspirei".
> - Pegar **1 gap por loop**; não auto-continuar pro próximo.

---

## GAP-1 — Modo de aprendizado é invisível ao aluno  ⭐ (prioridade: maior valor/menor esforço)

**Origem:** Loop "Modo de aprendizado (python vs qa)". O motor existe (`learner.mode`, planner,
tutor, `GET/POST /api/learner`), mas **não há UI** pra escolher o foco → só muda via API. Feature
construída, valor entregue ao aluno = 0.

**`/loop` curto:**
```
/loop 15m Fechar GAP-1: adicionar UI de onboarding "Qual seu foco? Python base · QA Automation" no #toc (Sumário) do futurecoder, 1ª visita, que faz POST /api/learner {mode}. Fora da Athena UI. build + smoke Playwright + checker independente.
```

**`/goal` completo:**
```
MODO: FECHAR GAP-1 — ONBOARDING DO MODO DE APRENDIZADO

Contexto:
- O backend do modo (python|qa) já existe: learner.mode + GET/POST /api/learner + planner/tutor cientes do modo.
- Falta a UI: o aluno não tem como escolher o foco. Hoje só muda via API.

Objetivo:
Adicionar um ponto de escolha simples ("Qual seu foco? Python base vs QA Automation")
na 1ª visita, que persista o modo via POST /api/learner, sem tocar a Athena UI nem criar app paralelo.

Regras:
- UI só em futurecoder-patches/ (App.js + dark.scss). NÃO mexer no AthenaPanel.
- Pergunta aparece 1x (1ª visita) e fica re-acessível (ex.: no #toc ou Config), não vira modal chato.
- Persistir a escolha no servidor (POST /api/learner) E localmente (pra não repetir a pergunta).

Sub-agents obrigatórios:
- UI/UX: onde encaixar no #toc sem poluir; copy curta e clara.
- QA/Jornada: validar o fluxo (escolher → persiste → /api/next muda).
- Checker read-only independente. Maker ≠ checker.

Tarefas:
1) Card "Qual seu foco?" no #toc (ou Config) com 2 opções (Python base / QA), 1ª visita.
2) Ao escolher: POST /api/learner {mode}; marcar localStorage pra não perguntar de novo.
3) Refletir a escolha (ex.: chip "Foco: QA" + permitir trocar).
4) build_ptbr.sh + smoke Playwright: escolher QA → /api/next passa a puxar QA; escolher Python → fica na base.
5) Teste (se backend tocado) + checker independente.

Formato: BLOCO A Discovery — B Implementação — C QA/smoke — D Checker — E STATUS
Condição: só parar quando o aluno conseguir escolher o modo pela UI e isso mudar a recomendação, com evidência (smoke) + checker APROVADO.
```
**Esforço:** Pequeno · **Done:** aluno troca o modo pela UI e `/api/next` muda; smoke + checker.

---

## GAP-2 — "Conceito jogado" ainda existe em ~9 dos 12 capítulos

**Origem:** Loop "Auditoria pedagógica / primers". O campo `concept_intro` e o padrão 🧩 já existem,
mas só foram aplicados a Shell/Strings/Variáveis. Loops For, If, Listas etc. ainda jogam
`def`/`return`/métodos/booleanos sem primer.

**`/loop` curto:**
```
/loop 15m Fechar GAP-2: estender o padrão concept_intro (🧩) aos próximos capítulos pré-Funções (Loops For, Instruções If, Listas) em exercises_br.json, introduzindo o conceito antecipado antes do editor, sem virar solução. build + smoke + checker.
```

**`/goal` completo:**
```
MODO: FECHAR GAP-2 — ESTENDER PRIMERS AOS DEMAIS CAPÍTULOS PRÉ-FUNÇÕES

Contexto:
- O campo concept_intro + render no PracticePanel + padrão "🧩 nomeia o conceito, na hora certa, sem solução" já existem (Shell/Strings/Variáveis).
- Falta aplicar aos outros capítulos que antecipam conceitos: Loops For, Instruções If, Listas (e revisar Loops Aninhadas).

Objetivo:
Aplicar o MESMO padrão concept_intro aos capítulos pré-Funções que ainda jogam conceitos sem preparo,
priorizando os de maior fricção, sem reescrever conteúdo nem destruir exercícios.

Regras:
- Só adicionar concept_intro (não remover/alterar lógica de exercício).
- Seguir o guia de 3 regras já criado (nomear o conceito + apontar aprofundamento + nunca a solução).
- Cognição de redação dos primers pode ir por agy se for em lote.

Sub-agents obrigatórios:
- Pedagogia: mapear os conceitos antecipados de Loops For / If / Listas e redigir/validar os primers.
- QA/Validação: confirmar que nenhum primer entrega a solução e que o build mostra os primers.
- Checker read-only independente. Maker ≠ checker.

Tarefas:
1) Mapear conceitos antecipados por exercício nesses capítulos (acumulador, .rstrip()/.zfill(), or/and, len(), índice).
2) Escrever concept_intro no padrão 🧩 onde há antecipação real.
3) Atualizar/estender o guard test (test_early_chapters_have_concept_intro) p/ cobrir os novos capítulos.
4) build_ptbr.sh + smoke Playwright (primers renderizam prompt→intro→editor).
5) Checker independente.

Formato: BLOCO A Mapa — B Primers aplicados — C QA — D Checker — E STATUS
Condição: parar quando os capítulos-alvo tiverem primers (sem spoiler), guard test verde e checker APROVADO.
```
**Esforço:** Pequeno-Médio · **Done:** primers nos capítulos-alvo + guard test + checker.

---

## GAP-3 — Kenney (FECHADO) → endurecer a regra anti-"asset citado"

**Origem:** Loop "RPG-lite Athena + Kenney". Era o caso-âncora de "Ralph Wiggum" (DONE com CSS/SVG
"inspirado", requisito de asset real não cumprido). **Já fechado** (PNG CC0 real no bundle). Resta só
transformar a lição em regra durável.

**`/loop` curto:**
```
/loop Fechar GAP-3: registrar no LOOP-CONTRACT.md a regra "requisito que diz REAL/asset/arquivo/visível exige prova no bundle (grep do base64/arquivo) ou screenshot, nunca citação". Sem código de produto.
```

**`/goal` completo:**
```
MODO: FECHAR GAP-3 — REGRA DURÁVEL "ASSET REAL = PROVA, NÃO CITAÇÃO"

Contexto:
- O loop do Kenney mostrou que "inspirado em X" foi marcado DONE sem usar o asset real.
- O gap técnico já foi fechado; falta a regra que impede a reincidência.

Objetivo:
Adicionar ao done-criteria do LOOP-CONTRACT.md (e à skill athena) a regra de verificação para
requisitos de "asset/arquivo/real/visível".

Regras:
- Só docs (LOOP-CONTRACT.md / skill athena). Nenhum código de produto.
- Preservar as decisões já registradas (não sobrescrever).

Tarefas:
1) No done-criteria, acrescentar: requisito com palavra REAL/asset/arquivo/incorporado exige prova
   verificável — grep do base64/arquivo no bundle final OU screenshot do elemento — anexada na evidência.
2) Registrar o exemplo Kenney como caso de referência.
Formato: BLOCO A Onde — B Regra adicionada — C STATUS
Condição: parar quando a regra estiver no LOOP-CONTRACT.md preservando o conteúdo anterior.
```
**Esforço:** Trivial (doc) · **Done:** regra no LOOP-CONTRACT.md.

---

## GAP-4 — Nada commitado (13+ loops na branch)

**Origem:** Transversal (todos os loops). Trabalho verificado vive só em `feat/plataforma-refactor`,
working tree. Em termos de produto, nada foi "shipado". É decisão do dono (regra "nada sem pedir").

**`/loop` curto:**
```
/loop Fechar GAP-4: propor (NÃO executar) plano de commits limpos agrupados por tema do trabalho não-commitado. Mostrar mensagens + arquivos por commit. Aguardar autorização explícita antes de qualquer git add/commit.
```

**`/goal` completo:**
```
MODO: FECHAR GAP-4 — PLANO DE COMMITS LIMPOS (SEM COMMITAR)

Contexto:
- 13+ loops de trabalho verificado estão sem commit na branch feat/plataforma-refactor.
- Regra do dono: nada commitado sem pedido explícito; sem rastro de IA (sem Co-Authored-By); CLAUDE.md nunca commitado.

Objetivo:
Produzir um plano de commits limpos agrupados por tema, com título + bullets + lista de arquivos por commit,
SEM executar git add/commit/push.

Regras:
- NÃO rodar git add/commit/push. Só ler (git status/diff --stat) e propor.
- Sem trailer de IA. Não commitar CLAUDE.md nem arquivos gitignored.
- Confirmar que .claude/ (agents/skills) deve ou não entrar — decisão do dono (recomendar gitignore).

Tarefas:
1) git status/diff --stat: mapear o que mudou.
2) Agrupar por tema (ex.: backend athena/modo; UI prática/checkpoint/primers; conteúdo hints/loops; asset Kenney; docs).
3) Para cada commit: título curto + bullets + arquivos.
4) Checklist de segurança (testes verdes, nada sensível, .gitignore cobre o privado).
Formato: BLOCO A Estado — B Plano de commits — C Checklist — D STATUS
Condição: parar quando houver um plano de commits claro e o checklist de segurança; commitar só após o dono autorizar.
```
**Esforço:** Pequeno (sob OK do dono) · **Done:** plano de commits + checklist; commit só com autorização.

---

## GAP-5 — Checkpoint de código só em localStorage

**Origem:** Loop "Checkpoint de código (F5)". O código que passou é salvo só no navegador; some se
limpar os dados. Já existe `/api/save-code` (#ide) e `practice_progress` no SQLite — não usados p/ o código da prática.

**`/loop` curto:**
```
/loop 15m Fechar GAP-5: persistir no servidor o código que passou na prática (estender practice_progress com coluna code, aditivo, ou reusar /api/save-code), com restauro no mount. Teste + smoke + checker.
```

**`/goal` completo:**
```
MODO: FECHAR GAP-5 — PERSISTIR O CHECKPOINT DE CÓDIGO NO SERVIDOR

Contexto:
- O checkpoint do código que passou hoje vive só em localStorage (some se limpar o navegador).
- Existe practice_progress (SQLite) e /api/save-code; nenhum guarda o código da prática.

Objetivo:
Persistir o código que passou também no servidor, de forma aditiva, mantendo o localStorage como
camada rápida, sem mudar o fluxo atual de done/XP.

Regras:
- Migração SQLite ADITIVA (ALTER TABLE practice_progress ADD COLUMN code, ou tabela nova).
- Não mudar a lógica de mastery/XP. UI só em futurecoder-patches.

Sub-agents obrigatórios:
- QA/Jornada: validar salvar→limpar localStorage→recuperar do servidor.
- Checker read-only independente. Maker ≠ checker.

Tarefas:
1) Migração aditiva p/ guardar o code por exercise_id no servidor.
2) savePracticeProgress envia o code; novo GET recupera; PracticePanel hidrata do servidor se localStorage vazio.
3) Teste do roundtrip (server) + build + smoke Playwright (F5 com localStorage limpo restaura do servidor).
4) Checker independente.
Formato: BLOCO A Discovery — B Implementação — C QA — D Checker — E STATUS
Condição: parar quando o código que passou sobreviver à limpeza do localStorage (vem do servidor), com teste + smoke + checker APROVADO.
```
**Esforço:** Médio · **Done:** código sobrevive a limpar o navegador (vem do servidor) + teste + checker.

---

## Ordem recomendada (artigo "Loops": prove 1 run, custo por mudança aceita)
1. **GAP-1** (menor esforço, destrava valor já construído) →
2. **GAP-3** (trivial, vira regra anti-reincidência) →
3. **GAP-2** (estende padrão pronto) →
4. **GAP-5** (médio) →
5. **GAP-4** (quando o dono quiser shipar).

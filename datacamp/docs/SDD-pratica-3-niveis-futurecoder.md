# SDD — Prática de 3 Níveis dentro do futurecoder (formato "30 Days of Python", PT-BR + QA)

> **Spec-Driven Development.** Documento de design. Define O QUÊ e POR QUÊ antes do código.
> Nada aqui foi implementado ainda — é a base para planejar (writing-plans) e executar.
>
> - **Data:** 2026-06-25
> - **Autor:** Claude (tutor/eng), a pedido do Deehlusa (André)
> - **Status:** PROPOSTA — design aprovado no brainstorm; aguarda revisão do aluno deste arquivo
> - **Estende:** [`SDD-curriculo-qa.md`](./SDD-curriculo-qa.md) (currículo QA em 5 fases + engine de mutation)
> - **Origem:** brainstorm 2026-06-25 (skill `superpowers:brainstorming`)
> - **Lei de execução:** `SPEC-skills-ptbr.md` (Second Brain) — rota **0-quota** para cognição pesada.

---

## 1. Objetivo

Transformar o **futurecoder** (servido em `/course/`) numa plataforma de **auto-aprendizado /
autodidata** mais forte, trazendo o que o repositório **"30 Days of Python" (Asabeneh)** tem de
melhor — **volume de exercícios graduados em 3 níveis de dificuldade** — só que:

- **PT-BR** (o aluno tem inglês B2; o 30 Days é em inglês),
- **alinhado a QA Automation** (cada exercício planta uma semente de teste/edge case),
- **aditivo** (não remove nem reordena o que já existe; respeita a decisão de 24/06 da SDD anterior),
- **unificado dentro do futurecoder** (uma plataforma só, ao lado da teoria e do shell).

Isso ataca o **gap diagnosticado** no `CLAUDE.md`: *"não é falta de lógica, é falta de
quilometragem."* Os 3 níveis dão a quilometragem; o framing QA prepara a Fase 2 (pytest).

### Decisão de produto (brainstorm 2026-06-25)
- **Abordagem escolhida:** **C + pitada de B** — adotar o **formato** de 3 níveis como molde do
  currículo PT-BR/QA (conteúdo próprio), **semeando** com exercícios concretos adaptados do 30 Days
  onde fizer sentido. (Rejeitadas: A = reestruturar tudo em "30 dias com streak", maior esforço e
  conflita com decisões travadas; B puro = só importar/traduzir, menos sob medida.)
- **Casa dos exercícios:** **tudo no futurecoder** (`/course/`), não no dashboard separado.
- **Nada está cravado** — há liberdade para ajustar a SDD anterior onde for coerente.

---

## 2. Restrições (do `CLAUDE.md`, da SDD anterior e da SPEC)

- **Free / 0-quota / local:** roda local; **cognição pesada via `agy`/`deliberation`** (Gemini),
  Claude só quando premium. **NUNCA** Workflow/Agent do Claude para research/tradução (SPEC linha 41,
  queimou ~2M tokens). Ver §8.
- **PT-BR** na prosa; **inglês** em código e nomes de variáveis (padrão de mercado).
- **Um conceito por vez** — o aluno se sobrecarrega com teoria empilhada. Os 3 níveis são a forma
  concreta disso: N1 isola 1 conceito, N2 combina com o anterior, N3 aplica e quebra.
- **O aluno digita TODO o código.** A plataforma valida e dá **dicas em escada**; **nunca entrega a
  solução**. (Reconciliação com a persona "Professor Elena Vasquez": adota-se o **espírito** —
  Socrático, QA-first, roadmap vivo, desafios — mas **mantém-se "o aluno digita"**; a plataforma não
  cospe código pronto + teste como a persona genérica sugeria.)
- **Mentalidade de quebrar o código** (edge cases, casos negativos) desde o começo.
- **Não reinventar / não tocar no motor gerado:** editar **só** em
  `datacamp/futurecoder-patches/` (fonte de verdade) → `datacamp/build_ptbr.sh` → verificar com
  Playwright. **Nunca** editar o clone `.futurecoder-src/` (gitignored, sobrescrito pelo build).
- **Sem rastros de IA no git** (sem trailer `Co-Authored-By`); não commitar `CLAUDE.md`.

---

## 3. Estado atual relevante (o que já existe)

| Peça | Onde | O que já faz |
|------|------|--------------|
| **futurecoder PT-BR** | `/course/` (React+Pyodide) | Teoria + shell Python ao vivo. Capítulos → páginas → passos. **Pyodide já carregado** (shell). |
| **Painel "📚 Aprenda mais"** | `futurecoder-patches/frontend/src/App.js` + `media_br.json` | Por capítulo (keyed via `chapters.json`): vídeo + fontes + mini-projeto. **Prova o padrão** de painel React próprio lendo JSON. |
| **XP + Conquistas** | `App.js` + `dark.scss` | Pill "⚡ Nível N · XX XP" na navbar + popup 🏆 com 6 badges, computado do progresso (`pages_progress`). |
| **serverSync / progresso** | `book/serverSync.js`, `server.py` (SQLite) | Espelha progresso no SQLite (sem login; localforage + Firebase off). |
| **Engine de mutation (plano)** | `SDD-curriculo-qa.md` §5 | "Aluno escreve o teste" avaliado por mutantes no Pyodide. **Reusado aqui** no Nível 3 QA. |

**Conclusão:** o padrão "painel React próprio + JSON + Pyodide + XP" já está validado (2x). A
prática de 3 níveis é **mais um painel desses**, não um motor novo.

---

## 4. Arquitetura

### 4.1 Visão (baixo risco, segue o padrão já validado)
- Um painel **"🏋️ Pratique"** por capítulo, renderizado no mesmo ponto do "📚 Aprenda mais"
  (em `App.js`, keyed por capítulo via `chapters.json`).
- Conteúdo num arquivo novo **`exercises_br.json`** (mesmo padrão de `media_br.json`).
- **Runner no Pyodide** já presente: executa o código do aluno e mostra ✅/❌ por caso.
- Integra no **XP existente** (cada nível concluído soma XP; nova badge "🏋️ Praticante").
- **Não tocar** no motor gerado do futurecoder (passos compilados de Python). Tudo via patches.

### 4.2 Componentes (frontend, em `futurecoder-patches/frontend/src/`)
| Arquivo | Papel |
|---------|-------|
| `components/PracticePanel.jsx` **(novo)** | UI do painel: lista os 3 níveis do capítulo atual, abre cada exercício, mostra editor + botão "▶ Rodar", feedback e dicas em escada. |
| `components/PyodideRunner.js` **(novo)** | Contrato de execução no Pyodide (ver §6). **Investigar reuso** do worker Pyodide que o shell já usa, em vez de subir uma 2ª instância (decisão de implementação; usar `codegraph`/Read no build). |
| `exercises_br.json` **(novo)** | Banco de exercícios por capítulo (schema §5). |
| `App.js` **(editar)** | Montar `<PracticePanel chapter={...}/>` ao lado do "Aprenda mais". |
| `css/dark.scss` **(editar)** | Estilo do painel, badges de nível (N1/N2/N3), estados ✅/❌, área de dica. **Lembrete:** só reflete após `build_ptbr.sh`. |
| `book/serverSync.js` **(editar, leve)** | Persistir conclusão de exercícios (chave `practice_progress`) no espelho SQLite. |

### 4.3 Backend (`datacamp/server.py`) — mínimo
- A avaliação roda **no cliente (Pyodide)**, como hoje. O servidor só **persiste** o progresso de
  prática (espelho SQLite) e, **opcionalmente**, expõe o tutor qualitativo já existente
  (`/api/tutor`, shell-out para `agy`) para "Pedir dica ao tutor" — **revisor**, nunca árbitro,
  nunca entrega solução.

---

## 5. Schema de dados — `exercises_br.json`

Keyed pelo **slug do capítulo** (igual ao `chapters.json`). Dois **modos** de exercício convivem:
`write_code` (aluno escreve a função) e `write_test` (aluno escreve o teste, avaliado por mutantes).

```json
{
  "_meta": "Exercícios de prática por capítulo do futurecoder. 3 níveis. PT-BR + QA. Conteúdo gerado/curado via agy (0-quota) e revisado.",
  "functions": {
    "chapter_title": "Funções",
    "exercises": [
      {
        "id": "func-n1-greet",
        "level": 1,
        "mode": "write_code",
        "title": "Sua primeira função pura",
        "concept": "def + return (sem print/input dentro)",
        "prompt": "Escreva greet(name) que RETORNA 'Olá, <name>!' (não use print).",
        "starter": "def greet(name):\n    ...",
        "tests": [
          {"call": "greet('Ana')", "expect": "Olá, Ana!"},
          {"call": "greet('')", "expect": "Olá, !"}
        ],
        "hints": [
          "Função pura: o resultado sai pelo return, não pelo print.",
          "f-string ajuda: f\"Olá, {name}!\".",
          "def greet(name):\\n    return f\"Olá, {name}!\""
        ],
        "xp": 10
      },
      {
        "id": "func-n2-fullprice",
        "level": 2,
        "mode": "write_code",
        "title": "Combinar funções",
        "concept": "chamar função dentro de função (reusa N1)",
        "prompt": "Usando greet, escreva welcome(name) que retorna a saudação + ' Bem-vindo.'",
        "starter": "def welcome(name):\n    ...",
        "tests": [
          {"call": "welcome('Ana')", "expect": "Olá, Ana! Bem-vindo."}
        ],
        "hints": ["Você pode chamar greet(name) aqui dentro.", "Concatene com + ou f-string."],
        "xp": 15
      },
      {
        "id": "func-n3-discount-test",
        "level": 3,
        "mode": "write_test",
        "title": "Pense como QA: teste apply_discount",
        "concept": "Arrange/Act/Assert — um bom teste pega o bug",
        "prompt": "A função apply_discount já existe (read-only). Escreva pelo menos 3 testes (def test_*) que peguem bugs: desconto 0, desconto 100%, e um valor típico.",
        "target_func": "apply_discount",
        "reference_impl": "def apply_discount(price, percent):\n    return price - price * percent / 100",
        "mutants": [
          "def apply_discount(price, percent):\n    return price",
          "def apply_discount(price, percent):\n    return price * percent / 100",
          "def apply_discount(price, percent):\n    return price - percent"
        ],
        "min_tests": 3,
        "starter": "def test_apply_discount_zero():\n    ...",
        "hints": [
          "Arrange (prepare valores), Act (chame), Assert (compare).",
          "Pense num caso que cada bug NÃO passaria: desconto 0 deve devolver o preço cheio.",
          "assert apply_discount(100, 0) == 100"
        ],
        "xp": 30
      }
    ]
  }
}
```

**Regras de schema:**
- `level` ∈ {1,2,3}; cada capítulo idealmente tem ≥1 por nível.
- `mode` ∈ {`write_code`, `write_test`}. `write_test` exige `reference_impl`, `mutants` (3–5),
  `min_tests`.
- `hints` é **sempre escada** (sutil → mais claro → quase-solução). Nunca a solução literal completa
  no nível mais alto de dica — mostra um fragmento/esqueleto, não o exercício inteiro resolvido.
- `xp` cresce com o nível (sugestão: 10 / 15 / 30).

---

## 6. Contrato do runner Pyodide (`PyodideRunner.js`)

### 6.1 `write_code`
1. Carrega o código do aluno no Pyodide.
2. Para cada caso em `tests`: avalia `call` e compara com `expect` (igualdade de valor).
3. UI mostra ✅/❌ por caso. **Passa** se todos ✅.
4. Falha de sintaxe/exceção → mostra o traceback PT (o aluno **lê o erro primeiro** — regra do CLAUDE.md).

### 6.2 `write_test` (mutation testing — reusa SDD anterior §5)
1. Carrega `reference_impl` + os `test_*` do aluno → rodar todos → **devem PASSAR** (`tests_passed_on_reference`).
2. Para cada `mutant`: carrega o mutante + os mesmos testes → **≥1 teste deve FALHAR** (mutante "morto").
3. `mutation_score = mortos / total`. **Passa** se: reference passou **E** `score == 1.0` **E**
   nº de `def test_*` ≥ `min_tests` (cada um com ≥1 `assert`).
4. UI mostra, por mutante: ✅ morto / ❌ sobreviveu + dica ("seu teste não cobriu este caso").

### 6.3 Performance / risco
- Limitar mutantes a **3–5** e **reusar o interpretador** Pyodide entre execuções (não recriar).
- Investigar no build se dá pra usar o **worker Pyodide existente do shell** (evita 2ª instância / 2º
  download de ~6MB). Decisão de implementação — usar `codegraph`/Read no clone.

---

## 7. Integração com XP / progresso

- Conclusão de exercício grava em `practice_progress` (localforage + espelho SQLite via `serverSync`).
- XP somado ao total existente; nova badge **"🏋️ Praticante"** (ex.: 5 exercícios concluídos) e
  **"🧪 Caçador de bugs"** (1º exercício `write_test` com 100% dos mutantes mortos).
- **Sem farm de XP:** XP por exercício só conta **uma vez** (idempotente por `id`).

---

## 8. Metodologia de execução (a lei da SPEC, travada aqui)

> Esta seção existe para não repetir o erro de queimar ~2M tokens (SPEC linha 41).

| Tipo de trabalho | Como executar | Por quê |
|------------------|---------------|---------|
| **Escrever/atualizar esta spec e o plano** | Claude inline | Síntese de design; barato; é o trabalho do tutor. |
| **Gerar/traduzir CONTEÚDO de exercícios** (prompts, dicas, casos, adaptar 30 Days p/ PT-BR/QA) | **`agy` / `deliberation:ask-gemini` (0-quota)**, em **lotes pequenos (~10–20)**; eu reviso e adapto. | Cognição pesada e repetitiva → rota 0-quota. **Nunca** Workflow/Agent do Claude. |
| **Implementar componentes React + runner** (`PracticePanel.jsx`, `PyodideRunner.js`, edições em `App.js`/`dark.scss`) | Claude inline **ou** **subagente do Claude bem-escopado** (1 tarefa fechada por vez) | A SPEC permite subagente do Claude só p/ implementação escopada. |
| **Perguntas estruturais de código** (quem chama o quê, onde está X, impacto) | **`codegraph`** (se indexado; senão `codegraph init` ou Read direcionado) | Mais rápido/preciso que grep; pedido do aluno (2026-06-25). |
| **Validar recursos externos (URLs)** | **HTTP real** (curl/fetch), nunca confiar no LLM | O `agy` já inventou 11 links antes (base errada). |
| **Verificar a UI** | `build_ptbr.sh` → **Playwright** (screenshot) + grep no bundle | `dark.scss` só reflete após build; SPA trava páginas à frente do progresso. |

**Validação de JSON gerado por LLM:** conteúdo com HTML/`<code>` quebra o JSON (newline/aspas) →
**sempre validar/reparar** antes do build (lição durável das sessões 8–9).

---

## 9. MVP (primeiro passo) e critérios de aceite

**Capítulo-piloto: `functions` (Funções).** É a ponte natural pra QA ("função pura = testável") e
permite exercitar os **dois modos** num só capítulo. *(Alternativa de partida mais fácil: `string_basics`/`a_bit_more_about_strings`, que encaixa o Password Validator já em andamento — decisão final do aluno na revisão desta spec.)*

**Escopo do MVP (ponta a ponta, 1 capítulo):**
1. `exercises_br.json` com o capítulo Funções: **N1 e N2 `write_code`** + **N3 `write_test`** (com 3 mutantes).
2. `PracticePanel.jsx` + `PyodideRunner.js` integrados em `App.js`, estilizados em `dark.scss`.
3. XP + persistência de prática (`practice_progress`).
4. `build_ptbr.sh` compila; verificação Playwright.

**Critérios de aceite (GO):**
- [ ] No `/course/`, no capítulo Funções, aparece o painel **"🏋️ Pratique"** com 3 níveis.
- [ ] **N1/N2:** aluno escreve a função, "▶ Rodar" mostra ✅/❌ por caso; ao passar, ganha XP (uma vez).
- [ ] **N3:** aluno escreve testes; vê **um mutante sobreviver**; corrige; **mata todos**; só então ganha XP.
- [ ] Erro de código mostra **traceback em PT** (o aluno lê o erro primeiro).
- [ ] Progresso de prática persiste (recarregar a página mantém o ✅).
- [ ] Nenhuma dica entrega a solução completa do exercício.
- [ ] Testes `unittest` do `server.py` verdes; build sem erro; screenshot Playwright confirma.

---

## 10. Rollout (marcos)

- **M1 — MVP (este doc, §9):** capítulo Funções ponta a ponta. *Aceite: critérios §9.*
- **M2 — Expandir conteúdo:** demais capítulos ganham 3 níveis, **conteúdo gerado via `agy` (0-quota)**
  em lotes, revisado e adaptado a QA. Priorizar onde há gap (Dicionários, Listas, Strings).
- **M3 — Sementes do 30 Days:** mapear exercícios Nível 1/2/3 do Asabeneh por tópico, **traduzir/adaptar
  via `agy`** com framing QA, validar e mesclar no `exercises_br.json`.
- **M4 — Ligar com a Fase 2 da SDD anterior:** os exercícios `write_test` viram a porta de entrada
  para o capítulo de pytest "de verdade".

---

## 11. Fora de escopo / riscos / questões abertas

**Fora de escopo agora:** Playwright/POM dentro do navegador (Fase 4 da SDD anterior, roda local);
streak diário estilo "30 dias" (abordagem A, rejeitada); reordenar o índice.

**Riscos:**
- **Pyodide lento** com N mutantes → limitar a 3–5 e reusar o interpretador (§6.3).
- **2ª instância Pyodide** (peso de download) → investigar reuso do worker do shell no build.
- **Método** → não empilhar conceitos; cada exercício novo = 1 conceito + Feynman check (CLAUDE.md).
- **JSON inválido** gerado por LLM → validar/reparar sempre (§8).

**Questões abertas (para a revisão do aluno):**
1. **Capítulo-piloto:** Funções (recomendado) ou Strings (encaixa o Password Validator)?
2. **Comparação de igualdade no `write_code`:** igualdade simples de valor cobre o MVP? (vs. comparar
   `repr`/tipos — decisão de implementação; default: valor.)
3. **Tutor qualitativo no painel:** incluir botão "Pedir dica ao tutor (agy)" já no MVP, ou só dicas
   pré-escritas em escada primeiro? (Recomendação: dicas pré-escritas no MVP; tutor agy no M2.)

---

## 12. Fontes / referências
- `SDD-curriculo-qa.md` (este repo) — currículo QA + engine de mutation (§5 reusada aqui).
- `media_br.json` (este repo) — padrão de painel React por capítulo (referência de implementação).
- `SPEC-skills-ptbr.md` (Second Brain) — rota 0-quota, lei de execução (§8).
- `30 Days of Python` — Asabeneh (https://github.com/Asabeneh/30-Days-Of-Python) — fonte das sementes (M3).
- `CLAUDE.md` (este repo, gitignored) — contrato de ensino e diagnóstico do aluno.

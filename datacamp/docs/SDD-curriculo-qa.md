# SDD — Plataforma de estudo Python → QA Automation (índice + trilha de testes)

> **Spec-Driven Development.** Documento de design. Define O QUÊ e POR QUÊ antes de qualquer
> código. Nada aqui foi implementado ainda — é a base para decidir e planejar.
>
> - **Data:** 2026-06-24
> - **Autor:** Claude (tutor), a pedido do Deehlusa
> - **Status:** PROPOSTA (aguarda aprovação/priorização do aluno)
> - **Base de evidência:** análise de `course_data.py` (futurecoder), `curriculum.py` + `server.py`
>   (dashboard), e research web 2026 (ver §10 Fontes).

---

## 1. Objetivo

Evoluir a plataforma de estudo **free, autodidata e assistida por IA**. O objetivo é **duplo e
equilibrado** (decisão do aluno, 2026-06-24): **(a) base sólida de Python + mini-projetos** ao
longo do caminho, **(b) trilha de QA/testes** em cima dessa base. **Não é "só QA"** — é Python
bem aprendido, praticado em mini-projetos, e *então* testado como um QA faria. O critério final é o
do `CLAUDE.md`: dado um sistema desconhecido, o aluno **escreve os testes** (pytest/requests/Playwright),
roda, interpreta falhas e commita num repo profissional **sem depender de IA para o código**.

### Decisões travadas com o aluno (2026-06-24)
- **Manter a ordem atual** do índice — apenas **ADICIONAR** (sem reordenar; preserva progresso/XP).
- **Mini-projetos ao longo do caminho**, não só no fim de cada fase (Python base via projetos pequenos).
- **Projeto de API roda contra mock local** (0 dependência externa, offline, sempre estável).

### Restrições (do `CLAUDE.md` e do contexto)
- **Free / 0-quota:** roda local; IA pesada via `agy` (Gemini), Claude só quando premium.
- **PT-BR** na prosa, **inglês** em código/nomes.
- **Um conceito por vez**; o aluno se sobrecarrega com muita teoria empilhada.
- **O aluno digita todo o código.** A plataforma revisa/valida; nunca entrega a solução.
- **Mentalidade de quebrar o código** (edge cases, casos negativos) desde o começo.
- Não reinventar: a base teórica é o **futurecoder** (open-source, MIT) já self-hosted.

---

## 2. Estado atual (o que já existe)

| Peça | O que é | Avaliação p/ QA |
|------|---------|-----------------|
| **futurecoder PT-BR** (`serve_futurecoder.py`) | Teoria + shell Python ao vivo. 11 caps, 57 págs. | Base Python boa; **sem** dict, OOP, try/except, pytest, json, open(). |
| **Dashboard** (`server.py` + `curriculum.py`) | 32 exercícios, 10 caps, valida com `agy`, XP em SQLite. | Progressão Python core boa; framing QA forte em alguns caps (Funções, Exceções, JSON). |
| **Curso embutido** (`course_data.py`) | futurecoder extraído/traduzido p/ aba "Curso". | Espelho da teoria. |

### O gap central (a descoberta)
Hoje, em **todos os 32 exercícios**, o aluno **escreve a FUNÇÃO** e a plataforma **roda os `assert`**
(confirmado em `server.py`: o Pyodide executa o campo `tests` de `curriculum.py` e envia `tests_passed`).
**O aluno nunca escreve um teste.** Mas a profissão de QA Automation é exatamente o inverso:
**escrever testes que pegam bugs.** Esse é o maior gap e o foco desta SDD.

### Conceitos ausentes p/ QA (consolidado das 3 análises)
Escrever testes (`def test_*`) · padrão **AAA** · `assert` com mensagem · `pytest.raises` ·
`@pytest.mark.parametrize` · `@pytest.fixture` / `conftest.py` · `pytest-cov` · mocking
(`unittest.mock`) · `requests`/HTTP · validação de schema JSON · **Page Object Model concreto** ·
regex p/ logs · CSV como massa de teste.

---

## 3. Decisão de design central

> **Inverter o papel: criar exercícios onde o ALUNO escreve os testes, avaliados por _mutation testing_.**

A plataforma guarda a função **correta** + N versões **com bugs plantados** (mutantes). O teste do
aluno precisa **passar na correta** e **falhar em cada mutante**. O score = % de mutantes "mortos".
Isso ensina, de forma medível, a skill-núcleo de QA: *"um bom teste pega o bug"* — e roda 100% no
**Pyodide** que já está em uso (sem instalar nada). É também o que diferencia um QA de verdade de um
"gravador de testes" (evidência §10).

Mantém-se o tipo de exercício atual (aluno escreve função) **e** adiciona-se o novo tipo (aluno escreve
teste). Os dois convivem.

---

## 4. Índice proposto (o "índice melhorado")

Mescla **teoria (futurecoder)** + **prática (dashboard)** + **trilha de testes nova**, em 5 fases
alinhadas ao roadmap QA 2026. **DECISÃO: manter a ordem atual e só ADICIONAR** (sem reordenar).
Cada conceito de Python ganha um **mini-projeto pequeno** (kata) para fixar a base, e os testes vêm
em cima do que ele já construiu.

### Mini-projetos por fase (base Python via prática)
Pequenos, incrementais, cada um vira material testável depois:
**FizzBuzz** (loops) → **String Calculator** (parsing/strings) → **Password Validator** (funções, em
andamento) → **Roman Numerals** (parametrize) → **Tennis/BankAccount** (OOP/POM). Os "Projetos
integradores" maiores (1–4) fecham cada fase.

### FASE 1 — Python Core (consolidar; já ~80% pronto)
1. Tipos e variáveis *(existe)*
2. Condicionais e lógica *(existe)*
3. Loops *(existe — pode enxugar de 5→3 exercícios)*
4. Strings *(existe — ampliar p/ 4; add regex básico)*
5. Listas *(existe)*
6. Dicionários, sets, tuplas *(existe; **add no futurecoder**, que não cobre dict)*
7. **Funções puras** *(existe — âncora "função pura = testável"; opcional mover p/ mais cedo)*
8. Exceções *(existe — hoje o `pytest.raises` só aparece no `qa_note`)*
9. JSON *(existe — ampliar p/ "API Testing" na Fase 3)*
10. OOP / base do POM *(existe — tornar POM concreto: `LoginPage`)*
> **Projeto 1 integrador:** Password Strength Validator (já em andamento — Semana 1).

### FASE 2 — Escrever testes com pytest *(NOVO — o coração desta SDD)*
11. O que é um teste? Anatomia **AAA** (Arrange/Act/Assert)
12. Primeiro `assert` + mensagem de falha legível
13. Caminho feliz **e** caminho de erro (branch coverage mental)
14. Testar exceções → `try/except` do aluno, depois `pytest.raises`
15. Parametrização manual (lista de `(input, expected)`) → `@pytest.mark.parametrize`
16. Fixtures (`@pytest.fixture`, escopo) + `conftest.py`
17. Coverage (`pytest-cov`, meta ≥ 80%) + **mutation testing como lição** (cobertura ≠ proteção)
18. Mocking (`unittest.mock`) — isolar dependências
> Todos os exercícios 11–18 usam o **tipo "aluno escreve o teste"** (§5).

### FASE 3 — API Testing com `requests` *(amplia o cap. JSON)*
19. HTTP: métodos, status codes, headers
20. `requests`: GET/POST; asserções de status/body
21. Validação de schema (campos obrigatórios via `set` — recicla Fase 1)
22. Fixtures de API (base URL, token) em pytest
> **Projeto 2 integrador:** suíte pytest p/ API pública (JSONPlaceholder → Reqres com auth fake).
> *(Pode rodar contra mock local p/ manter 0 dependência externa.)*

### FASE 4 — Browser com Playwright + POM *(fora do Pyodide — local)*
23. Locators (`get_by_role`/`get_by_text`), actions, `expect(...)`
24. Page Object Model concreto (classe por página)
25. Fixtures de `browser`/`page`; screenshots/trace em falha; auto-wait (sem `sleep`)
> **Projeto 3 integrador:** suíte POM p/ SauceDemo (login + carrinho + checkout).

### FASE 5 — CI/CD e Portfólio
26. Git workflow (branch, PR, commit msg)
27. GitHub Actions: rodar pytest no push; badge verde no README
28. Relatório (pytest-html) + (opcional) Docker
> **Projeto 4 final:** framework completo (pytest + POM + requests + GitHub Actions).

---

## 5. Especificação técnica — exercício "aluno escreve o teste"

### 5.1 Mudança no schema de `curriculum.py`
Novo `type` por exercício (default `"write_code"` p/ os 32 atuais; novos = `"write_test"`):

```python
{
    "ord": 33,
    "chapter": "11. Escrever testes (pytest)",
    "title": "Testar apply_discount (AAA)",
    "type": "write_test",                 # <-- novo
    "concept": "Arrange / Act / Assert",
    "lesson": "...",
    "instructions": ["Escreva 3 testes cobrindo: desconto 0, desconto total, valor típico."],
    "target_func": "apply_discount",      # função SOB TESTE (fornecida pronta)
    "reference_impl": "def apply_discount(price, percent):\n    return price - price*percent/100",
    "mutants": [                          # <-- bugs plantados; cada um deve ser 'morto'
        "def apply_discount(price, percent):\n    return price",            # ignora desconto
        "def apply_discount(price, percent):\n    return price*percent/100",# retorna o desconto
        "def apply_discount(price, percent):\n    return price - percent",  # esquece o /100*price
    ],
    "starter": "def test_apply_discount():\n    ...",
    "min_tests": 3,                       # exige nº mínimo de funções test_*
    "points": 30,
}
```

### 5.2 Engine de avaliação (mutation) — onde roda
- **Pyodide (browser), como hoje.** O runner:
  1. Carrega `reference_impl` + o código de teste do aluno → roda todos os `test_*` → **devem PASSAR**.
  2. Para cada mutante: carrega `mutant` + os mesmos testes → **pelo menos 1 deve FALHAR** (mutante "morto").
  3. `score = mutantes_mortos / total_mutantes`; aprova se testes passam na correta **e** `score == 100%`.
- Validações de qualidade: nº de `def test_*` ≥ `min_tests`; cada um contém ≥1 `assert`.
- `agy` continua como **revisor qualitativo** (nomes dos testes, AAA, legibilidade) — não árbitro.

### 5.3 Mudanças em `server.py`
- `/api/grade` aceita `exercise_type`; p/ `write_test`, recebe do cliente `mutation_score` +
  `tests_passed_on_reference` (calculados no Pyodide) e o código de teste do aluno.
- `grade_with_agy()` ganha um prompt-modo "revisar testes" (foco em AAA/cobertura, não em implementar).
- XP só com `tests_passed_on_reference == True` **e** `mutation_score == 1.0` **e** `min_tests` satisfeito.

### 5.4 Mudanças no frontend (`index.html` / patches)
- Editor mostra a **função sob teste** (read-only) + área p/ o aluno escrever `test_*`.
- Botão "▶ Rodar meus testes" → roda referência + mutantes → mostra, por mutante,
  ✅ morto / ❌ sobreviveu (com dica: "seu teste não cobriu este caso").

---

## 6. Mini-projetos de portfólio (saída concreta p/ vagas)
1. **Password Validator** — funções puras, `pytest.raises`, parametrize, boundary values. *(em andamento)*
2. **API Testing suite** — `requests`, fixtures de auth, status/body/schema. *(skill mais valorizada júnior)*
3. **UI + Playwright POM** — locators, POM, screenshots em falha. *(parte "visível" do portfólio)*
4. **Framework completo + GitHub Actions** — une tudo, CI com badge verde.

---

## 7. Recursos free por tópico (a linkar em cada capítulo)
| Tópico | Recurso free |
|--------|--------------|
| Python core | futurecoder.io (já instalado) · Real Python "Python Basics" |
| pytest | Test Automation University "Introduction to pytest" · docs.pytest.org |
| API/requests | Real Python "Python Requests" |
| Playwright | TAU "Introduction to Playwright" · playwright.dev/python |
| TDD/katas | kata-log.rocks/tdd · The Digital Cat "TDD in Python with pytest" |
| Mutation testing | mutatest docs · vmzakharov/mutate-test-kata |
| CI | docs.github.com/actions |

---

## 8. Plano de rollout (marcos + critério de aceite)
- **M0 — Higiene** *(feito)*: `.gitignore` cobre `*.db`/`*.sqlite*`; nenhum banco rastreado. ✅
- **M1 — Trilha de testes (MVP):** schema `type:"write_test"` + 1 capítulo (exercícios 11–13) +
  engine de mutation no Pyodide. **Aceite:** aluno escreve teste, vê mutante sobreviver, corrige, mata todos.
- **M2 — pytest completo:** exercícios 14–18 (raises, parametrize, fixtures, coverage, mock).
  **Aceite:** 5 conceitos pytest praticados *escrevendo* testes.
- **M3 — API testing:** amplia cap. JSON → 19–22 + Projeto 2 (mock local). **Aceite:** suíte verde contra mock.
- **M4 — Reordenação opcional do índice** (Funções mais cedo; enxugar Loops). **Aceite:** sem perder XP.
- **M5 — Playwright/POM + CI** (fora do Pyodide). **Aceite:** Projeto 3 e 4 rodando + GitHub Actions.

Cada marco: implementação enxuta (preferir `agy`/subagentes p/ trabalho repetitivo), testes `unittest`
do `server.py` verdes, e registro no `CLAUDE.md` (Registro de sessões).

---

## 9. Fora de escopo / riscos / questões abertas
- **Fora de escopo agora:** Playwright dentro do navegador (precisa rodar local, Fase 4); Allure/Docker.
- **Risco — Pyodide:** rodar N mutantes pode ficar lento; mitigar limitando mutantes (3–5) e reusando o interpretador.
- **Risco — método:** não empilhar conceitos; cada exercício novo = 1 conceito + Feynman check (CLAUDE.md).
- **Decididas (2026-06-24):**
  - ✅ Objetivo = **base Python + mini-projetos + QA** (não só QA).
  - ✅ **Manter ordem atual** do índice (só adicionar).
  - ✅ Projeto de API = **mock local**.
- **Aberta:**
  1. Próximo passo: **M1 (MVP da trilha de testes)** já, ou **plano de execução completo (M1–M5)** primeiro?
     *(Recomendação: começar pelo M1 + retomar o **Password Validator** — já em andamento, é base Python
     + mini-projeto + 1º exercício de escrever testes; cabe no "um conceito por vez".)*

---

## 10. Fontes (research 2026)
- Test Automation University — Introduction to pytest / Playwright (testautomationu.applitools.com)
- pytest docs (docs.pytest.org) · Real Python (pytest, requests)
- Roadmaps QA 2026: SuperSQA, BirJob, TestLeaf · TestDino (Playwright)
- kata-log.rocks · The Digital Cat (TDD in pytest) · mutatest docs · vmzakharov/mutate-test-kata
- Portfólio ref.: github.com/danielokpanachi/playwright-projects · github.com/AutomationPanda/playwright-python-tutorial

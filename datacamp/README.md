# 🐍 Plataforma de estudo de Python

## ⭐ futurecoder em PT-BR (plataforma principal) — `serve_futurecoder.py`

Fork self-hosted do [futurecoder](https://github.com/alexmojaki/futurecoder)
(React + Pyodide, **MIT**) rodando **localmente em português**: UI profissional,
shell Python ao vivo, debuggers (Python Tutor, snoop), curso completo.

```bash
cd datacamp && python3 serve_futurecoder.py
```
→ **http://localhost:8001**

Como foi montado (já feito; só refazer se mudar o conteúdo):
- Fonte clonada em `.futurecoder-src/` (fora do git). Python 3.12 (via Homebrew).
- `core/translation.py` tem um patch (try/except) porque a tradução `br` oficial é
  ~96% — o que falta cai pro inglês em vez de quebrar o build.
- Build: `FUTURECODER_LANGUAGE=br PRINT_ERRORS=1 FIX_CORE_IMPORTS=1 .venv/bin/python -m scripts.generate_static_files`
  e depois `cd frontend && REACT_APP_LANGUAGE=br CI=false npm run build`.
- `serve_futurecoder.py` serve o build com headers COOP/COEP (exigência do Pyodide).
- Pendente: `agy` traduzir os ~4% de rótulos de UI em inglês + capítulo de Dicionários.

---

# 🎯 Trilha Python para QA (prática complementar) — `server.py`

Dashboard interativo de estudo. Você vê o exercício, escreve o código (aqui ou no
VSCode), roda os testes na hora e a IA (`agy`, 0-quota) valida e te dá XP.

## Como rodar

```bash
cd datacamp
python3 server.py
```

Depois abra **http://localhost:8000** no navegador. `Ctrl+C` para parar.

## Como funciona

1. **Escolhe um exercício** na barra lateral (trilha linear, foco QA).
2. **Escreve o código** no editor (ou cola do VSCode).
3. **▶ Rodar testes (Pyodide)** → roda Python *no navegador* e checa com `assert`.
   Verde = passou, vermelho = mostra o erro.
4. **🤖 Validar com agy** → o `agy` (Gemini, 0-quota) revisa a qualidade no modo
   tutor (1 ponto forte + 1 melhoria, sem te entregar a resposta) e libera o **XP**.

## Stack (tudo grátis, sem instalar nada)

| Peça      | O quê                          | Por quê |
|-----------|--------------------------------|---------|
| `index.html`   | Frontend + **Pyodide** (CDN) | Roda Python no navegador, sem servidor de execução |
| `server.py`    | Backend **Python stdlib**    | Serve o dashboard e chama o `agy` |
| `curriculum.py`| Conteúdo (10 capítulos, 32 ex.) | Cada exercício tem contexto, instruções, exemplo, dica e código inicial |
| `progress.db`  | **SQLite**                   | Banco de verdade pro progresso/XP (não vai pro git) |
| `agy`          | Antigravity CLI (Gemini)     | Validação por IA **0-quota** |

## 📚 Curso completo em PT-BR (aba "Curso")

O dashboard tem o **curso do futurecoder embutido e traduzido pra PT-BR** — 11
capítulos (O Shell → Jogo da Velha), 57 páginas, com navegação Table of Contents,
lições e código. É a sua **base teórica**, dentro do app, sem redirect.

- Conteúdo extraído do [futurecoder](https://github.com/alexmojaki/futurecoder)
  (licença **MIT** — ver `FUTURECODER-LICENSE.txt`), usando a **tradução PT-BR
  oficial** do projeto (96% dos passos).
- Gerado por `build_course.py` → `course_data.py` (não editar à mão; regerar).
  Fonte clonada em `.futurecoder-src/` (fora do git).
- Pendente (via `agy`): traduzir os ~11 passos sem PT e o cap. de Dicionários
  (o locale `br` não cobriu).

Regerar o curso:
```bash
python3 build_course.py   # precisa do clone em .futurecoder-src/
```

## A base extra (opcional)

A dashboard é a **prática**. Pra aprender o conceito do zero (a "base"), use:

- **[futurecoder.io](https://futurecoder.io)** — curso Python interativo, open-source, **em português** (roda no navegador, mesma tech daqui). Melhor ponto de partida.
- **[Pense em Python](https://penseallen.github.io/PensePython2e/)** — livro-texto PT-BR (Creative Commons), teoria por capítulo.

Cada capítulo da dashboard tem uma **📖 Aula do capítulo** com teoria curta + link direto
pra esses recursos, e cada exercício tem um **📚 Aprenda primeiro** com o conceito específico.

## Editar o conteúdo

Tudo que é exercício/capítulo está em `curriculum.py` (Python puro). Pode editar à
vontade e reiniciar o servidor — o conteúdo é re-semeado **sem apagar seu XP**
(o progresso fica no `progress.db`, que é preservado).

## Progresso

Tudo fica em `progress.db` (SQLite). Pra ver no terminal:

```bash
sqlite3 progress.db "SELECT ord, title, status, score FROM exercises e JOIN progress p ON p.exercise_id=e.id ORDER BY ord;"
```

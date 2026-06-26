# -*- coding: utf-8 -*-
"""
Dashboard de estudo Python-para-QA (estilo DataCamp, 0-quota).

Stack:
  - Backend: Python stdlib apenas (http.server, sqlite3, subprocess) -> nada de pip.
  - Banco:   SQLite (progress.db) -> exercicios, capitulos, progresso e XP.
  - IA:      agy (Antigravity CLI / Gemini, 0-quota) valida o codigo e da os pontos.
  - Conteudo: curriculum.py (capitulos + exercicios com anatomia completa).

Rodar:
    python3 server.py
Depois abra http://localhost:8000 no navegador.
"""

import json
import re
import shutil
import sqlite3
import subprocess
import http.server
import socketserver
from pathlib import Path

from curriculum import TRACK, CHAPTERS

try:
    from course_data import COURSE, ATTRIBUTION
except ImportError:  # curso ainda não gerado (rodar: python3 build_course.py)
    COURSE, ATTRIBUTION = [], ""

HERE = Path(__file__).parent
DB_PATH = HERE / "progress.db"
SAVED_DIR = HERE / "saved_code"
COURSE_BUILD = HERE / ".futurecoder-src" / "frontend" / "course"
PORT = 8000
AGY_TIMEOUT = 180  # agy pode pendurar (exit 124); cortamos com timeout.


# ---------------------------------------------------------------------------
# Banco de dados
# ---------------------------------------------------------------------------
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Recria o conteudo (capitulos/exercicios) e PRESERVA o progresso/XP."""
    conn = db()
    # Conteudo e estatico: derruba e re-semeia (aplica updates do curriculum.py).
    conn.executescript(
        """
        DROP TABLE IF EXISTS exercises;
        DROP TABLE IF EXISTS chapters;
        CREATE TABLE chapters (
            ord         INTEGER PRIMARY KEY,
            title       TEXT UNIQUE,
            description TEXT,
            lesson      TEXT,
            resources   TEXT     -- linhas 'label||url'
        );
        CREATE TABLE exercises (
            id           INTEGER PRIMARY KEY,
            ord          INTEGER UNIQUE,
            chapter      TEXT,
            title        TEXT,
            concept      TEXT,
            lesson       TEXT,
            context      TEXT,
            instructions TEXT,   -- bullets juntados por quebra de linha
            example      TEXT,
            qa_note      TEXT,
            hint         TEXT,
            starter      TEXT,
            func         TEXT,
            tests        TEXT,
            points       INTEGER,
            -- Refactor "aprender fazendo": campos opcionais novos
            type           TEXT DEFAULT 'write_code',  -- write_code | write_test
            predict        TEXT DEFAULT '',            -- pergunta "o que isto retorna?"
            hints          TEXT DEFAULT '[]',          -- JSON: dicas progressivas (lista)
            video          TEXT DEFAULT '',            -- URL de video (YouTube)
            sources        TEXT DEFAULT '[]',          -- JSON: [{label,url}]
            -- Campos da trilha "aluno escreve o teste" (mutation testing)
            target_func    TEXT DEFAULT '',            -- funcao sob teste (fornecida pronta)
            reference_impl TEXT DEFAULT '',            -- implementacao correta
            mutants        TEXT DEFAULT '[]',          -- JSON: lista de impls bugadas
            min_tests      INTEGER DEFAULT 0           -- nº minimo de funcoes test_*
        );
        CREATE TABLE IF NOT EXISTS progress (
            exercise_id INTEGER PRIMARY KEY,
            status      TEXT DEFAULT 'todo',   -- todo | done
            score       INTEGER DEFAULT 0,
            attempts    INTEGER DEFAULT 0,
            last_code   TEXT DEFAULT '',
            updated_at  TEXT DEFAULT (datetime('now','localtime'))
        );
        """
    )
    for i, (title, info) in enumerate(CHAPTERS.items(), start=1):
        resources = "\n".join(f"{label}||{url}" for label, url in info["resources"])
        conn.execute(
            "INSERT INTO chapters (ord,title,description,lesson,resources) VALUES (?,?,?,?,?)",
            (i, title, info["description"], info["lesson"], resources),
        )
    for ex in TRACK:
        # Dicas progressivas: usa 'hints' (lista) se houver, senao cai no 'hint' unico.
        hints = ex.get("hints") or ([ex["hint"]] if ex.get("hint") else [])
        row = {
            "ord": ex["ord"],
            "chapter": ex["chapter"],
            "title": ex["title"],
            "concept": ex.get("concept", ""),
            "lesson": ex.get("lesson", ""),
            "context": ex.get("context", ""),
            "instructions": "\n".join(ex.get("instructions", [])),
            "example": ex.get("example", ""),
            "qa_note": ex.get("qa_note", ""),
            "hint": ex.get("hint", ""),
            "starter": ex.get("starter", ""),
            "func": ex.get("func", ""),
            "tests": ex.get("tests", ""),
            "points": ex.get("points", 0),
            "type": ex.get("type", "write_code"),
            "predict": ex.get("predict", ""),
            "hints": json.dumps(hints, ensure_ascii=False),
            "video": ex.get("video", ""),
            "sources": json.dumps(ex.get("sources", []), ensure_ascii=False),
            "target_func": ex.get("target_func", ""),
            "reference_impl": ex.get("reference_impl", ""),
            "mutants": json.dumps(ex.get("mutants", []), ensure_ascii=False),
            "min_tests": ex.get("min_tests", 0),
        }
        conn.execute(
            """INSERT INTO exercises
               (ord,chapter,title,concept,lesson,context,instructions,example,qa_note,
                hint,starter,func,tests,points,
                type,predict,hints,video,sources,target_func,reference_impl,mutants,min_tests)
               VALUES
               (:ord,:chapter,:title,:concept,:lesson,:context,:instructions,:example,:qa_note,
                :hint,:starter,:func,:tests,:points,
                :type,:predict,:hints,:video,:sources,:target_func,:reference_impl,:mutants,:min_tests)""",
            row,
        )
    conn.execute(
        "INSERT OR IGNORE INTO progress (exercise_id) SELECT id FROM exercises"
    )
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS course_progress (
            id             INTEGER PRIMARY KEY CHECK (id = 1),
            page_slug      TEXT DEFAULT '',
            pages_progress TEXT DEFAULT '{}',
            editor_content TEXT DEFAULT '',
            pages_done     INTEGER DEFAULT 0,
            pages_total    INTEGER DEFAULT 0,
            updated_at     TEXT DEFAULT (datetime('now','localtime'))
        );
        """
    )
    conn.execute("INSERT OR IGNORE INTO course_progress (id) VALUES (1)")
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS practice_progress (
            exercise_id TEXT PRIMARY KEY,
            xp          INTEGER DEFAULT 0,
            mode        TEXT DEFAULT '',
            updated_at  TEXT DEFAULT (datetime('now','localtime'))
        );
        """
    )
    conn.commit()
    conn.close()


def get_track():
    conn = db()
    rows = conn.execute(
        """SELECT e.*, p.status, p.score, p.attempts, p.last_code
           FROM exercises e JOIN progress p ON p.exercise_id = e.id
           ORDER BY e.ord"""
    ).fetchall()
    chap_rows = conn.execute(
        "SELECT title, description, lesson, resources FROM chapters ORDER BY ord"
    ).fetchall()
    conn.close()

    track = []
    for r in rows:
        d = dict(r)
        d["instructions"] = d["instructions"].split("\n") if d["instructions"] else []
        for key in ("hints", "sources", "mutants"):
            try:
                d[key] = json.loads(d.get(key) or "[]")
            except (ValueError, TypeError):
                d[key] = []
        track.append(d)

    # Progresso por capitulo.
    chapters = []
    for c in chap_rows:
        items = [t for t in track if t["chapter"] == c["title"]]
        done = sum(1 for t in items if t["status"] == "done")
        xp = sum(t["score"] for t in items)
        maxxp = sum(t["points"] for t in items)
        resources = []
        for line in (c["resources"] or "").split("\n"):
            if "||" in line:
                label, url = line.split("||", 1)
                resources.append({"label": label, "url": url})
        chapters.append({
            "title": c["title"],
            "description": c["description"],
            "lesson": c["lesson"],
            "resources": resources,
            "total": len(items),
            "done": done,
            "xp": xp,
            "max_xp": maxxp,
            "pct": round(100 * done / len(items)) if items else 0,
        })

    return {
        "chapters": chapters,
        "track": track,
        "total_xp": sum(t["score"] for t in track),
        "max_xp": sum(t["points"] for t in track),
    }


# ---------------------------------------------------------------------------
# Progresso do curso (futurecoder) + salvar codigo no projeto
# ---------------------------------------------------------------------------
def get_course_progress():
    conn = db()
    row = conn.execute("SELECT * FROM course_progress WHERE id=1").fetchone()
    conn.close()
    if row is None:
        return {"page_slug": "", "pages_progress": {}, "editor_content": "",
                "pages_done": 0, "pages_total": 0, "pct": 0, "updated_at": None}
    d = dict(row)
    try:
        d["pages_progress"] = json.loads(d["pages_progress"] or "{}")
    except (ValueError, TypeError):
        d["pages_progress"] = {}
    total = d["pages_total"] or 0
    d["pct"] = round(100 * d["pages_done"] / total) if total else 0
    d.pop("id", None)
    return d


def save_course_progress(page_slug, pages_progress, editor_content, pages_done, pages_total):
    conn = db()
    conn.execute(
        """UPDATE course_progress
           SET page_slug=?, pages_progress=?, editor_content=?,
               pages_done=?, pages_total=?, updated_at=datetime('now','localtime')
           WHERE id=1""",
        (page_slug or "", json.dumps(pages_progress or {}), editor_content or "",
         int(pages_done or 0), int(pages_total or 0)),
    )
    conn.commit()
    conn.close()
    return {"ok": True}


def save_code(slug, code):
    """Grava o codigo do aluno em saved_code/<slug>.py. Sanitiza o slug (anti path-traversal)."""
    safe = re.sub(r"[^A-Za-z0-9_-]", "", slug or "") or "untitled"
    if not (code or "").strip():
        return {"ok": False, "error": "codigo vazio"}, 400
    SAVED_DIR.mkdir(parents=True, exist_ok=True)
    path = SAVED_DIR / f"{safe}.py"
    path.write_text(code, encoding="utf-8")
    return {"ok": True, "path": f"saved_code/{safe}.py"}, 200


def save_practice_progress(exercise_id, xp, mode):
    """Espelha a conclusao de um exercicio do painel Pratique no SQLite."""
    if not exercise_id:
        return {"ok": False, "error": "sem exercise_id"}, 400
    conn = db()
    conn.execute(
        """INSERT INTO practice_progress (exercise_id, xp, mode, updated_at)
           VALUES (?,?,?,datetime('now','localtime'))
           ON CONFLICT(exercise_id) DO UPDATE SET
               xp=excluded.xp, mode=excluded.mode, updated_at=datetime('now','localtime')""",
        (str(exercise_id), int(xp or 0), str(mode or "")),
    )
    conn.commit()
    conn.close()
    return {"ok": True}, 200


def get_practice_progress():
    conn = db()
    rows = conn.execute(
        "SELECT exercise_id, xp, mode, updated_at FROM practice_progress"
    ).fetchall()
    conn.close()
    items = [dict(r) for r in rows]
    return {"items": items, "count": len(items), "xp": sum(i["xp"] for i in items)}


# ---------------------------------------------------------------------------
# Tutor IA por fase (agy 0-quota OU claude via CLI) — segue as regras do CLAUDE.md
# ---------------------------------------------------------------------------
TUTOR_TIMEOUT = 180

# Regras de ensino destiladas do CLAUDE.md (tutor de Python para QA Automation).
TUTOR_RULES = """Voce e o tutor particular de logica de programacao e Python para QA Automation
do aluno (Deehlusa). Siga ESTRITAMENTE estas regras:
- Responda em portugues (PT-BR). Codigo e nomes de variaveis em ingles.
- NUNCA escreva a solucao completa do exercicio. No maximo 1-3 linhas de exemplo
  com um conceito ISOLADO (nunca o exercicio em si).
- Use o metodo socratico: faca perguntas que guiem o aluno a achar a resposta sozinho.
- Erro e material de aula: se o codigo dele quebra, NAO conserte; pergunte o que ele
  acha que a mensagem de erro esta dizendo e guie ate ele achar o bug.
- Um conceito por vez. Mensagens curtas. Nao despeje teoria.
- Mentalidade de QA: provoque ele a pensar em edge cases, entradas invalidas,
  casos negativos e legibilidade.
- Celebre progresso com evidencia concreta (aponte a linha exata do codigo dele)."""

TUTOR_CLIS = {
    "agy": ["agy", "--print"],
    "claude": ["claude", "-p"],
}


def build_tutor_prompt(context, question, code):
    code = code or "(o aluno ainda nao escreveu codigo)"
    question = (question or "").strip() or "O aluno pediu ajuda, mas nao escreveu a duvida."
    return f"""{TUTOR_RULES}

CONTEXTO DA AULA ATUAL:
{context or "(sem contexto de pagina)"}

CODIGO ATUAL DO ALUNO:
```python
{code}
```

PERGUNTA / PEDIDO DO ALUNO:
{question}

Responda como tutor, seguindo as regras acima."""


def run_tutor(tutor, context, question, code):
    base = TUTOR_CLIS.get(tutor)
    if base is None:
        return {"ok": False, "feedback": "Tutor invalido."}, 400
    if shutil.which(base[0]) is None:
        return {"ok": False, "feedback": f"'{base[0]}' nao esta no PATH deste terminal."}, 200
    prompt = build_tutor_prompt(context, question, code)
    try:
        out = subprocess.run(
            base + [prompt], capture_output=True, text=True, timeout=TUTOR_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "feedback": "O tutor demorou demais (timeout). Tenta de novo."}, 200
    text = (out.stdout or "").strip()
    if not text:
        return {"ok": False, "feedback": "O tutor nao retornou nada. Tenta de novo."}, 200
    return {"ok": True, "feedback": text, "tutor": tutor}, 200


# ---------------------------------------------------------------------------
# Validacao com agy (0-quota)
# ---------------------------------------------------------------------------
def build_prompt(ex, code, tests_passed):
    """Prompt no modo TUTOR: agy da feedback, NAO reescreve a solucao."""
    instr = ex["instructions"] if isinstance(ex["instructions"], str) \
        else "\n".join(ex["instructions"])

    # Modo "aluno escreve o teste": revisar a QUALIDADE dos testes, nao implementar.
    if ex.get("type") == "write_test":
        return f"""Voce e um tutor de QA Automation revisando os TESTES que um aluno escreveu.
Responda em portugues (PT-BR). Seja curto e direto.

REGRAS:
- NAO escreva os testes por ele. NAO mostre os testes certos.
- Avalie como um QA avaliaria testes: cobrem caminho feliz E casos de erro/limite?
  Os nomes dos test_* sao descritivos? Seguem Arrange/Act/Assert?
- De no maximo 1 ponto forte + 1 melhoria.
- Na ULTIMA linha escreva exatamente 'RESULT: PASS' se os testes estao bons
  (mataram os bugs plantados), ou 'RESULT: FAIL' se ficaram fracos.

EXERCICIO: {ex['title']}
CONTEXTO: {ex['context']}
INSTRUCOES:
{instr}
OS TESTES DO ALUNO MATARAM TODOS OS BUGS PLANTADOS (mutantes)? {"sim" if tests_passed else "nao"}

TESTES ESCRITOS PELO ALUNO:
```python
{code}
```
"""

    return f"""Voce e um tutor de Python para QA Automation revisando o codigo de um aluno.
Responda em portugues (PT-BR). Seja curto e direto.

REGRAS:
- NAO reescreva a solucao do aluno. NAO mostre o codigo certo.
- De no maximo 1 ponto forte + 1 melhoria.
- Pense como QA: edge cases, entradas invalidas, legibilidade.
- Na ULTIMA linha escreva exatamente 'RESULT: PASS' se o codigo resolve o
  enunciado, ou 'RESULT: FAIL' se nao resolve.

EXERCICIO: {ex['title']}
CONTEXTO: {ex['context']}
INSTRUCOES:
{instr}
TESTES AUTOMATICOS (Pyodide) PASSARAM? {"sim" if tests_passed else "nao"}

CODIGO DO ALUNO:
```python
{code}
```
"""


def grade_with_agy(ex, code, tests_passed):
    prompt = build_prompt(ex, code, tests_passed)
    try:
        out = subprocess.run(
            ["agy", "--print", prompt],
            capture_output=True, text=True, timeout=AGY_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "feedback": "agy demorou demais (timeout). Tenta de novo.", "passed": False}
    except FileNotFoundError:
        return {"ok": False, "feedback": "agy nao encontrado no PATH.", "passed": False}

    text = (out.stdout or "").strip()
    if not text:
        return {"ok": False, "feedback": "agy nao retornou nada.", "passed": False}

    passed = "RESULT: PASS" in text.upper()
    feedback = "\n".join(
        ln for ln in text.splitlines() if "RESULT:" not in ln.upper()
    ).strip()
    return {"ok": True, "feedback": feedback, "passed": passed}


def record_attempt(exercise_id, code, tests_passed):
    # try/finally garante fechar a conexao mesmo se grade_with_agy lancar (evita
    # vazamento de conexao -> "database is locked" com varios alunos). [agy review]
    conn = db()
    try:
        ex = conn.execute("SELECT * FROM exercises WHERE id=?", (exercise_id,)).fetchone()
        if ex is None:
            return {"error": "exercicio nao encontrado"}, 404

        result = grade_with_agy(dict(ex), code, tests_passed)

        prog = conn.execute(
            "SELECT * FROM progress WHERE exercise_id=?", (exercise_id,)
        ).fetchone()
        already_done = prog["status"] == "done"

        awarded = 0
        new_status = prog["status"]
        new_score = prog["score"]
        if result.get("passed") and not already_done:
            awarded = ex["points"]
            new_status = "done"
            new_score = ex["points"]

        conn.execute(
            """UPDATE progress
               SET status=?, score=?, attempts=attempts+1, last_code=?,
                   updated_at=datetime('now','localtime')
               WHERE exercise_id=?""",
            (new_status, new_score, code, exercise_id),
        )
        conn.commit()

        return {
            "feedback": result["feedback"],
            "passed": bool(result.get("passed")),
            "xp_awarded": awarded,
            "already_done": already_done,
        }, 200
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Servidor HTTP
# ---------------------------------------------------------------------------
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(HERE), **kw)

    def translate_path(self, path):
        clean = path.split("?", 1)[0].split("#", 1)[0]
        if clean.startswith("/course"):
            rel = clean[len("/course"):].lstrip("/")
            return str(COURSE_BUILD / rel) if rel else str(COURSE_BUILD / "index.html")
        return super().translate_path(path)

    def end_headers(self):
        p = self.path.split("?", 1)[0]
        # Pyodide (input()/Ctrl+C) precisa de SharedArrayBuffer -> COOP/COEP.
        # SO no curso: o dashboard usa Pyodide de CDN + iframe e quebraria com COEP global.
        if p.startswith("/course"):
            self.send_header("Cross-Origin-Opener-Policy", "same-origin")
            self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
            self.send_header("Cross-Origin-Resource-Policy", "cross-origin")
        # HTML nunca cacheia (senao o navegador serve um index.html velho que aponta
        # pro bundle antigo). Os assets com hash no nome continuam cacheaveis.
        if p.endswith("/") or p.endswith(".html") or p in ("", "/course"):
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def _service_worker_stub(self):
        stub = (
            b"self.addEventListener('install',e=>self.skipWaiting());\n"
            b"self.addEventListener('activate',async e=>{\n"
            b"  const ks=await caches.keys(); await Promise.all(ks.map(k=>caches.delete(k)));\n"
            b"  await self.registration.unregister();\n"
            b"  const cs=await self.clients.matchAll(); cs.forEach(c=>c.navigate(c.url));\n"
            b"});\n"
        )
        self.send_response(200)
        self.send_header("Content-Type", "application/javascript")
        self.send_header("Content-Length", str(len(stub)))
        self.end_headers()
        self.wfile.write(stub)

    def _json(self, payload, code=200):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/course":
            self.send_response(302)
            self.send_header("Location", "/course/")
            self.end_headers()
            return
        if path.endswith("service-worker.js"):
            return self._service_worker_stub()
        if self.path.startswith("/api/track"):
            return self._json(get_track())
        if self.path.startswith("/api/practice-progress"):
            return self._json(get_practice_progress())
        if self.path.startswith("/api/course-progress"):
            return self._json(get_course_progress())
        if self.path.startswith("/api/course"):
            return self._json({"course": COURSE, "attribution": ATTRIBUTION})
        return super().do_GET()  # serve dashboard, estaticos e /course/*

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(raw or b"{}")
        except ValueError:
            return self._json({"error": "json invalido"}, 400)

        if self.path.startswith("/api/grade"):
            payload, code = record_attempt(
                int(data.get("exercise_id")),
                data.get("code", ""),
                bool(data.get("tests_passed")),
            )
            return self._json(payload, code)
        if self.path.startswith("/api/course-progress"):
            save_course_progress(
                data.get("page_slug", ""),
                data.get("pages_progress", {}),
                data.get("editor_content", ""),
                data.get("pages_done", 0),
                data.get("pages_total", 0),
            )
            return self._json({"ok": True})
        if self.path.startswith("/api/save-code"):
            payload, code = save_code(data.get("slug", ""), data.get("code", ""))
            return self._json(payload, code)
        if self.path.startswith("/api/practice-progress"):
            payload, code = save_practice_progress(
                data.get("exercise_id", ""),
                data.get("xp", 0),
                data.get("mode", ""),
            )
            return self._json(payload, code)
        if self.path.startswith("/api/tutor"):
            payload, code = run_tutor(
                data.get("tutor", "agy"),
                data.get("context", ""),
                data.get("question", ""),
                data.get("code", ""),
            )
            return self._json(payload, code)
        self._json({"error": "rota desconhecida"}, 404)

    def log_message(self, *a):
        pass  # silencia o log barulhento


def main():
    init_db()
    print(f"Dashboard pronto -> http://localhost:{PORT}")
    print("Ctrl+C para parar.")
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nAte mais!")


if __name__ == "__main__":
    main()

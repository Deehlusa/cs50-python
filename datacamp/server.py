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
from datetime import datetime, timedelta
from pathlib import Path

from curriculum import TRACK, CHAPTERS

try:
    from course_data import COURSE, ATTRIBUTION
except ImportError:  # curso ainda não gerado (rodar: python3 build_course.py)
    COURSE, ATTRIBUTION = [], ""

try:
    from athena import orchestrator as _orchestrator  # camada de agentes (Athena)
    from athena import pedagogy as _pedagogy
    from athena import librarian as _librarian
    from athena import badges as _badges
except ImportError:  # pacote athena ausente — degrada sem quebrar o dashboard
    _orchestrator = None
    _pedagogy = None
    _librarian = None
    _badges = None

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
    # --- Athena AI Learning OS (SDD-ai-learning-os.md §A3) — tabelas aditivas ---
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS learner (
            id          INTEGER PRIMARY KEY CHECK (id = 1),
            name        TEXT DEFAULT '',
            level       INTEGER DEFAULT 0,
            xp          INTEGER DEFAULT 0,
            streak_days INTEGER DEFAULT 0,
            last_active TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS mastery (
            concept     TEXT PRIMARY KEY,
            strength    REAL DEFAULT 0,
            last_seen   TEXT DEFAULT '',
            next_review TEXT DEFAULT '',
            attempts    INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS events (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            ts      TEXT DEFAULT (datetime('now','localtime')),
            kind    TEXT DEFAULT '',
            ref     TEXT DEFAULT '',
            payload TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS agent_runs (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            ts       TEXT DEFAULT (datetime('now','localtime')),
            agent    TEXT DEFAULT '',
            task     TEXT DEFAULT '',
            provider TEXT DEFAULT '',
            status   TEXT DEFAULT '',
            tokens   INTEGER DEFAULT 0,
            notes    TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS content_queue (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            chapter  TEXT DEFAULT '',
            kind     TEXT DEFAULT '',
            state    TEXT DEFAULT 'todo',
            priority INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS memory (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            ts    TEXT DEFAULT (datetime('now','localtime')),
            kind  TEXT DEFAULT '',          -- decision | session | content
            title TEXT DEFAULT '',
            body  TEXT DEFAULT '',
            tags  TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS user_badges (
            user_id     INTEGER DEFAULT 1,
            badge_id    TEXT,
            unlocked_at TEXT DEFAULT (datetime('now','localtime')),
            PRIMARY KEY (user_id, badge_id)
        );
        """
    )
    conn.execute("INSERT OR IGNORE INTO learner (id) VALUES (1)")
    # Migração ADITIVA: coluna learner.mode ("python"|"qa") — modo de aprendizado. CREATE TABLE
    # IF NOT EXISTS não altera tabela já existente, então adicionamos a coluna sob demanda.
    _cols = {r[1] for r in conn.execute("PRAGMA table_info(learner)")}
    if "mode" not in _cols:
        conn.execute("ALTER TABLE learner ADD COLUMN mode TEXT DEFAULT 'python'")
    # Migração ADITIVA (GAP-5): coluna practice_progress.code — guarda o último código que
    # PASSOU em cada exercício da prática, pra sobreviver à limpeza do localStorage (checkpoint).
    _pcols = {r[1] for r in conn.execute("PRAGMA table_info(practice_progress)")}
    if "code" not in _pcols:
        conn.execute("ALTER TABLE practice_progress ADD COLUMN code TEXT DEFAULT ''")
    # Seed do backlog do Orchestrator no content_queue — uma vez, só se a fila estiver vazia
    # (o estado de execução vive aqui; o backlog "fonte" é o athena.orchestrator).
    if _orchestrator is not None:
        empty = conn.execute("SELECT COUNT(*) c FROM content_queue").fetchone()[0] == 0
        if empty:
            conn.executemany(
                "INSERT INTO content_queue (chapter, kind, state, priority) VALUES (?,?,?,?)",
                [(i["chapter"], i["kind"], i["state"], i["priority"])
                 for i in _orchestrator.MVP_BACKLOG],
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
    prev = conn.execute("SELECT pages_done FROM course_progress WHERE id=1").fetchone()
    prev_done = (prev["pages_done"] if prev else 0) or 0
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
    # evento de página só quando o nº de páginas concluídas AUMENTA (anti-spam do debounce).
    if int(pages_done or 0) > int(prev_done):
        log_event("page", ref=str(page_slug or ""), source="course",
                  payload={"pages_done": int(pages_done or 0), "pages_total": int(pages_total or 0)})
        evaluate_badges()  # 1ª página pode desbloquear first_step
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


def save_practice_progress(exercise_id, xp, mode, code=""):
    """Espelha a conclusao de um exercicio do painel Pratique no SQLite.

    Na 1a conclusao de cada exercicio, sobe o dominio do conceito correspondente (Mastery
    Tracker). Idempotente por exercise_id: refazer o mesmo exercicio NAO refarma o dominio.
    `code` (GAP-5): guarda o codigo que passou — atualizado a cada conclusao (checkpoint que
    sobrevive a limpeza do localStorage). `code` e opcional p/ nao quebrar chamadas antigas.
    """
    if not exercise_id:
        return {"ok": False, "error": "sem exercise_id"}, 400
    conn = db()
    try:
        # BEGIN IMMEDIATE serializa submits concorrentes do MESMO exercício: só o 1º
        # vê already=False e sobe mastery (evita duplo-bump/evento em double-click ou rede lenta).
        conn.execute("BEGIN IMMEDIATE")
        already = conn.execute(
            "SELECT 1 FROM practice_progress WHERE exercise_id=?", (str(exercise_id),)
        ).fetchone() is not None
        conn.execute(
            """INSERT INTO practice_progress (exercise_id, xp, mode, code, updated_at)
               VALUES (?,?,?,?,datetime('now','localtime'))
               ON CONFLICT(exercise_id) DO UPDATE SET
                   xp=excluded.xp, mode=excluded.mode,
                   -- só sobrescreve o checkpoint com código NÃO-vazio: um chamador antigo
                   -- (3 args, code='') não pode apagar o código já salvo do aluno.
                   code=CASE WHEN excluded.code != '' THEN excluded.code ELSE practice_progress.code END,
                   updated_at=datetime('now','localtime')""",
            (str(exercise_id), int(xp or 0), str(mode or ""), str(code or "")),
        )
        conn.commit()
    finally:
        conn.close()
    bumped = None
    if not already:
        # evento de prática (conta TODA 1ª conclusão, mesmo sem conceito mapeado).
        log_event("practice", ref=str(exercise_id), source="practice",
                  payload={"mode": str(mode or ""), "xp": int(xp or 0)})
        if _pedagogy is not None:
            concept = _pedagogy.concept_for_exercise(str(exercise_id), str(mode or ""))
            if concept:
                record_mastery(concept, True, source="practice")  # 1a conclusao = acerto
                bumped = concept
    return {"ok": True, "mastery_bumped": bumped}, 200


def get_practice_progress():
    conn = db()
    rows = conn.execute(
        "SELECT exercise_id, xp, mode, code, updated_at FROM practice_progress"
    ).fetchall()
    conn.close()
    items = [dict(r) for r in rows]
    return {"items": items, "count": len(items), "xp": sum(i["xp"] for i in items)}


# ---------------------------------------------------------------------------
# Athena AI Learning OS — auditoria do /loop (SDD §A3, tabela agent_runs)
# ---------------------------------------------------------------------------
def record_agent_run(agent, task, provider, status="ok", tokens=0, notes=""):
    """Registra uma execucao de agente do /loop. Provider deve seguir o roteamento (SDD §A4)."""
    if not agent:
        return {"ok": False, "error": "sem agent"}, 400
    conn = db()
    cur = conn.execute(
        """INSERT INTO agent_runs (agent, task, provider, status, tokens, notes)
           VALUES (?,?,?,?,?,?)""",
        (str(agent), str(task or ""), str(provider or ""),
         str(status or "ok"), int(tokens or 0), str(notes or "")),
    )
    run_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {"ok": True, "id": run_id}, 200


def get_agent_runs(limit=50):
    conn = db()
    rows = conn.execute(
        "SELECT id, ts, agent, task, provider, status, tokens, notes "
        "FROM agent_runs ORDER BY id DESC LIMIT ?",
        (int(limit),),
    ).fetchall()
    conn.close()
    items = [dict(r) for r in rows]
    return {"items": items, "count": len(items)}


def index_memory(kind, title, body, tags=""):
    """Indexa uma entrada (decisão/sessão/conteúdo) na memória do Librarian (#13)."""
    if not (title or body):
        return {"ok": False, "error": "memória vazia"}, 400
    conn = db()
    cur = conn.execute(
        "INSERT INTO memory (kind, title, body, tags) VALUES (?,?,?,?)",
        (str(kind or ""), str(title or ""), str(body or ""), str(tags or "")),
    )
    mid = cur.lastrowid
    conn.commit()
    conn.close()
    return {"ok": True, "id": mid}, 200


def recall_memory(query, limit=5):
    """Recupera as entradas mais relevantes p/ a query (recall por palavra-chave)."""
    if _librarian is None:
        return {"items": [], "count": 0}
    conn = db()
    rows = conn.execute("SELECT id, ts, kind, title, body, tags FROM memory").fetchall()
    conn.close()
    entries = [dict(r) for r in rows]
    hits = _librarian.recall(query or "", entries, int(limit))
    return {"items": hits, "count": len(hits)}


def get_plan():
    """Plano do Orchestrator (SDD §C3): backlog MVP + progresso + próximo item 'todo'."""
    if _orchestrator is None:
        return {"backlog": [], "progress": {"done": 0, "total": 0}, "next": {}}
    return {
        "backlog": _orchestrator.backlog(),
        "progress": _orchestrator.progress(),
        "next": _orchestrator.next_todo(),
    }


# ---------------------------------------------------------------------------
# Events — log append-only de eventos REAIS de aprendizagem (base do badge engine).
# Reusa a tabela `events (id, ts, kind, ref, payload)` — NÃO altera schema: a origem
# (`source`) e os detalhes vão no `payload` JSON. Política anti-duplicidade (alto sinal):
#   • page     → só quando pages_done AUMENTA (não a cada save debounced).
#   • practice → só na 1ª conclusão de cada exercício (idempotente por exercise_id).
#   • mastery  → 1 por tentativa REAL (os chamadores já filtram por "1ª vez"); `source`
#                distingue practice/grade/api. (Um practice 1ª-vez emite practice+mastery:
#                payloads complementares — practice traz `mode`, mastery traz `strength`.)
# ---------------------------------------------------------------------------
def log_event(kind, ref="", payload=None, source=""):
    """Insere 1 linha append-only em `events`. Best-effort: NUNCA derruba a rota real."""
    body = dict(payload or {})
    if source:
        body["source"] = source
    try:
        conn = db()
        conn.execute(
            "INSERT INTO events (kind, ref, payload) VALUES (?,?,?)",
            (str(kind), str(ref or ""), json.dumps(body, ensure_ascii=False)),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass  # instrumentação não pode quebrar o fluxo principal


def get_events(limit=50):
    """Últimos eventos (rota de DEBUG /api/events), mais recentes primeiro."""
    conn = db()
    rows = conn.execute(
        "SELECT id, ts, kind, ref, payload FROM events ORDER BY id DESC LIMIT ?",
        (int(limit),),
    ).fetchall()
    conn.close()
    items = []
    for r in rows:
        try:
            pl = json.loads(r["payload"]) if r["payload"] else {}
        except Exception:
            pl = {}
        items.append({"id": r["id"], "ts": r["ts"], "kind": r["kind"],
                      "ref": r["ref"], "source": pl.get("source", ""), "payload": pl})
    return {"items": items, "count": len(items)}


# ---------------------------------------------------------------------------
# Badges (MVP Loop 2) — avaliação persistida ligada a aprendizagem real.
# Regras puras em athena/badges.py; aqui mora a leitura do estado + persistência
# (tabela `user_badges`, INSERT idempotente). Aluno único (id=1), como o resto do app.
# ---------------------------------------------------------------------------
def _badge_context():
    """Monta o ctx para badges.evaluate a partir de mastery + course_progress."""
    rows = _mastery_rows()  # [{concept,label,level,strength,next_review}]
    strength = {r["concept"]: r["strength"] for r in rows}
    rows2 = [{"concept": r["concept"], "strength": r["strength"], "level": r["level"],
              "mastered": r["strength"] >= _pedagogy.MASTERED} for r in rows]
    conn = db()
    row = conn.execute("SELECT pages_done FROM course_progress WHERE id=1").fetchone()
    conn.close()
    pages_done = (row["pages_done"] if row else 0) or 0
    return {"rows": rows2, "strength": strength, "pages_done": int(pages_done)}


def evaluate_badges():
    """Avalia as regras e grava em user_badges os novos (INSERT OR IGNORE = idempotente).

    Retorna a lista de ids RECÉM-desbloqueados (para a UI futura celebrar). Best-effort.
    """
    if _badges is None or _pedagogy is None:
        return []
    try:
        satisfied = _badges.evaluate(_badge_context())
    except Exception:
        return []
    newly = []
    conn = db()
    try:  # try/finally fecha a conexão mesmo em erro (padrão de record_attempt — evita lock)
        for bid in satisfied:
            cur = conn.execute(
                """INSERT OR IGNORE INTO user_badges (user_id, badge_id, unlocked_at)
                   VALUES (1, ?, datetime('now','localtime'))""",
                (str(bid),),
            )
            if cur.rowcount > 0:
                newly.append(bid)
        conn.commit()
    finally:
        conn.close()
    return newly


def get_badges():
    """Estado dos badges do aluno (rota /api/badges) — definições + flag unlocked."""
    conn = db()
    rows = conn.execute("SELECT badge_id, unlocked_at FROM user_badges WHERE user_id=1").fetchall()
    conn.close()
    unlocked = {r["badge_id"]: r["unlocked_at"] for r in rows}
    defs = _badges.BADGE_DEFS if _badges else []
    items = [{
        "id": b["id"], "name": b["name"], "icon": b["icon"], "track": b["track"],
        "desc": b.get("desc", ""), "unlocked": b["id"] in unlocked,
        "unlocked_at": unlocked.get(b["id"], ""),
    } for b in defs]
    return {"items": items, "unlocked": len(unlocked), "total": len(items)}


# ---------------------------------------------------------------------------
# Athena — Progress Analyst (#9) + Mastery Tracker (#8): SDD §A2/§B6
# ---------------------------------------------------------------------------
def _mastery_map():
    """{concept_key: strength} a partir da tabela mastery."""
    conn = db()
    rows = conn.execute("SELECT concept, strength FROM mastery").fetchall()
    conn.close()
    return {r["concept"]: r["strength"] for r in rows}


def _mastery_rows():
    """[{concept,label,level,strength,next_review}] na ordem do currículo (inclui agendamento).

    Mescla a tabela mastery com CONCEPTS para o Progress Analyst decidir entre revisão
    espaçada vencida e conceito novo.
    """
    conn = db()
    rows = conn.execute("SELECT concept, strength, next_review FROM mastery").fetchall()
    conn.close()
    by_key = {r["concept"]: r for r in rows}
    out = []
    for c in _pedagogy.CONCEPTS:
        r = by_key.get(c["key"])
        out.append({
            "concept": c["key"], "label": c["label"], "level": c["level"],
            "strength": r["strength"] if r else 0.0,
            "next_review": r["next_review"] if r else "",
        })
    return out


def get_learner():
    """Perfil do aluno (singleton id=1): inclui o modo de aprendizado ('python'|'qa')."""
    conn = db()
    row = conn.execute(
        "SELECT name, level, xp, streak_days, mode FROM learner WHERE id=1"
    ).fetchone()
    conn.close()
    mode = (row["mode"] if row and "mode" in row.keys() else None) or "python"
    return {
        "name": row["name"] if row else "",
        "level": row["level"] if row else 0,
        "xp": row["xp"] if row else 0,
        "streak_days": row["streak_days"] if row else 0,
        "mode": mode if mode in ("python", "qa") else "python",
    }


def set_learner_mode(mode):
    """Define o modo de aprendizado. Aceita só 'python'|'qa'; senão devolve erro 400."""
    valid = getattr(_pedagogy, "VALID_MODES", ("python", "qa")) if _pedagogy else ("python", "qa")
    if mode not in valid:
        return {"ok": False, "error": f"modo invalido (use {' ou '.join(valid)})"}, 400
    conn = db()
    try:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("UPDATE learner SET mode=? WHERE id=1", (mode,))
        conn.commit()
    finally:
        conn.close()
    log_event("learner_mode", ref=mode, source="learner")
    return {"ok": True, "mode": mode}, 200


def get_next():
    """Próxima ação: revisão espaçada vencida tem prioridade; senão, próximo conceito novo.

    Respeita o MODO do aluno: 'python' segue só a base (suave); 'qa' puxa as trilhas QA cedo.
    """
    if _pedagogy is None:
        return {}
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return _pedagogy.next_action(_mastery_rows(), now, get_learner()["mode"])


def get_mastery():
    """Mapa de domínio por conceito (módulo H), na ordem do currículo."""
    if _pedagogy is None:
        return {"items": [], "mastered": 0, "total": 0}
    current = _mastery_map()
    items = []
    for c in _pedagogy.CONCEPTS:
        strength = current.get(c["key"], 0.0)
        items.append({
            "concept": c["key"], "label": c["label"], "level": c["level"],
            "strength": strength, "mastered": strength >= _pedagogy.MASTERED,
        })
    mastered = sum(1 for i in items if i["mastered"])
    return {"items": items, "mastered": mastered, "total": len(items)}


def record_mastery(concept, correct, source=""):
    """Atualiza o domínio de um conceito após uma tentativa (curva de aprendizagem).

    `source` = origem do sinal (practice|grade|api), registrada no log de eventos.
    """
    if not concept:
        return {"ok": False, "error": "sem concept"}, 400
    if _pedagogy is None:
        return {"ok": False, "error": "athena ausente"}, 500
    conn = db()
    row = conn.execute(
        "SELECT strength, attempts, next_review FROM mastery WHERE concept=?", (str(concept),)
    ).fetchone()
    cur_strength = row["strength"] if row else 0.0
    attempts = (row["attempts"] if row else 0) + 1
    new_strength = _pedagogy.update_strength(cur_strength, bool(correct))
    # Repetição espaçada: agenda a próxima revisão (intervalo cresce com o domínio).
    now_dt = datetime.now()
    last_seen = now_dt.strftime("%Y-%m-%d %H:%M:%S")
    # Era uma revisão vencida? (sinal p/ o futuro badge "review streak", Loop 4)
    was_review = _pedagogy.is_due(row["next_review"] if row else "", last_seen)
    interval = _pedagogy.review_interval_days(new_strength)
    next_review = (now_dt + timedelta(days=interval)).strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        """INSERT INTO mastery (concept, strength, last_seen, next_review, attempts)
           VALUES (?,?,?,?,?)
           ON CONFLICT(concept) DO UPDATE SET
               strength=excluded.strength,
               last_seen=excluded.last_seen,
               next_review=excluded.next_review,
               attempts=excluded.attempts""",
        (str(concept), new_strength, last_seen, next_review, attempts),
    )
    conn.commit()
    conn.close()
    mastered = new_strength >= _pedagogy.MASTERED
    log_event("mastery", ref=str(concept), source=source, payload={
        "strength": new_strength, "mastered": mastered,
        "attempts": attempts, "review": bool(was_review),
    })
    evaluate_badges()  # avalia/persiste badges após mudança de domínio (idempotente)
    return {"ok": True, "concept": str(concept), "strength": new_strength,
            "mastered": mastered, "next_review": next_review}, 200


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


_MODE_FRAMING = {
    "python": ("MODO DO ALUNO: Python base. Foque na lógica e nos fundamentos; explique com "
               "calma, sem empurrar testes/QA ainda. Só mencione QA se o aluno perguntar."),
    "qa": ("MODO DO ALUNO: QA Automation. Conecte cada conceito a 'como eu testaria isso' "
           "(casos de borda, asserts, função pura = testável), reforçando a mentalidade de quem quebra o código."),
}


def build_tutor_prompt(context, question, code, mode="python"):
    code = code or "(o aluno ainda nao escreveu codigo)"
    question = (question or "").strip() or "O aluno pediu ajuda, mas nao escreveu a duvida."
    framing = _MODE_FRAMING.get(mode, _MODE_FRAMING["python"])
    return f"""{TUTOR_RULES}

{framing}

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
    prompt = build_tutor_prompt(context, question, code, get_learner()["mode"])
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
    bump_concept = None
    try:
        ex = conn.execute("SELECT * FROM exercises WHERE id=?", (exercise_id,)).fetchone()
        if ex is None:
            return {"error": "exercicio nao encontrado"}, 404

        # grade_with_agy é lento (subprocess até 180s) -> roda FORA da transação para
        # não segurar o write-lock. A serialização do bump vem do BEGIN IMMEDIATE abaixo.
        result = grade_with_agy(dict(ex), code, tests_passed)

        # BEGIN IMMEDIATE serializa submits concorrentes do MESMO exercício: só o 1º vê
        # already_done=False e premia/sobe mastery (mesma garantia de save_practice_progress;
        # evita XP/mastery em dobro num double-click ou retry de rede). [QA: grade race]
        conn.execute("BEGIN IMMEDIATE")
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
            # Unifica o dashboard com a MESMA curva de mastery da prática (Athena §A3):
            # 1a aprovação de um exercício do painel sobe o domínio do conceito do capítulo.
            if _pedagogy is not None:
                ex_type = ex["type"] if "type" in ex.keys() else ""
                bump_concept = _pedagogy.concept_for_chapter(ex["chapter"], ex_type)

        conn.execute(
            """UPDATE progress
               SET status=?, score=?, attempts=attempts+1, last_code=?,
                   updated_at=datetime('now','localtime')
               WHERE exercise_id=?""",
            (new_status, new_score, code, exercise_id),
        )
        conn.commit()

        payload = {
            "feedback": result["feedback"],
            "passed": bool(result.get("passed")),
            "xp_awarded": awarded,
            "already_done": already_done,
        }
    finally:
        conn.close()

    # bump DEPOIS de fechar a conexão principal — record_mastery abre a sua (evita lock).
    if bump_concept:
        record_mastery(bump_concept, True, source="grade")
        payload["mastery_bumped"] = bump_concept
    return payload, 200


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
        # Raiz agora abre o CURSO (futurecoder) — é a plataforma principal. O dashboard
        # legado continua acessível direto em /index.html.
        if path in ("", "/"):
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
        if self.path.startswith("/api/agent-run"):
            return self._json(get_agent_runs())
        if self.path.startswith("/api/events"):
            from urllib.parse import urlparse, parse_qs
            q = parse_qs(urlparse(self.path).query)
            raw = (q.get("limit") or ["50"])[0]
            limit = int(raw) if str(raw).isdigit() else 50   # nunca 500 em ?limit=abc
            return self._json(get_events(limit))
        if self.path.startswith("/api/badges"):
            return self._json(get_badges())
        if self.path.startswith("/api/plan"):
            return self._json(get_plan())
        if self.path.startswith("/api/next"):
            return self._json(get_next())
        if self.path.startswith("/api/learner"):
            return self._json(get_learner())
        if self.path.startswith("/api/mastery"):
            return self._json(get_mastery())
        if self.path.startswith("/api/memory"):
            from urllib.parse import urlparse, parse_qs
            q = parse_qs(urlparse(self.path).query)
            query = (q.get("q") or [""])[0]
            limit = int((q.get("limit") or ["5"])[0])
            return self._json(recall_memory(query, limit))
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
                data.get("code", ""),
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
        if self.path.startswith("/api/agent-run"):
            payload, code = record_agent_run(
                data.get("agent", ""),
                data.get("task", ""),
                data.get("provider", ""),
                data.get("status", "ok"),
                data.get("tokens", 0),
                data.get("notes", ""),
            )
            return self._json(payload, code)
        if self.path.startswith("/api/learner"):
            payload, code = set_learner_mode(data.get("mode", ""))
            return self._json(payload, code)
        if self.path.startswith("/api/mastery"):
            payload, code = record_mastery(
                data.get("concept", ""),
                bool(data.get("correct", False)),
                source="api",
            )
            return self._json(payload, code)
        if self.path.startswith("/api/memory"):
            payload, code = index_memory(
                data.get("kind", ""),
                data.get("title", ""),
                data.get("body", ""),
                data.get("tags", ""),
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

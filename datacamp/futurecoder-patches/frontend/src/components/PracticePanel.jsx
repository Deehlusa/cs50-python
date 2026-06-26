// PracticePanel — painel "🏋️ Pratique" por capítulo (formato 30 Days, 3 níveis).
// O aluno escreve o código; a plataforma roda no Pyodide e dá dicas em escada
// (nunca a solução). Modo write_code (escreve a função) e write_test (escreve o
// teste, avaliado por mutation testing). Persiste em localStorage + servidor.

import React from "react";
import exercisesBr from "../exercises_br.json";
import {runExercise, stopExercise} from "./PyodideRunner";
import {savePracticeProgress} from "../book/serverSync";

const PRACTICE_KEY = "futurecoder_practice_v1";

function loadProgress() {
  try { return JSON.parse(localStorage.getItem(PRACTICE_KEY) || "{}"); } catch (e) { return {}; }
}
function persist(p) {
  try { localStorage.setItem(PRACTICE_KEY, JSON.stringify(p)); } catch (e) {}
  window.dispatchEvent(new Event("practice-updated"));
}

export function practiceStats() {
  const vals = Object.values(loadProgress());
  return {
    count: vals.length,
    xp: vals.reduce((s, e) => s + (e.xp || 0), 0),
    wroteTest: vals.some(e => e.mode === "write_test"),
  };
}

// ── Streak diário (🔥) ──────────────────────────────────────────────────────
const STREAK_KEY = "futurecoder_streak_v1";
function todayStr(d) {
  d = d || new Date();
  return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
}
export function getStreak() {
  try { return JSON.parse(localStorage.getItem(STREAK_KEY) || '{"last":null,"count":0,"best":0}'); }
  catch (e) { return {last: null, count: 0, best: 0}; }
}
function touchStreak() {
  const s = getStreak();
  const t = todayStr();
  if (s.last === t) return s;            // já praticou hoje
  const y = new Date(); y.setDate(y.getDate() - 1);
  s.count = (s.last === todayStr(y)) ? (s.count || 0) + 1 : 1;  // ontem? continua; senão reinicia
  s.last = t;
  s.best = Math.max(s.best || 0, s.count);
  try { localStorage.setItem(STREAK_KEY, JSON.stringify(s)); } catch (e) {}
  window.dispatchEvent(new Event("practice-updated"));
  return s;
}

// Hint de 1ª execução do Pyodide (download ~15s só na 1ª vez).
let __pyodideWarmed = false;

// Mapeia título do capítulo (NFC) -> bloco de exercícios.
const exMap = {};
Object.keys(exercisesBr).forEach(k => { if (k !== "_meta") exMap[k.normalize("NFC")] = exercisesBr[k]; });
function getExercisesForChapter(title) {
  if (!title) return null;
  return exMap[title.normalize("NFC")] || null;
}

const LEVEL_LABEL = {1: "N1 · Aquecimento", 2: "N2 · Combinar", 3: "N3 · Mini-projeto"};

function Feedback({result}) {
  if (!result) return null;
  if (result.info) return <div className="practice-feedback info">⏳ {result.info}</div>;
  if (result.error) return <div className="practice-feedback err">⚠ {result.error}</div>;
  if (result.mode === "write_code") {
    return (
      <div className={"practice-feedback " + (result.ok ? "ok" : "fail")}>
        <div className="practice-feedback-head">
          {result.ok ? "✅ Todos os casos passaram!" : "❌ Alguns casos falharam:"}
        </div>
        <ul className="practice-cases">
          {(result.results || []).map((r, i) => (
            <li key={i} className={r.passed ? "pass" : "fail"}>
              <code>{r.call}</code> → esperado <code>{r.expect}</code>, obtido <code>{r.actual}</code> {r.passed ? "✓" : "✗"}
            </li>
          ))}
        </ul>
      </div>
    );
  }
  return (
    <div className={"practice-feedback " + (result.ok ? "ok" : "fail")}>
      <div className="practice-feedback-head">
        {result.ok ? "✅ Seus testes mataram todos os bugs!" : "❌ Ainda não — veja o que falta:"}
      </div>
      <ul className="practice-cases">
        <li className={result.ref_ok ? "pass" : "fail"}>
          Seus testes passam na função correta {result.ref_ok ? "✓" : "✗ (revise seus asserts)"}
        </li>
        <li className={result.enough ? "pass" : "fail"}>
          {result.n_tests}/{result.min_tests} testes mínimos {result.enough ? "✓" : "✗"}
        </li>
        {(result.mutants || []).map((m, i) => (
          <li key={i} className={m.killed ? "pass" : "fail"}>
            Bug #{i + 1}: {m.killed ? "morto ✓" : "sobreviveu ✗ — seu teste não cobriu este caso"}
          </li>
        ))}
      </ul>
    </div>
  );
}

function ExerciseCard({ex, done, onDone}) {
  const [code, setCode] = React.useState(ex.starter || "");
  const [running, setRunning] = React.useState(false);
  const [result, setResult] = React.useState(null);
  const [hintLevel, setHintLevel] = React.useState(0);

  const run = async () => {
    setRunning(true);
    setResult(__pyodideWarmed ? null : {info: "Carregando o Python no navegador (só na 1ª vez, ~10-15s)…"});
    const r = await runExercise(ex, code);
    __pyodideWarmed = true;
    setResult(r);
    setRunning(false);
    if (r && r.ok) {
      touchStreak();
      if (!done) onDone(ex);
    }
  };

  const onKeyDown = (e) => {
    if (e.key === "Tab") {            // Tab indenta (4 espaços) em vez de mudar o foco
      e.preventDefault();
      const el = e.target;
      const s = el.selectionStart, en = el.selectionEnd;
      setCode(el.value.slice(0, s) + "    " + el.value.slice(en));
      requestAnimationFrame(() => { el.selectionStart = el.selectionEnd = s + 4; });
    }
  };

  const hints = ex.hints || [];
  return (
    <div className={"practice-card " + (done ? "done" : "")}>
      <div className="practice-card-head">
        <span className={"practice-level lvl-" + ex.level}>{LEVEL_LABEL[ex.level] || ("N" + ex.level)}</span>
        <span className="practice-card-title">{ex.title}</span>
        <span className="practice-card-xp">{done ? "✓ " : ""}{ex.xp} XP</span>
      </div>
      <div className="practice-prompt">{ex.prompt}</div>
      <textarea
        className="practice-editor"
        spellCheck={false}
        value={code}
        onChange={e => setCode(e.target.value)}
        onKeyDown={onKeyDown}
        rows={Math.max(4, code.split("\n").length + 1)}
      />
      <div className="practice-actions">
        <button className="btn btn-primary btn-sm practice-run" disabled={running} onClick={run}>
          {running ? "Rodando…" : "▶ Rodar"}
        </button>
        {running &&
          <button className="btn btn-sm practice-stop" onClick={() => stopExercise()}>■ Parar</button>}
        {hintLevel < hints.length &&
          <button className="btn btn-sm practice-hint-btn" onClick={() => setHintLevel(h => h + 1)}>
            💡 Dica {hintLevel + 1}/{hints.length}
          </button>}
        <button className="btn btn-sm practice-reset" onClick={() => { setCode(ex.starter || ""); setResult(null); }}>
          ↺ Reiniciar
        </button>
      </div>
      {hintLevel > 0 &&
        <div className="practice-hints">
          {hints.slice(0, hintLevel).map((h, i) => (
            <div key={i} className="practice-hint"><span className="practice-hint-n">{i + 1}.</span> <code>{h}</code></div>
          ))}
        </div>}
      <Feedback result={result}/>
    </div>
  );
}

export const PracticePanel = ({chapterTitle}) => {
  const [open, setOpen] = React.useState(false);
  const [progress, setProgress] = React.useState(loadProgress());
  const chapter = getExercisesForChapter(chapterTitle);
  if (!chapter || !chapter.exercises || !chapter.exercises.length) return null;

  const onDone = (ex) => {
    const p = loadProgress();
    if (!p[ex.id]) {
      p[ex.id] = {done: true, xp: ex.xp || 0, mode: ex.mode};
      persist(p);
      setProgress({...p});
      try { savePracticeProgress(ex.id, ex.xp || 0, ex.mode); } catch (e) {}
    }
  };

  const exercises = chapter.exercises.slice().sort((a, b) => (a.level || 0) - (b.level || 0));
  const doneCount = exercises.filter(e => progress[e.id]).length;

  return (
    <div className="practice-panel">
      <button className="practice-trigger" onClick={() => setOpen(o => !o)} aria-expanded={open}>
        <span>🏋️ Pratique <span className="practice-count">{doneCount}/{exercises.length}</span></span>
        <span className="practice-arrow">{open ? "▲" : "▼"}</span>
      </button>
      {open &&
        <div className="practice-body">
          <div className="practice-intro">
            Você escreve o código — a plataforma roda e te guia com dicas, nunca entrega a solução pronta.
          </div>
          {exercises.map(ex => (
            <ExerciseCard key={ex.id} ex={ex} done={!!progress[ex.id]} onDone={onDone}/>
          ))}
        </div>}
    </div>
  );
};

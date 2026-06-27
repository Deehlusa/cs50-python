// PracticePanel — painel "🏋️ Pratique" por capítulo (formato 30 Days, 3 níveis).
// O aluno escreve o código; a plataforma roda no Pyodide e dá dicas em escada
// (nunca a solução). Modo write_code (escreve a função) e write_test (escreve o
// teste, avaliado por mutation testing). Persiste em localStorage + servidor.

import React from "react";
import exercisesBr from "../exercises_br.json";
import {runExercise, stopExercise} from "./PyodideRunner";
import {savePracticeProgress, getPracticeProgress} from "../book/serverSync";

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
        {!result.ok &&
          <div className="practice-next-hint">
            💡 Próximo passo: olhe o <b>primeiro caso vermelho</b> — compare o que sua função devolveu
            com o esperado. Travou? Clique em <b>Dica</b>.
          </div>}
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
      {!result.ok &&
        <div className="practice-next-hint">
          🛡️ Mentalidade QA: para cada <b>bug que sobreviveu</b>, adicione um <code>assert</code> com
          um caso que o exponha. Pense em entradas-limite (vazio, zero, negativo).
        </div>}
    </div>
  );
}

function ExerciseCard({ex, done, saved, onDone}) {
  // Restaura o CÓDIGO que passou (checkpoint) ao montar/F5; senão começa do starter.
  const [code, setCode] = React.useState((saved && saved.code) || ex.starter || "");
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
      onDone(ex, code);   // salva/atualiza o checkpoint do código que passou
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
      {ex.concept_intro &&
        <div className="practice-concept-intro">{ex.concept_intro}</div>}
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
        {saved && saved.code && saved.code !== code &&
          <button className="btn btn-sm practice-checkpoint"
                  title="Restaura o código que você fez passar neste exercício"
                  onClick={() => { setCode(saved.code); setResult(null); }}>
            🚩 Recuperar meu código que passou
          </button>}
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
  // Auto-abre quando o capítulo tem exercício NÃO feito: a prática (XP/badges/streak)
  // ficava colapsada abaixo da dobra e muitos alunos nunca a descobriam. [UX fora do Athena]
  const autoOpen = () => {
    const ch = getExercisesForChapter(chapterTitle);
    const p = loadProgress();
    return !!(ch && ch.exercises && ch.exercises.some(e => !p[e.id]));
  };
  const [open, setOpen] = React.useState(autoOpen);
  // Reavalia ao TROCAR de capítulo (navegar entre páginas do mesmo capítulo preserva o
  // toggle manual, pois chapterTitle não muda).
  React.useEffect(() => { setOpen(autoOpen()); }, [chapterTitle]);  // eslint-disable-line
  const [progress, setProgress] = React.useState(loadProgress());
  const [syncWarn, setSyncWarn] = React.useState("");
  // GAP-5: hidrata do servidor o código que passou quando o localStorage está vazio (ou sem
  // code) para esse exercício. O localStorage segue como camada rápida (não sobrescreve o que
  // já existe localmente). Roda 1x no mount; best-effort (server off → não faz nada).
  React.useEffect(() => {
    let alive = true;
    getPracticeProgress().then(({items}) => {
      if (!alive || !items || !items.length) return;
      const p = loadProgress();
      let changed = false;
      items.forEach(it => {
        const id = it.exercise_id;
        const local = p[id];
        if (it.code && (!local || !local.code)) {
          p[id] = {
            done: true, xp: it.xp || (local && local.xp) || 0,
            mode: it.mode || (local && local.mode) || "", code: it.code,
          };
          changed = true;
        }
      });
      if (changed) { persist(p); setProgress({...p}); }
    });
    return () => { alive = false; };
  }, []);  // eslint-disable-line
  const chapter = getExercisesForChapter(chapterTitle);
  if (!chapter || !chapter.exercises || !chapter.exercises.length) return null;

  const onDone = async (ex, code) => {
    const p = loadProgress();
    // Guarda o CÓDIGO que passou (checkpoint): sobrevive ao F5 e dá pra recuperar depois.
    p[ex.id] = {
      done: true, xp: ex.xp || 0, mode: ex.mode,
      code: code != null ? code : (p[ex.id] && p[ex.id].code) || "",
    };
    persist(p);
    setProgress({...p});
    // GAP-5: sincroniza XP/mastery (o servidor é idempotente: só a 1ª conclusão sobe domínio)
    // E persiste o código que passou no servidor a cada conclusão (checkpoint sempre fresco).
    // Se falhar, AVISA — o progresso local segue seguro.
    const res = await savePracticeProgress(ex.id, ex.xp || 0, ex.mode, p[ex.id].code);
    if (!res || !res.ok) {
      setSyncWarn("Salvo localmente, mas a sincronização com o servidor falhou ("
        + ((res && res.error) || "desconhecido") + "). Seu progresso local está seguro.");
    } else {
      setSyncWarn("");
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
            {doneCount === 0
              ? <> Comece pelo <b>N1 (aquecimento)</b> e suba de nível.</>
              : <> {doneCount}/{exercises.length} feitos — continue de onde parou.</>}
          </div>
          {syncWarn &&
            <div className="practice-syncwarn">⚠ {syncWarn}</div>}
          {exercises.map(ex => (
            // key inclui se já há code salvo: quando a hidratação do servidor (GAP-5) traz o
            // código que passou para um exercício que estava sem code local, a key vira "…:s" e
            // o card remonta UMA vez restaurando o código (sem perder edição — só no 1º load).
            <ExerciseCard key={ex.id + (progress[ex.id] && progress[ex.id].code ? ":s" : ":n")}
                          ex={ex} done={!!progress[ex.id]}
                          saved={progress[ex.id]} onDone={onDone}/>
          ))}
        </div>}
    </div>
  );
};

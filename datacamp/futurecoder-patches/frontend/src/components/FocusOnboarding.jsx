import React from "react";

// GAP-1 — Onboarding do modo de aprendizado (python | qa). O motor já existe no
// server.py (learner.mode + GET/POST /api/learner + planner/tutor cientes do modo);
// aqui está a ÚNICA superfície onde o aluno escolhe o foco. Vive no #toc (Sumário):
// aparece como card na 1ª visita e depois vira um chip re-acessível ("trocar").
// Persiste no servidor (POST /api/learner) E no localStorage (pra não repetir a pergunta).
const KEY = "futurecoder_focus_chosen_v1";

const MODES = [
  {
    id: "python",
    emoji: "🐍",
    title: "Python base",
    desc: "Fundamentos primeiro: lógica, dados e funções, no seu ritmo.",
  },
  {
    id: "qa",
    emoji: "🧪",
    title: "QA Automation",
    desc: "Aprender Python já mirando testar e quebrar software (rumo a pytest).",
  },
];

export const FocusOnboarding = () => {
  const [mode, setMode] = React.useState(null);      // modo atual (do servidor)
  const [chosen, setChosen] = React.useState(() => {
    try { return localStorage.getItem(KEY) === "1"; } catch { return false; }
  });
  const [editing, setEditing] = React.useState(false);
  const [busy, setBusy] = React.useState(false);

  React.useEffect(() => {
    fetch("/api/learner")
      .then((r) => r.json())
      .then((d) => { if (d && d.mode) setMode(d.mode); })
      .catch(() => {});   // server.py off → degrada sem quebrar o sumário
  }, []);

  const choose = async (id) => {
    setBusy(true);
    setMode(id);          // otimista
    try {
      await fetch("/api/learner", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({mode: id}),
      });
    } catch (e) { /* best-effort: o localStorage abaixo ainda registra a escolha */ }
    try { localStorage.setItem(KEY, "1"); } catch (e) {}
    setChosen(true);
    setEditing(false);
    setBusy(false);
  };

  const current = MODES.find((m) => m.id === mode);
  const showPicker = !chosen || editing;

  if (!showPicker) {
    return (
      <div className="focus-chip-row">
        <span className="focus-chip">
          🎯 Foco: <b>{current ? current.title : "Python base"}</b>
        </span>
        <button type="button" className="focus-chip-edit" onClick={() => setEditing(true)}>
          trocar
        </button>
      </div>
    );
  }

  return (
    <div className="focus-onboarding">
      <div className="focus-onboarding-head">
        <div className="focus-onboarding-title">Qual é o seu foco?</div>
        <p className="focus-onboarding-sub">
          Isso personaliza o que a Athena sugere a seguir. Dá pra trocar quando quiser.
        </p>
      </div>
      <div className="focus-options">
        {MODES.map((m) => (
          <button
            key={m.id}
            type="button"
            className={"focus-option" + (mode === m.id ? " selected" : "")}
            disabled={busy}
            onClick={() => choose(m.id)}
          >
            <span className="focus-option-emoji">{m.emoji}</span>
            <span className="focus-option-title">{m.title}</span>
            <span className="focus-option-desc">{m.desc}</span>
          </button>
        ))}
      </div>
      {editing &&
        <button type="button" className="focus-onboarding-cancel" onClick={() => setEditing(false)}>
          cancelar
        </button>}
    </div>
  );
};

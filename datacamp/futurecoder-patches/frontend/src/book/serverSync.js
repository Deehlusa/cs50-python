// Sincroniza progresso do curso com o SQLite do server.py (mesma origem)
// e salva o codigo do editor num arquivo do projeto. Tudo best-effort:
// se o backend nao estiver no ar, o localforage ja garante a persistencia local.
import _ from "lodash";
import {bookState, bookSetState} from "./store";

const PROGRESS_API = "/api/course-progress";
const SAVE_API = "/api/save-code";

// Uma pagina conta como concluida quando o step atual e o ULTIMO step da pagina.
export function courseCompletion(pages, pagesProgress) {
  const slugs = Object.keys(pages || {}).filter((s) => s !== "loading_placeholder");
  let done = 0;
  slugs.forEach((slug) => {
    const steps = (pages[slug] && pages[slug].steps) || [];
    if (!steps.length) return;
    const lastName = steps[steps.length - 1].name;
    const cur = pagesProgress && pagesProgress[slug] && pagesProgress[slug].step_name;
    if (cur && cur === lastName) done++;
  });
  return {done, total: slugs.length};
}

const postProgress = _.debounce(
  (body) => {
    fetch(PROGRESS_API, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(body),
    }).catch(() => {});
  },
  2000,
  {maxWait: 10000},
);

export function saveServerProgress(pages, user, editorContent) {
  if (!user || !user.uid) return;
  const {done, total} = courseCompletion(pages, user.pagesProgress);
  postProgress({
    page_slug: user.pageSlug || "",
    pages_progress: user.pagesProgress || {},
    editor_content: editorContent || "",
    pages_done: done,
    pages_total: total,
  });
}

export async function saveCodeToProject(slug, code) {
  const r = await fetch(SAVE_API, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({slug, code}),
  });
  return r.json();
}

// Progresso do painel "Pratique": espelha cada exercicio concluido no SQLite.
// Best-effort; a fonte de verdade local e o localStorage (PracticePanel).
export async function savePracticeProgress(exerciseId, xp, mode) {
  try {
    const r = await fetch("/api/practice-progress", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({exercise_id: exerciseId, xp: xp, mode: mode}),
    });
    return await r.json();
  } catch (e) {
    return {ok: false};
  }
}

// Tutor IA por fase: backend roda agy (gratis) ou claude via CLI, seguindo o CLAUDE.md.
export async function askTutor(tutor, context, question, code) {
  const r = await fetch("/api/tutor", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({tutor, context, question, code}),
  });
  return r.json();
}

// Zera o progresso do curso: volta cada pagina ao 1o passo (limpa todos os checkpoints)
// e zera o espelho no SQLite. NAO mexe no codigo salvo em saved_code/.
export function resetCourseProgress() {
  const pages = bookState.pages || {};
  // pagesProgress vazio = nenhuma pagina visitada -> todos os checks somem (inclusive
  // paginas de 1 passo so, onde "voltar ao passo 0" ainda contaria como concluida).
  // Mantemos APENAS a pagina atual no passo 0 pra nao quebrar currentStepName().
  const fresh = {};
  const cur = (bookState.user && bookState.user.pageSlug) || "";
  const curSteps = (pages[cur] && pages[cur].steps) || [];
  if (curSteps.length) fresh[cur] = {step_name: curSteps[0].name};
  // atualiza o estado (re-renderiza TOC/quick-menu sem os checks) + persiste via middleware
  bookSetState("user.pagesProgress", fresh);
  // zera o espelho no servidor de imediato (o middleware tambem o faria, com debounce)
  fetch(PROGRESS_API, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      page_slug: (bookState.user && bookState.user.pageSlug) || "",
      pages_progress: fresh,
      editor_content: bookState.editorContent || "",
      pages_done: 0,
      pages_total: Object.keys(fresh).length,
    }),
  }).catch(() => {});
}

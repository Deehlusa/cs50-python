import React from 'react';
import Terminal from './shell/Terminal';
import "./css/main.scss"
import "./css/pygments.css"
import "./css/github-markdown.css"
import "./css/dark.scss"
import chapters from "./chapters.json"
import mediaBr from "./media_br.json"
import {connect} from "react-redux";
import {
  addSpecialMessage,
  bookSetState,
  bookState,
  closeSpecialMessage,
  currentPage,
  currentStep,
  currentStepName,
  disableLogin,
  logEvent,
  movePage,
  moveStep,
  openAssessment,
  postCodeEntry,
  setDeveloperMode,
  setEditorContent,
  signOut,
  specialHash,
} from "./book/store";
import {courseCompletion, saveCodeToProject, askTutor} from "./book/serverSync";
import {ClearProgressButton} from "./components/ClearProgressButton";
import {PracticePanel, practiceStats, getStreak} from "./components/PracticePanel";
// Ícones vetoriais REAIS — game-icons.net (autor: Lorc, CC BY 3.0). Ver assets/game-icons/CREDITS.txt.
import {ReactComponent as GuildOwl} from "./assets/game-icons/guild-owl.svg";
import {ReactComponent as CrestSprout} from "./assets/game-icons/rank-sprout.svg";
import {ReactComponent as CrestSword} from "./assets/game-icons/rank-sword.svg";
import {ReactComponent as CrestOrb} from "./assets/game-icons/rank-orb.svg";
import {ReactComponent as CrestScroll} from "./assets/game-icons/rank-scroll.svg";
import {ReactComponent as CrestCrown} from "./assets/game-icons/rank-crown.svg";
// Moldura REAL — Kenney Fantasy UI Borders (CC0). Arquivo do pack incorporado como border-image
// 9-slice no AthenaPanel. Ver assets/kenney-fantasy-ui-borders/CREDITS.txt + License.txt.
import kenneyFrame from "./assets/kenney-fantasy-ui-borders/panel-border-016.png";
import Popup from "reactjs-popup";
import AceEditor from "react-ace";
import Collapsible from 'react-collapsible';
import "ace-builds/src-noconflict/mode-python";
import "ace-builds/src-noconflict/theme-monokai";
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome'
import {
  faBars,
  faBug,
  faCog,
  faCompress,
  faExpand,
  faLightbulb,
  faListCheck,
  faListOl,
  faPlay,
  faQuestionCircle,
  faSignOutAlt,
  faStop,
  faUserGraduate
} from '@fortawesome/free-solid-svg-icons'
import {HintsAssistant} from "./Hints";
import Toggle from 'react-toggle'
import "react-toggle/style.css"
import {ErrorBoundary, FeedbackMenuButton} from "./Feedback";
import birdseyeIcon from "./img/birdseye_icon.png";
import languageIcon from "./img/language.png";
import {interrupt, runCode, terminalRef} from "./RunCode";
import firebase from "firebase/app";
import {TableOfContents} from "./TableOfContents";
import HeaderLoginInfo from "./components/HeaderLoginInfo";
import terms from "./terms.json"
import _ from "lodash";
import {otherVisibleLanguages} from "./languages";

// ── Lookup: page slug → chapter title (built once at module load) ──────────
const slugToChapter = {};
chapters.forEach(ch => {
  ch.pages.forEach(p => { slugToChapter[p.slug] = ch.title; });
});

// ── XP / Achievement helpers ───────────────────────────────────────────────
function computeXP(pagesProgress, pages) {
  const done = Object.keys(pagesProgress || {}).filter(slug => {
    const steps = (pages && pages[slug] && pages[slug].steps) || [];
    if (!steps.length) return false;
    const lastName = steps[steps.length - 1].name;
    return pagesProgress[slug] && pagesProgress[slug].step_name === lastName;
  });
  const practice = practiceStats();
  return {doneSlugs: done, xp: done.length * 20 + practice.xp, practice};
}

function computeLevel(xp) {
  return Math.floor(Math.sqrt(xp / 40)) + 1;
}

function xpForNextLevel(level) {
  return (level) * (level) * 40;
}

function touchedChapters(pagesProgress) {
  const touched = new Set();
  Object.keys(pagesProgress || {}).forEach(slug => {
    if (slugToChapter[slug]) touched.add(slugToChapter[slug]);
  });
  return touched;
}

function completedChapters(doneSlugs) {
  const chapterPageSets = {};
  chapters.forEach(ch => {
    chapterPageSets[ch.title] = new Set(ch.pages.map(p => p.slug));
  });
  const doneSet = new Set(doneSlugs);
  return Object.keys(chapterPageSets).filter(title =>
    [...chapterPageSets[title]].every(s => doneSet.has(s))
  );
}

// Conquistas. rarity ∈ comum|raro|epico|lendario. progress(ctx) -> {cur,max} (barra nas travadas).
const BADGES = [
  {id: "first_page", icon: "🐍", name: "Primeiro programa", desc: "Concluiu ao menos 1 página", rarity: "comum",
   check: c => c.doneSlugs.length >= 1},
  {id: "marathon", icon: "🏃", name: "Maratona", desc: "Concluiu 5 páginas", rarity: "comum",
   check: c => c.doneSlugs.length >= 5, progress: c => ({cur: c.doneSlugs.length, max: 5})},
  {id: "explorer", icon: "🗺️", name: "Explorador", desc: "Tocou em 3 capítulos", rarity: "comum",
   check: c => c.touched >= 3, progress: c => ({cur: c.touched, max: 3})},
  {id: "first_chapter", icon: "📖", name: "Primeiro capítulo", desc: "Concluiu um capítulo inteiro", rarity: "raro",
   check: c => c.chaptersDone >= 1},
  {id: "halfway", icon: "⚡", name: "Na metade", desc: "50% do curso concluído", rarity: "raro",
   check: c => c.pct >= 50, progress: c => ({cur: c.pct, max: 50})},
  {id: "chapter_master", icon: "📚", name: "Mestre dos capítulos", desc: "Concluiu TODOS os capítulos", rarity: "epico",
   check: c => c.totalChapters > 0 && c.chaptersDone >= c.totalChapters, progress: c => ({cur: c.chaptersDone, max: c.totalChapters})},
  {id: "pythonista", icon: "🏆", name: "Pythonista", desc: "100% do curso concluído", rarity: "lendario",
   check: c => c.pct >= 100, progress: c => ({cur: c.pct, max: 100})},
  {id: "practitioner", icon: "🏋️", name: "Praticante", desc: "5 exercícios de prática", rarity: "comum",
   check: c => c.practice.count >= 5, progress: c => ({cur: c.practice.count, max: 5})},
  {id: "forger", icon: "🔨", name: "Forjador", desc: "15 exercícios de prática", rarity: "raro",
   check: c => c.practice.count >= 15, progress: c => ({cur: c.practice.count, max: 15})},
  {id: "bughunter", icon: "🧪", name: "Caçador de bugs", desc: "Matou todos os bugs de um teste", rarity: "raro",
   check: c => c.practice.wroteTest},
  {id: "qa_mind", icon: "🔬", name: "Mente de QA", desc: "30 exercícios de prática", rarity: "epico",
   check: c => c.practice.count >= 30, progress: c => ({cur: c.practice.count, max: 30})},
  {id: "xp500", icon: "💎", name: "Pedra preciosa", desc: "Acumulou 500 XP", rarity: "raro",
   check: c => c.xp >= 500, progress: c => ({cur: c.xp, max: 500})},
  {id: "level5", icon: "⭐", name: "Nível 5", desc: "Chegou ao nível 5", rarity: "raro",
   check: c => c.level >= 5, progress: c => ({cur: c.level, max: 5})},
  {id: "level10", icon: "🌟", name: "Nível 10", desc: "Chegou ao nível 10", rarity: "epico",
   check: c => c.level >= 10, progress: c => ({cur: c.level, max: 10})},
  {id: "streak3", icon: "🔥", name: "Em chamas", desc: "3 dias seguidos praticando", rarity: "comum",
   check: c => c.streak.count >= 3, progress: c => ({cur: c.streak.count, max: 3})},
  {id: "streak7", icon: "🔥", name: "Semana cheia", desc: "7 dias seguidos praticando", rarity: "raro",
   check: c => c.streak.count >= 7, progress: c => ({cur: c.streak.count, max: 7})},
  {id: "streak30", icon: "🔥", name: "Inabalável", desc: "30 dias seguidos praticando", rarity: "lendario",
   check: c => c.streak.count >= 30, progress: c => ({cur: c.streak.count, max: 30})},
];

// ── XP Pill + Achievements popup ──────────────────────────────────────────
const AchievementsPopup = ({user, pages}) => {
  const {doneSlugs, xp, practice} = computeXP(user.pagesProgress, pages);
  const level = computeLevel(xp);
  const nextLevelXP = xpForNextLevel(level);
  const prevLevelXP = xpForNextLevel(level - 1);
  const barPct = nextLevelXP > prevLevelXP
    ? Math.round(100 * (xp - prevLevelXP) / (nextLevelXP - prevLevelXP))
    : 100;
  const total = Object.keys(pages || {}).filter(s => s !== "loading_placeholder").length;
  const pct = total ? Math.round(100 * doneSlugs.length / total) : 0;
  const streak = getStreak();
  const ctx = {
    doneSlugs, pagesProgress: user.pagesProgress, pct, practice, xp, level, streak,
    touched: touchedChapters(user.pagesProgress).size,
    chaptersDone: completedChapters(doneSlugs).length,
    totalChapters: chapters.length,
  };
  const unlockedCount = BADGES.filter(b => b.check(ctx)).length;

  return (
    <Popup
      nested
      trigger={
        <button className="nav-item nav-link xp-pill" title="XP e Conquistas">
          <span className="xp-icon">⚡</span>
          <span className="xp-label">Nível {level} · {xp} XP</span>
          <span className="xp-bar-wrap">
            <span className="xp-bar-fill" style={{width: barPct + "%"}}/>
          </span>
        </button>
      }
    >
      {close => (
        <div className="achievements-popup">
          <div className="achievements-head">
            <span>🏆 Conquistas <span className="ach-count">{unlockedCount}/{BADGES.length}</span></span>
            <button className="tutor-close" onClick={close}>×</button>
          </div>
          <div className="achievements-xp-summary">
            <span className="achievements-level">Nível {level}</span>
            <span className="achievements-xp-text">
              {xp} XP · {doneSlugs.length}/{total} páginas
              {streak.count > 0 ? " · 🔥 " + streak.count + (streak.count === 1 ? " dia" : " dias") : ""}
            </span>
          </div>
          <div className="achievements-grid">
            {BADGES.map(badge => {
              const unlocked = badge.check(ctx);
              const pr = !unlocked && badge.progress ? badge.progress(ctx) : null;
              return (
                <div key={badge.id}
                     className={"badge-card r-" + (badge.rarity || "comum") + " " + (unlocked ? "unlocked" : "locked")}>
                  <div className="badge-icon">{unlocked ? badge.icon : "🔒"}</div>
                  <div className="badge-name">{badge.name}</div>
                  <div className="badge-desc">{badge.desc}</div>
                  {pr &&
                    <div className="badge-progress">
                      <span className="badge-progress-fill"
                            style={{width: Math.min(100, Math.round(100 * pr.cur / pr.max)) + "%"}}/>
                    </div>}
                  {pr && <div className="badge-progress-text">{Math.min(pr.cur, pr.max)}/{pr.max}</div>}
                  {unlocked && <div className="badge-rarity">{badge.rarity || "comum"}</div>}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </Popup>
  );
};

// ── "Aprenda mais" panel (per-chapter resources from media_br.json) ────────
// Media_br keys use the chapter title in PT-BR. Map them via a normalised key.
const mediaKeyMap = {};
Object.keys(mediaBr).forEach(k => {
  if (k !== "_meta") mediaKeyMap[k.normalize("NFC")] = k;
});

function getMediaForChapter(chapterTitle) {
  if (!chapterTitle) return null;
  const key = mediaKeyMap[chapterTitle.normalize("NFC")];
  return key ? mediaBr[key] : null;
}

const LearnMorePanel = ({pageSlug}) => {
  const [open, setOpen] = React.useState(false);
  const chapterTitle = pageSlug ? slugToChapter[pageSlug] : null;
  const media = getMediaForChapter(chapterTitle);
  if (!media) return null;

  return (
    <div className="learn-more-panel">
      <button
        className="learn-more-trigger"
        onClick={() => setOpen(o => !o)}
        aria-expanded={open}
      >
        <span>📚 Aprenda mais</span>
        <span className="learn-more-arrow">{open ? "▲" : "▼"}</span>
      </button>
      {open && (
        <div className="learn-more-body">
          {media.video && (
            <div className="learn-more-section">
              <div className="learn-more-section-title">📺 Vídeo</div>
              <a href={media.video.url} target="_blank" rel="noopener noreferrer"
                 className="learn-more-link">
                {media.video.label}
              </a>
            </div>
          )}
          {media.sources && media.sources.length > 0 && (
            <div className="learn-more-section">
              <div className="learn-more-section-title">📖 Fontes</div>
              {media.sources.map((s, i) => (
                <a key={i} href={s.url} target="_blank" rel="noopener noreferrer"
                   className="learn-more-link">
                  {s.label}
                </a>
              ))}
            </div>
          )}
          {media.mini_project && (
            <div className="learn-more-section learn-more-project">
              <div className="learn-more-section-title">🧩 Mini-projeto</div>
              <div className="learn-more-project-title">{media.mini_project.title}</div>
              <div className="learn-more-project-goal">{media.mini_project.goal}</div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const EditorButtons = (
  {
    disabled,
    showBirdseye,
    showEditor,
    showPythonTutor,
    showSnoop,
    showQuestionButton,
    running,
  }) =>
  <div className={"editor-buttons " + (showEditor ? "" : "invisible")}>
    {
      running ?
        <button
          className="btn btn-danger"
          onClick={() => interrupt()}
        >
          <FontAwesomeIcon icon={faStop}/> {terms.stop}
        </button>
        :
        <button
          disabled={disabled}
          className="btn btn-primary"
          onClick={() => runCode({source: "editor"})}
        >
          <FontAwesomeIcon icon={faPlay}/> {terms.run}
        </button>
    }

    {" "}

    {showSnoop &&
      <button
        disabled={disabled || running}
        className="btn btn-success"
        onClick={() => runCode({source: "snoop"})}
      >
        <FontAwesomeIcon icon={faBug}/> <span style={{fontFamily: "monospace"}}>snoop</span>
      </button>}

    {" "}

    {showPythonTutor &&
      <button
        disabled={disabled || running}
        className="btn btn-success"
        onClick={() => {
          runCode({source: "pythontutor"});
          let code = bookState.editorContent;
          if (code.includes("assert_equal") && !code.includes("def assert_equal(")) {
            code = 'def assert_equal(actual, expected):\n' +
              '    if actual == expected:\n' +
              '        print("OK")\n' +
              '    else:\n' +
              '        print(f"Error! {repr(actual)} != {repr(expected)}")\n\n\n' + code;
          }
          window.open(
            'https://pythontutor.com/iframe-embed.html#code=' +
            encodeURIComponent(code) +
            '&codeDivHeight=600' +
            '&codeDivWidth=600' +
            '&cumulative=false' +
            '&curInstr=0' +
            '&heapPrimitives=false' +
            '&origin=opt-frontend.js' +
            '&py=3' +
            '&rawInputLstJSON=%5B%5D' +
            '&textReferences=false',
          );
        }}
      >
        <FontAwesomeIcon icon={faUserGraduate}/> Python Tutor
      </button>}

    {" "}

    {showBirdseye &&
      <button
        disabled={disabled || running}
        className="btn btn-success"
        onClick={() => runCode({source: "birdseye"})}
      >
        <img
          src={birdseyeIcon}
          width={20}
          height={20}
          alt="birdseye logo"
          style={{position: "relative", top: "-2px"}}
        />
        <span style={{fontFamily: "monospace"}}> birdseye</span>
      </button>}

    {" "}

    {showQuestionButton && !disabled &&
      <a className="btn btn-success"
         href={"#question"}>
        <FontAwesomeIcon icon={faQuestionCircle}/> {terms.ask_for_help}
      </a>}
  </div>;

const Editor = ({readOnly, value}) => {
  const editorRef = React.useRef(null);
  const containerRef = React.useRef(null);
  React.useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    // ResizeObserver calls editor.resize() whenever the container size changes
    const observer = new ResizeObserver(() => {
      if (editorRef.current) {
        editorRef.current.resize();
      }
    });
    observer.observe(container);
    return () => observer.disconnect();
  }, []);
  return (
    <div className="editor" ref={containerRef}>
      <AceEditor
        mode="python"
        theme="monokai"
        onChange={setEditorContent}
        onLoad={(editor) => {
          editorRef.current = editor;
          editor.renderer.setScrollMargin(10);
          editor.renderer.setPadding(10);
        }}
        value={value}
        name="editor"
        height="100%"
        width="100%"
        fontSize="15px"
        setOptions={{
          fontFamily: "monospace",
          showPrintMargin: false,
        }}
        readOnly={readOnly}
      />
    </div>
  );
};

const Shell = () =>
  <Terminal
    onCommand={(cmd) => runCode({code: cmd, source: "shell"})}
    ref={terminalRef}
  />

const Messages = (
  {
    messageSections,
  }) => {
  const nonEmptySections = messageSections.filter(section => section?.messages?.length);
  if (!nonEmptySections.length) {
    return <p dangerouslySetInnerHTML={{__html: terms.assessment_description}}/>;
  }
  return nonEmptySections.map((section) => {
    if (section.type === "passed_tests") {
      return <div key={section.type} className="card alert alert-success" style={{padding: 0}}>
        <div className="card-body">
          <details>
            <summary>
              {_.template(terms.assessment_passed_tests)({ num: section.messages.length })}
            </summary>
            <br/>
            <SectionMessages section={section}/>
          </details>
        </div>
      </div>
    } else if (section.type === "messages") {
      return <div key={section.type}>
        <SectionMessages section={section}/>
      </div>;
    } else {
      return <div key={section.type}>
        <div className="alert alert-warning" role="alert">
          {terms.assessment_lint}
        </div>
        <SectionMessages section={section}/>
      </div>
    }
  });
}

const SectionMessages = ({section}) => {
  return section.messages.map((message, index) =>
    <div key={index}>
      <div dangerouslySetInnerHTML={{__html: message}} className={`assistant-${section.type}-message`}/>
      {index !== section.messages.length - 1 && <hr/>}
    </div>
  )
}

const Assistant = (assistant) => {
  const {messageSections, step, lastSeenMessageSections} = assistant;
  if (!step.requirements) {
    return null;
  }
  const newMessages = messageSections.some((section) => {
    if (section.type === "passed_tests" || !section.messages.length) {
      return false;
    }
    const lastSeenSection = lastSeenMessageSections.find(s => s.type === section.type);
    return section.messages.some((message) => !lastSeenSection?.messages.includes(message));
  });
  return <div className="assistant accordion">
    <Collapsible classParentString="assistant-requirements card"
                 contentInnerClassName="assistant-content card-body"
                 trigger={<div className="card-header">
                   {terms.requirements}
                 </div>}
    >
      <p>
        {terms.requirements_description}
      </p>
      <ul>
        {step.requirements.map((requirement, index) =>
          <li key={index}>
            <Requirement requirement={requirement}/>
          </li>
        )}
      </ul>
    </Collapsible>
    <Collapsible onOpening={openAssessment}
                 onClosing={() => bookSetState("assessmentOpen", false)}
                 classParentString="assistant-assessment card"
                 contentInnerClassName="assistant-content card-body"
                 trigger={<div className="card-header">
                   {terms.assessment} &nbsp;
                   {newMessages && <span className="badge badge-pill badge-danger">{terms.new}</span>}
                 </div>}
    >
      <Messages {...{messageSections}}/>
    </Collapsible>
    <Collapsible classParentString="assistant-hints card"
                 contentInnerClassName="assistant-content card-body"
                 trigger={<div className="card-header">
                   {terms.hints_and_solution}
                 </div>}
    >
      <HintsAssistant {...assistant}/>
    </Collapsible>
  </div>
    ;
}

const Requirement = (
  {
    requirement,
  }) => {
  let text;
  switch (requirement.type) {
    case "verbatim":
      text = terms.verbatim;
      break;
    case "exercise":
      text = terms.exercise_requirement;
      break;
    case "program_in_text":
      text = terms.program_in_text;
      break;
    case "function_exercise":
      text = _.template(terms.function_exercise)(requirement);
      break;
    case "function_exercise_goal":
      text = _.template(terms.function_exercise_goal)(requirement);
      break;
    case "exercise_stdin":
      text = terms.exercise_stdin;
      break;
    case "non_function_exercise":
      if (!requirement.inputs.trim()) {
        text = terms.no_input_variables;
      } else {
        text = _.template(terms.non_function_exercise)(requirement);
      }
      break;
    default:
      text = requirement.message;
      break;
  }
  return <div className="assistant-requirement" dangerouslySetInnerHTML={{__html: text}}/>
}

const QuestionWizard = (
  {
    messages,
    requestExpectedOutput,
    expectedOutput,
  }) =>
  <>
    <h1>{terms.question_wizard}</h1>
    <div dangerouslySetInnerHTML={{__html: terms.question_wizard_intro}}/>
    <hr/>
    {requestExpectedOutput && <>
      <div dangerouslySetInnerHTML={{__html: terms.question_wizard_expected_output}}/>
      <AceEditor
        onChange={value => bookSetState("questionWizard.expectedOutput", value)}
        theme={"monokai"}
        onLoad={(editor) => {
          editor.renderer.setScrollMargin(10);
          editor.renderer.setPadding(10);
        }}
        width="100%"
        height="15em"
        value={expectedOutput}
        name="expectedOutput"
        fontSize="15px"
        setOptions={{
          fontFamily: "monospace",
          showPrintMargin: false,
        }}
      />
      <hr/>
    </>
    }
    {messages.map((message, index) =>
      <div key={index}>
        <Markdown html={message} copyFunc={text => navigator.clipboard.writeText(text)}/>
        <hr/>
      </div>
    )}
  </>

const Markdown = (
  {
    html,
    copyFunc,
  }) =>
  <div dangerouslySetInnerHTML={{__html: html}}
       onClick={(event) => {
         // https://stackoverflow.com/questions/54109790/how-to-add-onclick-event-to-a-string-rendered-by-dangerouslysetinnerhtml-in-reac
         const button = event.target.closest("button");
         if (button && event.currentTarget.contains(button) && button.classList.contains("copy-button")) {
           const codeElement = button.closest("code");
           let codeText = codeElement.textContent;
           codeText = codeText.substring(0, codeText.length - 1 - button.textContent.length);
           copyFunc(codeText);
         }
       }}
  />

const CourseText = (
  {
    user,
    step,
    page,
    pages,
    assistant,
  }) => {
    // Lista de páginas ordenada por índice para mostrar o DESTINO dos botões prev/next
    // (navegação deixava de ser "cega": o aluno vê o tópico que vem). [Fluxo de estudo]
    const pageList = Object.values(pages).sort((a, b) => a.index - b.index);
    const stripHtml = (h) => (h || "").replace(/<[^>]+>/g, "");
    const prevPage = pageList[page.index - 1];
    const nextPage = pageList[page.index + 1];
    return (
    <>
    <div className="page-breadcrumb">
      {slugToChapter[page.slug] || "Curso"} · {page.index + 1}/{Object.keys(pages).length} do curso
    </div>
    <h1 dangerouslySetInnerHTML={{__html: page.title}}/>
    {page.steps.map((part, index) =>
      <div
        key={index}
        id={`step-text-${index}`}
        className={index > 0 ? 'pt-3' : ''}
        style={index > step.index ? {display: 'none'} : {}}
      >
        <Markdown html={part.text} copyFunc={text => bookSetState("editorContent", text)}/>
        <hr style={{ margin: '0' }}/>
      </div>
    )}
      <Assistant {...assistant} step={step}/>
    {/* pt-3 is Bootstrap's helper class. Shorthand for padding-top: 1rem. Available classes are pt-{1-5} */}
    <div className='pt-3'>
      {page.index > 0 &&
      <button className="btn btn-primary previous-button page-nav-btn"
              onClick={() => movePage(-1)} title={prevPage ? stripHtml(prevPage.title) : ""}>
        ← {terms.previous}
        {prevPage && <span className="page-nav-dest">{stripHtml(prevPage.title)}</span>}
      </button>}
      {" "}
      {page.index < Object.keys(pages).length - 1 &&
      <button className="btn btn-success next-button page-nav-btn"
              onClick={() => movePage(+1)} title={nextPage ? stripHtml(nextPage.title) : ""}>
        {terms.next} →
        {nextPage && <span className="page-nav-dest">{stripHtml(nextPage.title)}</span>}
      </button>}
    </div>
    <LearnMorePanel pageSlug={page.slug}/>
    <PracticePanel chapterTitle={page.slug ? slugToChapter[page.slug] : null}/>
    <br/>
    {
      user.developerMode && <StepButtons/>
    }
  </>
    );
  }

class AppComponent extends React.Component {
  render() {
    if (this.props.route === "toc") {
      return <TableOfContents/>
    }

    return <div className="book-container">
      <NavBar user={this.props.user}/>
      <ErrorBoundary canGiveFeedback>
        <AppMain {...this.props}/>
      </ErrorBoundary>
    </div>
  }
}

const TutorPanel = () => {
  const [open, setOpen] = React.useState(false);
  const [pos, setPos] = React.useState({x: Math.max(12, window.innerWidth - 392), y: 64});
  const [tutor, setTutor] = React.useState("agy");
  const [question, setQuestion] = React.useState("");
  const [answer, setAnswer] = React.useState("");
  const [loading, setLoading] = React.useState(false);
  const off = React.useRef({dx: 0, dy: 0});

  const startDrag = (e) => {
    off.current = {dx: e.clientX - pos.x, dy: e.clientY - pos.y};
    const move = (ev) => setPos({
      x: Math.min(Math.max(0, ev.clientX - off.current.dx), window.innerWidth - 80),
      y: Math.min(Math.max(0, ev.clientY - off.current.dy), window.innerHeight - 60),
    });
    const up = () => {
      window.removeEventListener("mousemove", move);
      window.removeEventListener("mouseup", up);
    };
    window.addEventListener("mousemove", move);
    window.addEventListener("mouseup", up);
  };

  const run = async (q) => {
    setLoading(true);
    setAnswer("");
    try {
      const page = currentPage();
      const context = page && page.title ? page.title : "";
      const res = await askTutor(tutor, context, q, bookState.editorContent || "");
      setAnswer((res && res.feedback) || "Erro ao falar com o tutor.");
    } catch {
      setAnswer("Nao consegui falar com o tutor. O servidor (server.py) esta rodando?");
    }
    setLoading(false);
  };

  return <>
    <button className="nav-item nav-link tutor-trigger"
            title="Pedir ajuda ao tutor (segue o CLAUDE.md)"
            onClick={() => setOpen(o => !o)}>
      <FontAwesomeIcon icon={faLightbulb}/> Tutor
    </button>
    {open &&
      <div className="tutor-float" style={{left: pos.x, top: pos.y}}>
        <div className="tutor-head" onMouseDown={startDrag}>
          <span><FontAwesomeIcon icon={faLightbulb}/> Tutor <span className="tutor-drag-hint">⠿ arraste</span></span>
          <button className="tutor-close" onClick={() => setOpen(false)}>×</button>
        </div>
        <div className="tutor-pickers">
          <button className={"tutor-pick " + (tutor === "agy" ? "active" : "")}
                  onClick={() => setTutor("agy")}>agy (grátis)</button>
          <button className={"tutor-pick " + (tutor === "claude" ? "active" : "")}
                  onClick={() => setTutor("claude")}>Claude</button>
        </div>
        <textarea className="tutor-question" rows={3}
                  placeholder="Escreva sua dúvida sobre esta aula…"
                  value={question} onChange={e => setQuestion(e.target.value)}/>
        <div className="tutor-actions">
          <button className="btn btn-primary btn-sm" disabled={loading}
                  onClick={() => run(question)}>Perguntar</button>
          <button className="btn btn-sm tutor-review" disabled={loading}
                  onClick={() => run("Revise meu código atual: 1 ponto forte + 1 melhoria, pensando como QA. Não reescreva a solução.")}>
            Revisar meu código
          </button>
        </div>
        <div className="tutor-answer">
          {loading ? "Pensando… (pode levar alguns segundos)" : (answer || "A resposta do tutor aparece aqui — ela te guia, não entrega a solução.")}
        </div>
      </div>}
  </>;
};

// Athena — painel de analytics/orquestração DENTRO do futurecoder (módulos G/H/I da
// SDD-ai-learning-os): próximo passo (Progress Analyst), domínio por conceito (Mastery
// Tracker) e log da sessão autônoma (/loop). Mesmo padrão do TutorPanel: botão na navbar
// → painel flutuante arrastável. Lê /api/{next,mastery,agent-run} no server.py.
// Emoji por conceito (UI-1 Skill Matrix) — inline, sem dependência nova (COEP-safe).
const CONCEPT_ICON = {
  shell_print_vars: "🐍", types_cast_conditionals: "🔀", loops: "🔁", strings: "🔤",
  collections: "🗂️", pure_functions: "🧩", exceptions: "⚠️", files_json_oop: "📦",
  pytest_aaa: "🧪", pytest_raises_param: "🎯", api_requests: "🌐", playwright_pom: "🎭",
  ci_cd: "⚙️",
};

// Badge curto por conceito QA (UI-3 QA Track).
const QA_BADGE = {
  pytest_aaa: "AAA", pytest_raises_param: "raises", api_requests: "requests",
  playwright_pom: "POM", ci_cd: "Actions",
};

// Ranks da Guilda por nº de conceitos dominados (0–13). Crest = ícone vetorial REAL (game-icons).
const RANKS = [
  {min: 0,  title: "Aprendiz",  Crest: CrestSprout},
  {min: 1,  title: "Escudeiro", Crest: CrestSword},
  {min: 4,  title: "Adepto",    Crest: CrestOrb},
  {min: 8,  title: "Arcanista", Crest: CrestScroll},
  {min: 12, title: "Mestre",    Crest: CrestCrown},
];
const rankFor = (mastered) => RANKS.reduce((acc, r) => mastered >= r.min ? r : acc, RANKS[0]);

const AthenaPanel = () => {
  const [open, setOpen] = React.useState(false);
  const [pos, setPos] = React.useState({x: Math.max(12, window.innerWidth - 432), y: 64});
  const [data, setData] = React.useState({next: null, mastery: null, runs: []});
  const [loading, setLoading] = React.useState(false);
  const [tab, setTab] = React.useState("matrix");   // UI-3: "matrix" (todos) | "qa" (QA Track)
  const off = React.useRef({dx: 0, dy: 0});

  const startDrag = (e) => {
    off.current = {dx: e.clientX - pos.x, dy: e.clientY - pos.y};
    const move = (ev) => setPos({
      x: Math.min(Math.max(0, ev.clientX - off.current.dx), window.innerWidth - 80),
      y: Math.min(Math.max(0, ev.clientY - off.current.dy), window.innerHeight - 60),
    });
    const up = () => {
      window.removeEventListener("mousemove", move);
      window.removeEventListener("mouseup", up);
    };
    window.addEventListener("mousemove", move);
    window.addEventListener("mouseup", up);
  };

  const load = async () => {
    setLoading(true);
    try {
      const [next, mastery, runs] = await Promise.all([
        fetch("/api/next").then(r => r.json()).catch(() => null),
        fetch("/api/mastery").then(r => r.json()).catch(() => null),
        fetch("/api/agent-run").then(r => r.json()).catch(() => ({items: []})),
      ]);
      setData({next, mastery, runs: (runs && runs.items) || []});
    } catch { /* server.py off — painel degrada sem quebrar */ }
    setLoading(false);
  };

  React.useEffect(() => { if (open) load(); }, [open]);

  // CTA "Ir praticar": rola até o PracticePanel da PÁGINA ATUAL (scroll seguro, sem rota nova).
  // Limite: não navega cross-capítulo (páginas à frente do progresso são travadas pela SPA).
  const goPractice = () => {
    const el = document.querySelector(".practice-panel");
    if (el) {
      el.scrollIntoView({behavior: "smooth", block: "start"});
      setOpen(false);
    }
  };

  const bars = (data.mastery && data.mastery.items) || [];
  const qa = bars.filter(it => it.level >= 8);          // trilha QA: pytest → CI/CD (níveis 8–12)
  const qaStarted = qa.some(it => it.strength > 0);
  // Guilda do Saber: rank + barra de XP a partir do domínio total.
  const mastered = (data.mastery && data.mastery.mastered) || 0;
  const totalC = (data.mastery && data.mastery.total) || 0;
  const overall = totalC ? Math.round((mastered / totalC) * 100) : 0;
  const rank = rankFor(mastered);
  const rankIdx = RANKS.indexOf(rank);
  const nextRank = RANKS[rankIdx + 1];
  const toNext = nextRank ? nextRank.min - mastered : 0;
  return <>
    <button className="nav-item nav-link athena-trigger"
            title="Athena — seu painel de aprendizado (próximo passo, domínio, sessão autônoma)"
            onClick={() => setOpen(o => !o)}>
      🦉 Athena
    </button>
    {open &&
      <div className="tutor-float athena-float athena-kenney-frame"
           style={{left: pos.x, top: pos.y, borderImageSource: `url(${kenneyFrame})`}}>
        <div className="tutor-head athena-guild-head" onMouseDown={startDrag}>
          <span className="athena-guild-title">
            <GuildOwl className="athena-guild-owl" aria-hidden="true"/>
            Athena · Salão da Guilda <span className="tutor-drag-hint">⠿ arraste</span>
          </span>
          <button className="tutor-close" onClick={() => setOpen(false)}>×</button>
        </div>
        {loading
          ? <div className="athena-body">Carregando…</div>
          : <div className="athena-body">
              <div className="athena-hero">
                <rank.Crest className="athena-hero-crest" aria-hidden="true"/>
                <div className="athena-hero-info">
                  <div className="athena-hero-rank">Rank: <b>{rank.title}</b></div>
                  <div className="athena-hero-xpbar">
                    <span className="athena-hero-xpfill" style={{width: overall + "%"}}/>
                  </div>
                  <div className="athena-hero-xptext">{mastered}/{totalC} habilidades · {overall}%</div>
                  <div className="athena-hero-hint">
                    {nextRank
                      ? `Domine +${toNext} conceito${toNext > 1 ? "s" : ""} (≥80%) para alcançar ${nextRank.title}.`
                      : "Rank máximo da guilda. Mantenha as revisões em dia."}
                  </div>
                </div>
              </div>
              <div className="athena-next">
                {data.next && data.next.label
                  ? <div className={"athena-next-card" + (data.next.review ? " is-review" : "")}>
                      <span className="athena-next-ico">{data.next.review ? "⏰" : "⚔️"}</span>
                      <div className="athena-next-info">
                        <div className="athena-quest-eyebrow">
                          {data.next.review ? "↻ Revisão da guilda" : "⚔️ Missão atual"}
                        </div>
                        <div className="athena-next-title">{data.next.label}</div>
                        <div className="athena-next-reason">{data.next.reason}</div>
                        <button className="athena-next-cta" onClick={goPractice}>🏋️ Ir praticar</button>
                      </div>
                    </div>
                  : <div className="athena-next-card is-done">
                      <span className="athena-next-ico">🎉</span>
                      <div className="athena-next-info">
                        <div className="athena-next-title">Currículo concluído</div>
                        <div className="athena-next-reason">Todos os conceitos dominados.</div>
                      </div>
                    </div>}
              </div>
              <div className="athena-mastery">
                <div className="athena-tabs">
                  <button className={"athena-tab" + (tab === "matrix" ? " active" : "")}
                          onClick={() => setTab("matrix")}>🗺️ Jornada</button>
                  <button className={"athena-tab" + (tab === "qa" ? " active" : "")}
                          onClick={() => setTab("qa")}>🛡️ QA Guild</button>
                </div>

                {tab === "matrix" &&
                  <>
                    <div className="athena-section-head">
                      <span className="athena-count">
                        {data.mastery ? `${data.mastery.mastered}/${data.mastery.total} conceitos dominados` : "Comece sua jornada"}
                      </span>
                    </div>
                    <div className="athena-legend">
                      ✅ dominado (≥80%) · 🔄 em progresso · 🔒 não iniciado — domínio cresce
                      ao acertar exercícios e cai se você erra. Revisões espaçadas mantêm a memória.
                    </div>
                    <div className="athena-matrix">
                      {bars.map(it => {
                        const pct = Math.round((it.strength || 0) * 100);
                        const track = it.level >= 12 ? "cicd" : it.level >= 8 ? "qa" : "core";
                        const state = it.mastered ? "done" : (it.strength > 0 ? "wip" : "todo");
                        const mark = it.mastered ? "✅" : (it.strength > 0 ? "🔄" : "🔒");
                        return <div className={`athena-card athena-card--${track} athena-card--${state}`}
                                    key={it.concept} title={`${it.label} — ${pct}%`}>
                          <span className="athena-card-ico">{CONCEPT_ICON[it.concept] || "•"}</span>
                          <span className="athena-card-label">{it.label}</span>
                          <span className="athena-card-foot">
                            <span className="athena-card-state">{mark}</span>
                            <span className="athena-card-pct">{pct}%</span>
                          </span>
                        </div>;
                      })}
                    </div>
                  </>}

                {tab === "qa" && (qaStarted
                  ? <div className="athena-qa-list">
                      <div className="athena-qa-intro">
                        Trilha QA → CI/CD: do primeiro <code>assert</code> ao pipeline verde a cada commit.
                      </div>
                      {qa.map(it => {
                        const pct = Math.round((it.strength || 0) * 100);
                        const state = it.mastered ? "done" : (it.strength > 0 ? "wip" : "todo");
                        const mark = it.mastered ? "✅" : (it.strength > 0 ? "🔄" : "🔒");
                        return <div className={"athena-qa-row athena-qa-row--" + state} key={it.concept}>
                          <span className="athena-qa-ico">{CONCEPT_ICON[it.concept] || "•"}</span>
                          <div className="athena-qa-main">
                            <div className="athena-qa-name">
                              {it.label} <span className="athena-qa-badge">{QA_BADGE[it.concept] || ""}</span>
                            </div>
                            <div className="athena-qa-track">
                              <span className="athena-qa-fill" style={{width: pct + "%"}}/>
                            </div>
                          </div>
                          <span className="athena-qa-state">{mark} {pct}%</span>
                        </div>;
                      })}
                    </div>
                  : <div className="athena-qa-empty">
                      <div className="athena-qa-empty-ico">🧪</div>
                      <div className="athena-qa-empty-title">A Guilda de QA está recrutando</div>
                      <div className="athena-qa-empty-text">
                        Testar é o que separa "funciona na minha máquina" de "pronto pra produção".
                        Domine a base de Python na aba <b>Jornada</b> e estes marcos abrem aqui:
                        <b> pytest</b> (testes que falham cedo), <b>requests</b> (API testing),
                        <b> Playwright</b> (E2E) e <b>CI/CD</b> (tudo verde a cada commit).
                      </div>
                    </div>)}
              </div>
              <details className="athena-runs-wrap">
                <summary>🤖 Sessão autônoma (log do /loop)</summary>
                <div className="athena-runs">
                  {data.runs.length
                    ? data.runs.slice(0, 12).map(r =>
                        <div key={r.id}>{r.ts} · <b>{r.agent}</b> [{r.provider}] {r.status}</div>)
                    : <div>(sem execuções ainda)</div>}
                </div>
              </details>
            </div>}
      </div>}
  </>;
};

function FocusButton() {
  const [on, setOn] = React.useState(false);

  // Modo foco = classe `focus-mode` no body + estado `on`, SEMPRE setados juntos
  // na mesma função (sem listener async que possa dessincronizar). Fullscreen é
  // best-effort e NÃO controla o estado do foco.
  const setMode = React.useCallback((next) => {
    setOn(next);
    document.body.classList.toggle("focus-mode", next);
    try {
      const el = document.documentElement;
      if (next && !document.fullscreenElement) {
        const req = el.requestFullscreen || el.webkitRequestFullscreen;
        if (req) { const p = req.call(el); if (p && p.catch) p.catch(() => {}); }
      } else if (!next && document.fullscreenElement) {
        const exit = document.exitFullscreen || document.webkitExitFullscreen;
        if (exit) { const p = exit.call(document); if (p && p.catch) p.catch(() => {}); }
      }
    } catch (e) { /* fullscreen bloqueado: o modo foco (classe) continua valendo */ }
  }, []);

  React.useEffect(() => {
    const onKey = (e) => {
      if (e.key === "Escape" && document.body.classList.contains("focus-mode")) setMode(false);
    };
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.classList.remove("focus-mode"); // nunca deixa preso no foco
    };
  }, [setMode]);

  return (
    <button className={"nav-item nav-link focus-toggle" + (on ? " active" : "")}
            title="Modo foco — esconde distrações pra você focar na aula (Esc sai)"
            aria-pressed={on}
            onClick={() => setMode(!on)}>
      <FontAwesomeIcon icon={on ? faCompress : faExpand}/> {on ? "Sair do foco" : "Foco"}
    </button>
  );
}

function NavBar({user}) {
  const [, forceUpdate] = React.useReducer(x => x + 1, 0);
  React.useEffect(() => {
    const h = () => forceUpdate();
    window.addEventListener("practice-updated", h);
    return () => window.removeEventListener("practice-updated", h);
  }, []);
  const {done, total} = courseCompletion(bookState.pages, user.pagesProgress);
  const pct = total ? Math.round(100 * done / total) : 0;
  return <nav className="navbar navbar-expand-lg navbar-dark">
        <span className="nav-item custom-popup">
          <MenuPopup user={user}/>
        </span>
    <span className="nav-item navbar-text">
          <HeaderLoginInfo email={user.email}/>
        </span>
    <a className="nav-item nav-link" href="#toc">
      <FontAwesomeIcon icon={faListOl}/> {terms.table_of_contents}
    </a>
    <TutorPanel/>
    <AthenaPanel/>
    <FocusButton/>
    {(() => {
      const s = getStreak();
      return s.count > 0
        ? <span className="nav-item streak-chip" title={"Sequência de prática: " + s.count + " dias (recorde " + (s.best || s.count) + ")"}>🔥 {s.count}</span>
        : null;
    })()}
    <AchievementsPopup user={user} pages={bookState.pages}/>
    <SettingsPopup user={user}/>
    <span className="nav-item course-progress" title={`${done}/${total} páginas`}>
      <span className="course-progress-bar">
        <span className="course-progress-fill" style={{width: pct + "%"}}/>
      </span>
      <span className="course-progress-label">{pct}% concluído</span>
    </span>
  </nav>;
}

const SaveCodeButton = () => {
  const [status, setStatus] = React.useState("");
  const onSave = async () => {
    const slug = bookState.user.pageSlug || "code";
    const code = bookState.editorContent || "";
    if (!code.trim()) { setStatus("vazio"); setTimeout(() => setStatus(""), 2500); return; }
    setStatus("salvando");
    try {
      const res = await saveCodeToProject(slug, code);
      setStatus(res && res.ok ? "salvo" : "erro");
    } catch {
      setStatus("erro");
    }
    setTimeout(() => setStatus(""), 2500);
  };
  const labels = {salvando: "Salvando…", salvo: "✓ Salvo no projeto", erro: "Erro ao salvar", vazio: "Editor vazio"};
  return <button className="btn btn-sm save-code-btn" onClick={onSave}>
    {labels[status] || "Salvar no projeto"}
  </button>;
};

function AppMain(
  {
    editorContent,
    assistant,
    specialMessages,
    questionWizard,
    pages,
    user,
    prediction,
    route,
    previousRoute,
    running,
  }) {
  const isQuestionWizard = route === "question";
  const fullIde = route === "ide";

  // Marca a rota #ide no body. O modo Foco esconde a IDE nas páginas de AULA (pra ler o texto),
  // mas na página #ide a IDE É o conteúdo — sem isso, o Foco escondia editor/Executar/shell e
  // "Executar" parecia não fazer nada. [fix: Foco no #ide]
  React.useEffect(() => {
    document.body.classList.toggle("route-ide", fullIde);
    return () => document.body.classList.remove("route-ide");
  }, [fullIde]);

  const page = currentPage();
  const step = currentStep();

  let showEditor, showSnoop, showPythonTutor, showBirdseye, showQuestionButton;
  if (fullIde || isQuestionWizard) {
    showEditor = true;
    showSnoop = true;
    showPythonTutor = true;
    showBirdseye = true;
    showQuestionButton = !(isQuestionWizard || previousRoute === "question");
  } else if (step.text.length) {
    showEditor = page.index >= pages.WritingPrograms.index;
    const snoopPageIndex = pages.UnderstandingProgramsWithSnoop.index;
    showSnoop = page.index > snoopPageIndex ||
      (page.index === snoopPageIndex && step.index >= 1);
    showPythonTutor = page.index >= pages.UnderstandingProgramsWithPythonTutor.index;
    showBirdseye = page.index >= pages.IntroducingBirdseye.index;
    showQuestionButton = page.index > pages.IntroducingBirdseye.index;
  }

  const cantUseEditor = prediction.state === "waiting" || prediction.state === "showingResult";

  return <>
    {!fullIde &&
      <div className="book-text markdown-body">
        {isQuestionWizard ?
          <QuestionWizard {...questionWizard}/>
          :
          <div onCopy={checkCopy}>
            <CourseText
              {...{
                assistant,
                user,
                step,
                page,
                pages,
              }}/>
          </div>
        }
      </div>

    }

    <EditorButtons {...{
      showBirdseye,
      showEditor,
      showSnoop,
      showPythonTutor,
      showQuestionButton,
      disabled: cantUseEditor,
      running,
    }}/>

    <div className={`ide ide-${fullIde ? 'full' : 'half'}`}>
      <div className="editor-and-terminal">
        {showEditor &&
          <Editor value={editorContent} readOnly={cantUseEditor}/> 
        }
        <div className="terminal" style={{height: showEditor ? undefined : "100%"}}>
          <Shell/>
        </div>
      </div>
    </div>

    <a className="btn btn-primary full-ide-button"
       href={"#" + (!fullIde ? "ide" : (specialHash(previousRoute) ? previousRoute : page.slug))}>
      <FontAwesomeIcon icon={fullIde ? faCompress : faExpand}/>
    </a>
    <SaveCodeButton/>

    {specialMessages.map((message, index) =>
      <Popup
        key={index}
        open={true}
        onClose={() => closeSpecialMessage(index)}
      >
        <SpecialMessageModal message={message}/>
      </Popup>
    )}
  </>;
}

const StepButton = ({delta, label}) =>
  <button className={`btn btn-danger btn-sm button-${label.replace(" ", "-").toLowerCase()}`}
          onClick={() => {
            const entry = {skip_step: delta, page_slug: bookState.user.pageSlug, step_name: currentStepName()};
            postCodeEntry(entry);
            logEvent('skip_step', entry);
            moveStep(delta);
          }}>
    {label}
  </button>

const StepButtons = () =>
  <div style={{position: "fixed", bottom: 0}}>
    <StepButton delta={-1} label={terms.reverse_step}/>
    {" "}
    <StepButton delta={+1} label={terms.skip_step}/>
  </div>


const tocPageState = (user, slug) => {
  const runtimePages = bookState.pages || {};
  const progress = (user && user.pagesProgress) || {};
  const steps = (runtimePages[slug] && runtimePages[slug].steps) || [];
  const name = progress[slug] && progress[slug].step_name;
  if (!steps.length || !name) return "";
  const idx = steps.findIndex(s => s.name === name);
  const last = steps.length - 1;
  if (idx >= last) return "done";
  if (idx > 0) return "started";
  return "";
};

const MenuPopup = ({user}) =>
    <Popup
      nested
      trigger={
        <button className="btn btn-sm btn-outline-secondary">
          <FontAwesomeIcon icon={faBars} size="lg"/>
        </button>}
    >
      {close => <div className="menu-popup quick-menu">
        <div className="quick-menu-head">
          <span>{terms.table_of_contents}</span>
          <ClearProgressButton className="clear-progress-mini" label="Limpar"/>
        </div>
        {chapters.map(chapter =>
          <div className="quick-menu-chapter" key={chapter.title}>
            <div className="quick-menu-chapter-title">{chapter.title}</div>
            {chapter.pages.map(page => {
              const state = tocPageState(user, page.slug);
              return <a key={page.slug} href={"#" + page.slug}
                        className={"quick-menu-page " + state}
                        onClick={() => close()}>
                <span className="quick-menu-mark">{state === "done" ? "✓" : (state === "started" ? "•" : "")}</span>
                <span className="quick-menu-title" dangerouslySetInnerHTML={{__html: page.title}}/>
              </a>;
            })}
          </div>
        )}
      </div>}
    </Popup>


const SettingsModal = ({user}) => (
  <div className="settings-modal">
    <h1>{terms.settings}</h1>
    <br/>
    <label>
      <Toggle
        defaultChecked={user.developerMode}
        onChange={(e) => setDeveloperMode(e.target.checked)}
      />
      <b>{terms.developer_mode}</b>
    </label>

    <p>{terms.developer_mode_description}</p>
  </div>
)

const SettingsPopup = ({user}) =>
  <Popup
    nested
    trigger={
      <button className="nav-item nav-link" title="Configurações">
        <FontAwesomeIcon icon={faCog}/> Config
      </button>}
  >
    {close => <div className="menu-popup settings-popup">
      <div className="quick-menu-head">{terms.settings}</div>
      <label className="settings-row">
        <Toggle defaultChecked={user.developerMode} onChange={(e) => setDeveloperMode(e.target.checked)}/>
        <span>{terms.developer_mode}</span>
      </label>
      <p className="settings-desc">{terms.developer_mode_description}</p>
      <ClearProgressButton/>
    </div>}
  </Popup>;

const SpecialMessageModal = ({message}) => (
  <div className="special-message-modal">
    <div dangerouslySetInnerHTML={{__html: message}}/>
  </div>
);

const checkCopy = () => {
  const selection = document.getSelection();
  const codeElement = (node) => node.parentElement.closest("code");
  if (
    [...document.querySelectorAll(".book-text code")]
      .filter(node => selection.containsNode(node))
      .concat([
        codeElement(selection.anchorNode),
        codeElement(selection.focusNode),
      ])
      .some((node) => node && !node.classList.contains("copyable"))
  ) {
    addSpecialMessage(terms.copy_warning);
  }
}


export const App = connect(
  state => ({
    ...state.book,
  }),
)(AppComponent);


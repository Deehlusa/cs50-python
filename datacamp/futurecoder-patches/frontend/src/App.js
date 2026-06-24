import React from 'react';
import Terminal from './shell/Terminal';
import "./css/main.scss"
import "./css/pygments.css"
import "./css/github-markdown.css"
import "./css/dark.scss"
import chapters from "./chapters.json"
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
  }) =>
    <>
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
      <button className="btn btn-primary previous-button"
              onClick={() => movePage(-1)}>
        ← {terms.previous}
      </button>}
      {" "}
      {page.index < Object.keys(pages).length - 1 &&
      <button className="btn btn-success next-button"
              onClick={() => movePage(+1)}>
        {terms.next} →
      </button>}
    </div>
    <br/>
    {
      user.developerMode && <StepButtons/>
    }
  </>

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

function NavBar({user}) {
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


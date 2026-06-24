import React from 'react';
import "./css/toc.scss"
import chapters from "./chapters.json"
import {bookState} from "./book/store";
import terms from "./terms.json"
import {ClearProgressButton} from "./components/ClearProgressButton";

export const TableOfContents = () => {
  const current = bookState.user.pageSlug;
  const runtimePages = bookState.pages || {};
  const progress = (bookState.user && bookState.user.pagesProgress) || {};

  // Estado de cada pagina: "done" (chegou no ultimo passo), "started" (avancou
  // pelo menos 1 passo) ou "" (nao comecou).
  const pageState = (slug) => {
    const steps = (runtimePages[slug] && runtimePages[slug].steps) || [];
    const name = progress[slug] && progress[slug].step_name;
    if (!steps.length || !name) return "";
    const idx = steps.findIndex(s => s.name === name);
    const last = steps.length - 1;
    if (idx >= last) return "done";
    if (idx > 0) return "started";
    return "";
  };

  // Resumo do progresso pro topo do sumario.
  const allSlugs = Object.keys(runtimePages).filter(s => s !== "loading_placeholder");
  const doneCount = allSlugs.filter(s => pageState(s) === "done").length;
  const pct = allSlugs.length ? Math.round(100 * doneCount / allSlugs.length) : 0;

  return (
    <div className="backend bg-dark toc">
      <div className="toc-header">
        <div className="container">
          <h1>futurecoder</h1>
          <div dangerouslySetInnerHTML={{__html: terms.toc_instructions}}/>
        </div>
      </div>

      <div className="container toc-container">
        <div className="row">
          <div className="col-md-9" role="main">
            <div className="toc-section">
              <h1 id="toc-toc">
                {terms.table_of_contents}
              </h1>
              {allSlugs.length > 0 &&
                <div className="toc-progress">
                  <div className="toc-progress-bar">
                    <div className="toc-progress-fill" style={{width: pct + "%"}}/>
                  </div>
                  <span className="toc-progress-label">{doneCount}/{allSlugs.length} páginas · {pct}%</span>
                  <ClearProgressButton className="clear-progress-mini"/>
                </div>}
              <ol className="toc-ol">
                {chapters.map(chapter =>
                  <li key={chapter.title}>
                    <h2>{chapter.title}</h2>
                    <ol>
                      {chapter.pages.map(page => {
                        const isCurrent = page.slug === current;
                        const state = pageState(page.slug);
                        return <li
                          key={page.slug}
                          className={"toc-page-item " + state + (isCurrent ? " current" : "")}>
                          <span className="toc-mark">{state === "done" ? "✓" : (state === "started" ? "•" : "")}</span>
                          <a href={"#" + page.slug}
                            // May have HTML generated from markdown
                             dangerouslySetInnerHTML={{__html: page.title}}/>
                          {isCurrent && <span className="toc-atual">{terms.current_page}</span>}
                        </li>;
                      })}
                    </ol>
                  </li>
                )}
              </ol>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

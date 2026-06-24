import React from "react";
import {resetCourseProgress} from "../book/serverSync";

// Botao unico reaproveitado no quick-menu (☰), no #toc e em Configuracoes.
// Pede confirmacao e zera todos os checkpoints do curso.
export const ClearProgressButton = ({className, label}) => {
  const onClick = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (window.confirm("Limpar todo o seu progresso do curso? Isso remove todos os checkpoints (✓ e •). O código salvo em saved_code/ não é afetado.")) {
      resetCourseProgress();
    }
  };
  return (
    <button type="button" className={"clear-progress-btn " + (className || "")} onClick={onClick}>
      {label || "Limpar progresso"}
    </button>
  );
};

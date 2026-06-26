// eslint-disable-next-line import/no-webpack-loader-syntax
import Worker from "worker-loader!./Worker.js";
import {makeChannel} from "sync-message";
import * as Comlink from 'comlink';
import {PyodideClient} from "pyodide-worker-runner";

const channel = makeChannel({serviceWorker: {scope: "/course/"}});

export const taskClient = new PyodideClient(() => new Worker(), channel);

export async function runCodeTask(entry, outputCallback, inputCallback) {
  let running = true;

  function wrappedOutputCallback(...args) {
    if (running) {
      outputCallback(...args);
    }
  }

  try {
    return await taskClient.call(
      taskClient.workerProxy.runCode,
      entry,
      Comlink.proxy(wrappedOutputCallback),
      Comlink.proxy(inputCallback),
    );
  } catch (e) {
    if (e.type === "InterruptError") {
      return {
        interrupted: true,
        error: null,
        passed: false,
        message_sections: [],
      }
    }
    throw e;
  } finally {
    running = false;
  }
}

// PATCH (datacamp): roda um programa Python cru no worker (painel "Pratique").
// Retorna a string crua devolvida pelo Worker.runRaw (JSON da harness, ou
// "__PRACTICE_PYERROR__..." em caso de erro fatal).
export async function runRawPython(code) {
  return await taskClient.call(taskClient.workerProxy.runRaw, code);
}

// Interrompe a execução em curso (escreve o interrupt buffer compartilhado).
// Usado pelo painel de prática p/ matar loop infinito (timeout) ou botão Parar.
export function interruptRaw() {
  try { taskClient.interrupt(); } catch (e) {}
}

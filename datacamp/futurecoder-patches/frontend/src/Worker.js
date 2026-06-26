/* eslint-disable */
// Otherwise webpack fails silently
// https://github.com/facebook/create-react-app/issues/8014
//
// PATCH (datacamp): adiciona `runRaw` — roda código Python arbitrário no MESMO
// Pyodide já carregado (sem 2ª instância, mesma origem -> seguro com COOP/COEP).
// Usado pelo painel "Pratique" (PyodideRunner). Retorna o valor da ÚLTIMA
// expressão (a harness termina com json.dumps(...), então volta a string JSON).

import * as Comlink from 'comlink';
import pythonCoreUrl from "./python_core.tar.load_by_url"
import {
  loadPyodideAndPackage,
  makeRunnerCallback,
  pyodideExpose,
  PyodideFatalErrorReloader
} from "pyodide-worker-runner";

const reloader = new PyodideFatalErrorReloader(async () => {
  const pyodide = await loadPyodideAndPackage({url: pythonCoreUrl, format: "tar"});
  pyodide.pyimport("core.init_pyodide").init(process.env.REACT_APP_LANGUAGE);
  return pyodide;
});

let programCount = 1;

const runCode = pyodideExpose(
  async function (extras, entry, outputCallback, inputCallback) {
    let outputPromise;
    const callback = makeRunnerCallback(extras, {
      input: () => inputCallback(),
      output: (parts) => {
        outputPromise = outputCallback(parts);
      },
    });

    return await reloader.withPyodide(async (pyodide) => {
      const pyodide_worker_runner = pyodide.pyimport("pyodide_worker_runner");
      try {
        await pyodide_worker_runner.install_imports(entry.input);
      } catch (e) {
        console.error(e);
      }

      const checkerModule = pyodide.pyimport("core.checker");
      checkerModule.default_runner.set_filename(`/my_program_${programCount++}.py`)
      const result = checkerModule.check_entry(entry, callback);
      await outputPromise;
      return result.toJs({dict_converter: Object.fromEntries});
    });
  },
);

// PATCH: runner cru para o painel de prática. `code` é um programa Python
// completo (a harness do PyodideRunner) cuja última expressão é json.dumps(...).
const runRaw = pyodideExpose(
  async function (extras, code) {
    return await reloader.withPyodide(async (pyodide) => {
      try {
        const result = await pyodide.runPythonAsync(code);
        return typeof result === "string" ? result : String(result);
      } catch (e) {
        const msg = (e && e.message) ? e.message : String(e);
        if (/KeyboardInterrupt/i.test(msg)) {
          return "__PRACTICE_PYERROR__Tempo limite (~8s): seu código pode ter um loop infinito. Execução interrompida.";
        }
        return "__PRACTICE_PYERROR__" + msg;
      }
    });
  },
);

Comlink.expose({runCode, runRaw});

// PyodideRunner — avalia exercícios de prática no Pyodide do futurecoder
// (via Worker.runRaw / TaskClient.runRawPython). Dois modos:
//   write_code: roda a função do aluno contra casos {call, expect}.
//   write_test: roda os testes do aluno na referência (devem passar) e em cada
//               mutante (cada mutante deve ser "morto" por algum teste falhar).
//
// Robustez:
//   - LOOP INFINITO: o código do aluno é transformado via AST, injetando um
//     contador-guarda no início de cada `while`/`for`; após N iterações levanta
//     RuntimeError. É in-process (não depende de interrupt/service-worker, que
//     estão desligados neste setup). Backup: timeout de 8s chama interruptRaw().
//   - Contagem de testes via AST (ignora asserts em comentário/string).
//   - O payload é decodificado em escopo LOCAL e removido dos globals.
// Dados em base64 (à prova de aspas/unicode); a harness termina com
// json.dumps(...), cujo valor o Worker.runRaw devolve.

import {runRawPython, interruptRaw} from "../TaskClient";

const RUN_TIMEOUT_MS = 8000;

function b64utf8(str) {
  const bytes = new TextEncoder().encode(str);
  let bin = "";
  for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
  return btoa(bin);
}

const LOGIC = `
def __main():
    import json as _json, base64 as _b64, ast as _ast
    data = _json.loads(_b64.b64decode(__PAYLOAD).decode("utf-8"))
    try:
        del globals()["__PAYLOAD"]
    except Exception:
        pass

    __LIMIT = 3000000
    __counter = [0]
    def __lg():
        __counter[0] += 1
        if __counter[0] > __LIMIT:
            raise RuntimeError("Loop muito longo — seu codigo pode ter um loop infinito.")
    def __reset():
        __counter[0] = 0

    class _Guard(_ast.NodeTransformer):
        def _wrap(self, n):
            self.generic_visit(n)
            n.body = [_ast.parse("__lg()").body[0]] + n.body
            return n
        def visit_While(self, n):
            return self._wrap(n)
        def visit_For(self, n):
            return self._wrap(n)

    def _guarded(src):
        tree = _Guard().visit(_ast.parse(src))
        _ast.fix_missing_locations(tree)
        return compile(tree, "<exercicio>", "exec")

    mode = data["mode"]
    student = data["student"]

    if mode == "write_code":
        ns = {"__lg": __lg}
        try:
            exec(_guarded(student), ns)
        except Exception as e:
            return {"mode": mode, "ok": False, "error": "Erro no seu codigo: " + repr(e), "results": []}
        results = []
        ok = True
        for t in data["tests"]:
            __reset()
            try:
                actual = eval(t["call"], ns)
                passed = actual == t["expect"]
            except Exception as e:
                actual = "ERRO: " + repr(e)
                passed = False
            if not passed:
                ok = False
            results.append({"call": t["call"], "expect": repr(t["expect"]), "actual": repr(actual), "passed": bool(passed)})
        return {"mode": mode, "ok": ok, "results": results}

    student_tests = student
    min_tests = data["min_tests"]
    try:
        tree = _ast.parse(student_tests)
        n_assert = sum(1 for n in _ast.walk(tree) if isinstance(n, _ast.Assert))
        n_testfn = sum(1 for n in _ast.walk(tree)
                       if isinstance(n, _ast.FunctionDef) and n.name.startswith("test_"))
        ntests = n_assert + n_testfn
    except Exception:
        ntests = 0

    def run_fails(func_src):
        ns = {"__lg": __lg}
        __reset()
        try:
            exec(_guarded(func_src + "\\n" + student_tests), ns)
        except Exception:
            return True
        for k in list(ns):
            if k.startswith("test_") and callable(ns[k]):
                __reset()
                try:
                    ns[k]()
                except Exception:
                    return True
        return False

    try:
        ref_fail = run_fails(data["reference_impl"])
    except Exception as e:
        return {"mode": mode, "ok": False, "error": "Seu teste nao roda: " + repr(e), "mutants": []}
    ref_ok = not ref_fail
    mutants = data["mutants"]
    mutant_results = []
    killed = 0
    for i, m in enumerate(mutants):
        try:
            dead = run_fails(m)
        except Exception:
            dead = True
        if dead:
            killed += 1
        mutant_results.append({"index": i, "killed": bool(dead)})
    enough = ntests >= min_tests
    ok = ref_ok and killed == len(mutants) and enough
    return {"mode": mode, "ok": bool(ok), "ref_ok": bool(ref_ok), "n_tests": ntests, "min_tests": min_tests, "enough": bool(enough), "killed": killed, "total_mutants": len(mutants), "mutants": mutant_results}

import json as __json
__json.dumps(__main())
`;

export async function runExercise(exercise, studentCode) {
  let data;
  if (exercise.mode === "write_test") {
    data = {
      mode: "write_test",
      student: studentCode,
      reference_impl: exercise.reference_impl,
      mutants: exercise.mutants || [],
      min_tests: exercise.min_tests || 1,
    };
  } else {
    data = {mode: "write_code", student: studentCode, tests: exercise.tests || []};
  }
  const payload = b64utf8(JSON.stringify(data));
  const harness = '__PAYLOAD = "' + payload + '"\n' + LOGIC;

  // Backup contra travamento: a thread principal tenta interromper após 8s.
  const killer = setTimeout(() => { interruptRaw(); }, RUN_TIMEOUT_MS);
  let raw;
  try {
    raw = await runRawPython(harness);
  } catch (e) {
    return {mode: exercise.mode, ok: false, error: "Falha ao executar (o servidor está rodando?): " + (e && e.message ? e.message : String(e))};
  } finally {
    clearTimeout(killer);
  }
  if (typeof raw === "string" && raw.startsWith("__PRACTICE_PYERROR__")) {
    return {mode: exercise.mode, ok: false, error: raw.replace("__PRACTICE_PYERROR__", "")};
  }
  try {
    return JSON.parse(raw);
  } catch (e) {
    return {mode: exercise.mode, ok: false, error: "Resposta inválida do runner: " + String(raw).slice(0, 200)};
  }
}

export function stopExercise() { interruptRaw(); }

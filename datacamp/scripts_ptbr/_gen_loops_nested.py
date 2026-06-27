# -*- coding: utf-8 -*-
"""Normaliza o conteúdo gerado pelo agy (capítulo 'Loops Aninhadas') para o schema canônico
do exercises_br.json, VALIDA com rigor (roda soluções; replica o run_fails do runner para
provar que a referência passa e todos os mutantes morrem), grava o sidecar de soluções e
mescla no exercises_br.json. Uso pontual (Exercise Generator, P2-7). Idempotente.
"""
import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "futurecoder-patches" / "frontend" / "src"
EX_FILE = SRC / "exercises_br.json"
SOL_FILE = ROOT / "docs" / "exercises_solutions.json"
sys.path.insert(0, str(ROOT))
from athena import exercise_generator as gen  # noqa

CHAPTER = "Loops Aninhadas"

# Conteúdo gerado pelo agy (0-quota), normalizado ao schema canônico (mode/level/prompt/...).
CHAPTER_OBJ = {
    "title": CHAPTER,
    "exercises": [
        {
            "id": "loops-nested-n1-coordinate-finder",
            "level": 1, "mode": "write_code",
            "title": "Localizador de coordenadas numa matriz",
            "concept": "for dentro de for (varrer matriz)",
            "prompt": ("Em automação de testes de UI, a gente acha elementos numa grade de tela "
                       "(matriz = lista de listas). Escreva `find_element_coordinates(grid, target)` "
                       "que percorre a matriz com loops aninhados (linha por linha, coluna por coluna) "
                       "e RETORNA uma lista com as coordenadas `[linha, coluna]` de cada ocorrência de "
                       "`target`. Caso-limite de QA: se não achar nada — ou a grade for vazia — retorne `[]`. "
                       "Use LISTAS `[r, c]`, nunca tuplas."),
            "starter": "def find_element_coordinates(grid, target):\n    # use dois for aninhados e devolva uma lista de [linha, coluna]\n    ...\n",
            "solution": "def find_element_coordinates(grid, target):\n    if not grid or not grid[0]:\n        return []\n    coordinates = []\n    for r in range(len(grid)):\n        for c in range(len(grid[r])):\n            if grid[r][c] == target:\n                coordinates.append([r, c])\n    return coordinates\n",
            "tests": [
                {"call": "find_element_coordinates([[1, 2, 3], [4, 5, 2], [2, 7, 8]], 2)", "expect": [[0, 1], [1, 2], [2, 0]]},
                {"call": "find_element_coordinates([[9, 9], [9, 9]], 9)", "expect": [[0, 0], [0, 1], [1, 0], [1, 1]]},
                {"call": "find_element_coordinates([[1, 2], [3, 4]], 5)", "expect": []},
                {"call": "find_element_coordinates([], 1)", "expect": []},
            ],
            "hints": [
                "Use `for r in range(len(grid))` para as linhas e, dentro, `for c in range(len(grid[r]))` para as colunas.",
                "No loop interno, compare `grid[r][c] == target`. Se bater, guarde a coordenada na lista de resultados.",
                "Guarde como LISTA: `coordinates.append([r, c])`. Tuplas `(r, c)` não batem com o JSON do validador.",
            ],
            "xp": 10,
        },
        {
            "id": "loops-nested-n2-faulty-sensors",
            "level": 2, "mode": "write_code",
            "title": "Mapa de sensores com defeito (matriz irregular)",
            "concept": "loops aninhados em matriz jagged + condição",
            "prompt": ("Validando sensores dispostos numa matriz, valor negativo = sensor com defeito. "
                       "Escreva `find_faulty_sensors(matrix)` que RETORNA a lista de coordenadas "
                       "`[linha, coluna]` de todos os valores < 0. As linhas podem ter tamanhos "
                       "diferentes (matriz irregular/jagged) — sua varredura precisa aguentar isso "
                       "sem estourar índice. Caso-limite: matriz vazia ou linha vazia → `[]`."),
            "starter": "def find_faulty_sensors(matrix):\n    # varra cada linha pelo SEU tamanho (jagged) e colete os [r, c] negativos\n    ...\n",
            "solution": "def find_faulty_sensors(matrix):\n    faults = []\n    for r in range(len(matrix)):\n        for c in range(len(matrix[r])):\n            if matrix[r][c] < 0:\n                faults.append([r, c])\n    return faults\n",
            "tests": [
                {"call": "find_faulty_sensors([[1, -2, 3], [-4, 5], [6, 7, -8, 9]])", "expect": [[0, 1], [1, 0], [2, 2]]},
                {"call": "find_faulty_sensors([[0, 1, 2], [3, 4]])", "expect": []},
                {"call": "find_faulty_sensors([[-1, -2], [], [-3]])", "expect": [[0, 0], [0, 1], [2, 0]]},
                {"call": "find_faulty_sensors([])", "expect": []},
            ],
            "hints": [
                "Para matriz jagged, use `range(len(matrix[r]))` (o tamanho DA linha r), não um número fixo de colunas.",
                "Condição: `if matrix[r][c] < 0:` então `faults.append([r, c])`.",
                "Uma linha vazia `[]` simplesmente não entra no loop interno — não precisa de tratamento especial.",
            ],
            "xp": 15,
        },
        {
            "id": "loops-nested-n3-matrix-overlap",
            "level": 3, "mode": "write_test",
            "title": "Pense como QA: teste has_overlap (sobreposição em matriz)",
            "concept": "Arrange/Act/Assert — um bom teste pega o bug (loops aninhados)",
            "prompt": ("A função `has_overlap(matrix_a, matrix_b)` já existe (read-only): devolve `True` se "
                       "existir ALGUMA posição `[r][c]` onde ambas as matrizes têm 1, senão `False` "
                       "(e `False` se alguma for vazia). Escreva pelo menos 3 testes `def test_*()` que "
                       "chamam `has_overlap(...)` e PEGAM bugs: (1) sobreposição numa linha que não é a "
                       "primeira; (2) 1s em ambas mas em posições DIFERENTES (não é overlap); (3) o "
                       "caso-limite de matriz vazia. Um bom teste mata os 3 mutantes."),
            "target_func": "has_overlap",
            "reference_impl": "def has_overlap(matrix_a, matrix_b):\n    if not matrix_a or not matrix_b:\n        return False\n    for r in range(len(matrix_a)):\n        for c in range(len(matrix_a[r])):\n            if matrix_a[r][c] == 1 and matrix_b[r][c] == 1:\n                return True\n    return False\n",
            "mutants": [
                # #1 remove a guarda de vazio -> IndexError quando b é menor (matável com a=[[1]], b=[])
                "def has_overlap(matrix_a, matrix_b):\n    for r in range(len(matrix_a)):\n        for c in range(len(matrix_a[r])):\n            if matrix_a[r][c] == 1 and matrix_b[r][c] == 1:\n                return True\n    return False\n",
                # #2 True se cada uma tem 1 em QUALQUER lugar (não na mesma posição)
                "def has_overlap(matrix_a, matrix_b):\n    if not matrix_a or not matrix_b:\n        return False\n    has_a = False\n    has_b = False\n    for r in range(len(matrix_a)):\n        for c in range(len(matrix_a[r])):\n            if matrix_a[r][c] == 1:\n                has_a = True\n            if matrix_b[r][c] == 1:\n                has_b = True\n    return has_a and has_b\n",
                # #3 só checa a primeira linha (return False prematuro dentro do for externo)
                "def has_overlap(matrix_a, matrix_b):\n    if not matrix_a or not matrix_b:\n        return False\n    for r in range(len(matrix_a)):\n        for c in range(len(matrix_a[r])):\n            if matrix_a[r][c] == 1 and matrix_b[r][c] == 1:\n                return True\n        return False\n    return False\n",
            ],
            "min_tests": 3,
            "starter": "# A função has_overlap já existe e está correta.\n# Escreva seus testes abaixo (def test_*), pensando nos 3 bugs.\ndef test_overlap_em_linha_posterior():\n    ...\n",
            "hints": [
                "Pra matar o mutante que checa só a 1ª linha: ponha o overlap numa linha de baixo, ex. `has_overlap([[0],[1]], [[0],[1]])` deve ser True.",
                "Pra matar o mutante 'tem 1 em qualquer lugar': 1 em A e 1 em B mas em posições diferentes deve dar False, ex. `has_overlap([[1,0]], [[0,1]])`.",
                "Pra matar o mutante sem guarda de vazio: teste `has_overlap([[1]], [])` — deve ser False (e o mutante quebra).",
            ],
            "xp": 30,
        },
    ],
}

# Conjunto de testes CORRETOS (do professor) p/ provar que os mutantes são matáveis (replica run_fails).
PROOF_TESTS = """
def test_overlap_linha_posterior():
    assert has_overlap([[0],[1]], [[0],[1]]) == True
def test_uns_em_posicoes_diferentes():
    assert has_overlap([[1,0]], [[0,1]]) == False
def test_matriz_vazia():
    assert has_overlap([[1]], []) == False
    assert has_overlap([], [[1]]) == False
def test_overlap_simples():
    assert has_overlap([[1,1]], [[0,1]]) == True
"""


def run_fails(func_src, tests_src):
    """Replica PyodideRunner.run_fails: exec(func+tests); falha se algum test_* levanta/erra."""
    ns = {}
    try:
        exec(func_src + "\n" + tests_src, ns)
    except Exception:
        return True
    for k in list(ns):
        if k.startswith("test_") and callable(ns[k]):
            try:
                ns[k]()
            except Exception:
                return True
    return False


def main():
    # 1) Valida write_code (roda soluções, exige listas/JSON-fiel)
    ok, errors, solutions = gen.validate_chapter(CHAPTER_OBJ)
    print("write_code/levels valid:", ok)
    for e in errors:
        print("  ERRO:", e)

    # 2) Valida write_test replicando o runner com testes corretos do professor
    n3 = next(e for e in CHAPTER_OBJ["exercises"] if e["mode"] == "write_test")
    ref_fail = run_fails(n3["reference_impl"], PROOF_TESTS)
    print("write_test: referência passa nos testes-prova:", not ref_fail)
    killed = 0
    for i, m in enumerate(n3["mutants"]):
        dead = run_fails(m, PROOF_TESTS)
        print(f"  mutante #{i} morto:", dead)
        killed += 1 if dead else 0
    wt_ok = (not ref_fail) and killed == len(n3["mutants"])
    print(f"write_test válido (ref ok + {killed}/{len(n3['mutants'])} mortos):", wt_ok)

    if not (ok and wt_ok):
        print("\n>>> VALIDAÇÃO FALHOU — não vou mesclar.")
        sys.exit(1)

    # 3) Tira as 'solution' do bundle -> sidecar; grava capítulo limpo
    clean = {"title": CHAPTER, "exercises": []}
    for e in CHAPTER_OBJ["exercises"]:
        e2 = {k: v for k, v in e.items() if k != "solution"}
        clean["exercises"].append(e2)

    ex_data = json.loads(EX_FILE.read_text(encoding="utf-8"))
    ex_data[CHAPTER] = clean
    EX_FILE.write_text(json.dumps(ex_data, ensure_ascii=False, indent=2), encoding="utf-8")

    sol_data = json.loads(SOL_FILE.read_text(encoding="utf-8")) if SOL_FILE.exists() else {}
    sol_data.update(solutions)
    SOL_FILE.write_text(json.dumps(sol_data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n>>> OK. Mesclado '{CHAPTER}' ({len(clean['exercises'])} exercícios) em exercises_br.json;"
          f" {len(solutions)} soluções no sidecar.")


if __name__ == "__main__":
    main()

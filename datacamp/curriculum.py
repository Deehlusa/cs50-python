# -*- coding: utf-8 -*-
"""
Currículo da Trilha Python para QA.

Camadas (a "base" + a prática):
  - BASE (teoria): futurecoder.io (interativo, pt-BR, MIT) + Pense em Python (CC).
  - PRÁTICA (aqui): exercícios QA-focused + validação agy.

Anatomia de cada exercício (inspirada em DataCamp / Exercism / freeCodeCamp):
  lesson       -> "Aprenda primeiro": o conceito em 2-3 linhas + mini-exemplo
  context      -> o quê + por quê
  instructions -> 2-4 passos curtos
  example      -> entrada -> saída
  qa_note      -> pra que serve no QA
  hint         -> ~50% do caminho (escondida)
  starter      -> código inicial (seed), SEM a solução
  tests        -> asserts que rodam no Pyodide

Cada capítulo tem: description, lesson (aula) e resources (links pra base em PT-BR).
O ALUNO escreve todas as soluções. Aqui não há solução pronta.
"""

# Capítulos: título -> {description, lesson, resources}.
# resources: lista de (label, url) com material de BASE gratuito em português.
CHAPTERS = {
    "1. Tipos e variáveis": {
        "description": "Como o Python guarda dados e como descobrir o tipo de cada valor.",
        "lesson": (
            "VARIÁVEL é uma caixa com nome onde você guarda um valor:\n"
            "    idade = 25\n"
            "    nome = 'Ana'\n"
            "O sinal = não é 'igual da matemática' — é 'guarde isto aqui'.\n"
            "\n"
            "TIPOS básicos (a 'forma' do valor):\n"
            "    int   -> número inteiro      ex: 25\n"
            "    float -> número com vírgula  ex: 3.14\n"
            "    str   -> texto (entre aspas) ex: 'Ana'\n"
            "    bool  -> verdadeiro/falso    ex: True, False\n"
            "\n"
            "type(valor) revela o tipo:\n"
            "    type(25)     -> <class 'int'>\n"
            "    type('Ana')  -> <class 'str'>\n"
            "\n"
            "CAST = trocar o tipo: int('5') -> 5 | str(5) -> '5' | float('2.5') -> 2.5\n"
            "No QA isso é crítico: '5' (texto) é DIFERENTE de 5 (número) — comparar "
            "os dois é um bug clássico."
        ),
        "resources": [
            ("Aprofundar: futurecoder (interativo)", "https://futurecoder.io/"),
            ("Aprofundar: Pense em Python — Variáveis", "https://penseallen.github.io/PensePython2e/"),
        ],
    },
    "2. Condicionais e lógica": {
        "description": "Tomar decisões no código com if/elif/else e operadores lógicos.",
        "lesson": (
            "`if` executa um bloco SÓ se uma condição for verdadeira; `else` é o "
            "'caso contrário'; `elif` encaixa casos no meio.\n"
            "Operadores lógicos combinam condições: `and` (e), `or` (ou), `not` (não).\n"
            "Analogia: um porteiro que decide quem entra conforme uma regra.\n"
            "No QA, toda asserção é uma condição que decide pass/fail."
        ),
        "resources": [
            ("futurecoder — condicionais (pt-BR)", "https://futurecoder.io/"),
            ("Pense em Python — Condicionais e recursão", "https://penseallen.github.io/PensePython2e/"),
        ],
    },
    "3. Loops": {
        "description": "Repetir ações com for e while.",
        "lesson": (
            "Um loop repete um bloco várias vezes. `for item in sequencia:` percorre "
            "cada item; `range(n)` gera 0,1,...,n-1.\n"
            "`break` para o loop; `continue` pula pro próximo item.\n"
            "Analogia: carimbar cada folha de uma pilha, uma por uma.\n"
            "Exemplo (diferente do exercício):\n"
            "  for n in range(3):\n"
            "      print(n)   # imprime 0, 1, 2"
        ),
        "resources": [
            ("futurecoder — loops (pt-BR)", "https://futurecoder.io/"),
            ("Pense em Python — Iteração", "https://penseallen.github.io/PensePython2e/"),
        ],
    },
    "4. Strings": {
        "description": "Manipular texto: dividir, juntar, inverter, normalizar.",
        "lesson": (
            "Strings têm métodos prontos: `.lower()`, `.upper()`, `.split()` (quebra "
            "em lista), `.strip()` (tira espaços).\n"
            "Fatiar (slicing): `s[0]` é o 1º caractere; `s[::-1]` inverte a string.\n"
            "Analogia: texto é uma fileira de letras que você pode cortar e remontar.\n"
            "No QA: comparar mensagens de log/UI exige normalizar o texto antes."
        ),
        "resources": [
            ("futurecoder — strings (pt-BR)", "https://futurecoder.io/"),
            ("Pense em Python — Strings", "https://penseallen.github.io/PensePython2e/"),
        ],
    },
    "5. Listas": {
        "description": "Guardar e transformar coleções de dados.",
        "lesson": (
            "Lista é uma coleção ORDENADA: `[10, 20, 30]`. Acesse por índice "
            "(`lista[0]` é o primeiro) e fatie (`lista[1:3]`).\n"
            "Métodos: `.append(x)` adiciona no fim, `.pop()` remove o último, "
            "`len(lista)` conta.\n"
            "Analogia: uma fila numerada onde a posição importa.\n"
            "No QA: listas guardam coleções de dados de teste (fixtures)."
        ),
        "resources": [
            ("futurecoder — listas (pt-BR)", "https://futurecoder.io/"),
            ("Pense em Python — Listas", "https://penseallen.github.io/PensePython2e/"),
        ],
    },
    "6. Dicionários, sets e tuplas": {
        "description": "Estruturas que viram fixtures, payloads JSON e comparações de conjuntos.",
        "lesson": (
            "Dicionário liga uma CHAVE a um VALOR: `{'nome': 'Ana'}` — acesse com "
            "`d['nome']`.\n"
            "Set é uma coleção SEM repetição e sem ordem: `{1, 2, 3}`.\n"
            "Tupla é uma lista IMUTÁVEL: `(1, 2)`.\n"
            "Analogia: dicionário é uma agenda (nome -> telefone).\n"
            "No QA: dicts são o formato de payloads JSON de API."
        ),
        "resources": [
            ("futurecoder — dicionários (pt-BR)", "https://futurecoder.io/"),
            ("Pense em Python — Dicionários", "https://penseallen.github.io/PensePython2e/"),
        ],
    },
    "7. Funções": {
        "description": "Empacotar lógica em funções reutilizáveis e testáveis.",
        "lesson": (
            "Função é um bloco com nome que recebe entradas (parâmetros) e devolve "
            "uma saída com `return`: `def soma(a, b): return a + b`.\n"
            "Função PURA não usa input()/print() dentro — só recebe e retorna. É a "
            "única que dá pra testar com pytest.\n"
            "Analogia: uma máquina — entra ingrediente, sai produto.\n"
            "Exemplo:  def dobro(n): return n * 2"
        ),
        "resources": [
            ("futurecoder — funções (pt-BR)", "https://futurecoder.io/"),
            ("Pense em Python — Funções", "https://penseallen.github.io/PensePython2e/"),
        ],
    },
    "8. Exceções": {
        "description": "Lidar com erros de propósito: try/except e raise.",
        "lesson": (
            "Erro (exceção) interrompe o programa. `try:` tenta algo e `except:` "
            "captura a falha sem quebrar tudo.\n"
            "`raise ValueError('msg')` lança um erro de propósito quando a entrada é "
            "inválida.\n"
            "Analogia: o disjuntor que desarma em vez de deixar a casa pegar fogo.\n"
            "No QA: testar entrada inválida que DEVE falhar = pytest.raises."
        ),
        "resources": [
            ("futurecoder — erros (pt-BR)", "https://futurecoder.io/"),
            ("Pense em Python — Tratamento de exceções", "https://penseallen.github.io/PensePython2e/"),
        ],
    },
    "9. JSON (API testing)": {
        "description": "Ler e gerar JSON com a biblioteca json.",
        "lesson": (
            "JSON é texto que representa dados (parece um dict). A biblioteca `json` "
            "converte os dois lados:\n"
            "  `json.loads(texto)` -> vira dict Python.\n"
            "  `json.dumps(dict)`  -> vira texto JSON.\n"
            "Analogia: tradutor entre o 'idioma' da API (texto) e o do Python (dict).\n"
            "No QA: você valida respostas de API o tempo todo."
        ),
        "resources": [
            ("Doc oficial Python — módulo json", "https://docs.python.org/pt-br/3/library/json.html"),
            ("Pense em Python", "https://penseallen.github.io/PensePython2e/"),
        ],
    },
    "10. OOP (base do Page Object Model)": {
        "description": "Classes: objetos com estado e comportamento.",
        "lesson": (
            "Classe é um molde de objeto. `__init__` é o construtor (roda ao criar); "
            "`self` é o próprio objeto; métodos são funções dentro da classe.\n"
            "  class Cachorro:\n"
            "      def __init__(self): self.late = 0\n"
            "      def latir(self): self.late += 1\n"
            "Analogia: a planta (classe) x a casa construída (objeto).\n"
            "No QA: é a base do Page Object Model no Playwright/Selenium."
        ),
        "resources": [
            ("futurecoder (pt-BR)", "https://futurecoder.io/"),
            ("Pense em Python — Classes e objetos", "https://penseallen.github.io/PensePython2e/"),
        ],
    },
}


TRACK = [
    # ===================== Cap 1 — Tipos e variáveis =====================
    {
        "ord": 1,
        "chapter": "1. Tipos e variáveis",
        "title": "Descrever um valor e seu tipo",
        "concept": "type(), f-strings, __name__",
        "lesson": (
            "`type(valor)` devolve o tipo; `.__name__` pega só o nome dele ('int').\n"
            "f-string monta texto com valores: f\"oi {nome}\".\n"
            "Ex: type(3.0).__name__  ->  'float'"
        ),
        "context": (
            "Em Python, todo valor tem um tipo (int, float, str, bool). Saber o tipo é "
            "o primeiro reflexo de quem testa software."
        ),
        "instructions": [
            "Crie a função `describe(value)`.",
            "Descubra o tipo com `type(value).__name__`.",
            "Retorne a string no formato '<valor> e do tipo <tipo>'.",
        ],
        "example": "describe(42)  ->  '42 e do tipo int'",
        "qa_note": "Validar tipos evita o bug clássico de comparar '5' (str) com 5 (int).",
        "hint": "Uma f-string resolve: f\"{value} e do tipo {type(value).__name__}\".",
        "starter": "def describe(value):\n    # monte a string com uma f-string\n    ...",
        "func": "describe",
        "tests": (
            "assert describe(42) == '42 e do tipo int'\n"
            "assert describe(3.5) == '3.5 e do tipo float'\n"
            "assert describe('oi') == 'oi e do tipo str'\n"
            "assert describe(True) == 'True e do tipo bool'\n"
        ),
        "points": 10,
    },
    {
        "ord": 2,
        "chapter": "1. Tipos e variáveis",
        "title": "Cast: texto para número",
        "concept": "float(), conversão de tipos",
        "lesson": (
            "Converter ('cast') troca o tipo de um valor. `float('1.5')` -> 1.5 ; "
            "`int('10')` -> 10.\n"
            "Cuidado: float('abc') dá erro (não é número)."
        ),
        "context": (
            "Dados quase sempre chegam como texto (CSV, formulário). Antes de fazer "
            "conta, é preciso converter a string em número."
        ),
        "instructions": [
            "Crie a função `to_number(s)`.",
            "Converta a string `s` para float.",
            "Retorne o número convertido.",
        ],
        "example": "to_number('3.14')  ->  3.14",
        "qa_note": "Massa de teste vem como texto; o cast errado é fonte comum de falha.",
        "hint": "A função embutida float() converte '3.14' em número.",
        "starter": "def to_number(s):\n    ...",
        "func": "to_number",
        "tests": (
            "assert to_number('3.14') == 3.14\n"
            "assert to_number('10') == 10.0\n"
            "assert to_number('-2.5') == -2.5\n"
        ),
        "points": 10,
    },

    # ===================== Cap 2 — Condicionais e lógica =====================
    {
        "ord": 3,
        "chapter": "2. Condicionais e lógica",
        "title": "Classificar um número",
        "concept": "if / elif / else",
        "lesson": (
            "Use if/elif/else pra escolher um caminho por vez:\n"
            "  if x > 0: ...\n  elif x == 0: ...\n  else: ...\n"
            "Só UM dos blocos roda."
        ),
        "context": (
            "Condicionais decidem o caminho do código conforme o valor. Toda "
            "verificação de teste nasce de uma decisão como esta."
        ),
        "instructions": [
            "Crie a função `classify(n)`.",
            "Retorne 'negativo' se n < 0, 'zero' se n == 0, 'positivo' se n > 0.",
        ],
        "example": "classify(-5) -> 'negativo' ; classify(0) -> 'zero'",
        "qa_note": "Cobrir os 3 ramos (negativo/zero/positivo) é 'branch coverage'.",
        "hint": "Um ramo if/elif/else para cada caso.",
        "starter": "def classify(n):\n    ...",
        "func": "classify",
        "tests": (
            "assert classify(-5) == 'negativo'\n"
            "assert classify(0) == 'zero'\n"
            "assert classify(7) == 'positivo'\n"
        ),
        "points": 10,
    },
    {
        "ord": 4,
        "chapter": "2. Condicionais e lógica",
        "title": "Maior de três",
        "concept": "comparações, lógica",
        "lesson": (
            "Comparações devolvem True/False: `5 > 3` -> True.\n"
            "A função `max()` já devolve o maior: `max(2, 9, 4)` -> 9."
        ),
        "context": (
            "Comparar valores é o que mais se faz em testes: o esperado x o obtido. "
            "Aqui você compara três números e devolve o maior."
        ),
        "instructions": [
            "Crie a função `max_of_three(a, b, c)`.",
            "Retorne o maior entre os três.",
            "Trate empates retornando o próprio valor.",
        ],
        "example": "max_of_three(1, 9, 3)  ->  9",
        "qa_note": "Comparar esperado x obtido é o coração de toda asserção.",
        "hint": "max() aceita vários argumentos: max(a, b, c).",
        "starter": "def max_of_three(a, b, c):\n    ...",
        "func": "max_of_three",
        "tests": (
            "assert max_of_three(1, 2, 3) == 3\n"
            "assert max_of_three(9, 2, 3) == 9\n"
            "assert max_of_three(5, 5, 5) == 5\n"
            "assert max_of_three(-1, -7, -3) == -1\n"
        ),
        "points": 15,
    },
    {
        "ord": 5,
        "chapter": "2. Condicionais e lógica",
        "title": "Ano bissexto",
        "concept": "and / or / not, regras compostas",
        "lesson": (
            "Combine condições com and/or: `(a and b)` só é True se as DUAS forem.\n"
            "`x % 4 == 0` testa se x é divisível por 4 (resto zero)."
        ),
        "context": (
            "Regras reais combinam várias condições. A do ano bissexto é famosa por "
            "ter armadilhas (1900 não é, 2000 é)."
        ),
        "instructions": [
            "Crie a função `is_leap(year)`.",
            "Regra: divisível por 4, MAS não por 100, EXCETO se divisível por 400.",
            "Retorne True ou False.",
        ],
        "example": "is_leap(2000) -> True ; is_leap(1900) -> False",
        "qa_note": "Cheia de edge cases — ouro pra treinar a mentalidade de quem quebra software.",
        "hint": "year % 4 == 0 and (year % 100 != 0 or year % 400 == 0).",
        "starter": "def is_leap(year):\n    ...",
        "func": "is_leap",
        "tests": (
            "assert is_leap(2024) == True\n"
            "assert is_leap(2023) == False\n"
            "assert is_leap(1900) == False\n"
            "assert is_leap(2000) == True\n"
        ),
        "points": 20,
    },

    # ===================== Cap 3 — Loops =====================
    {
        "ord": 6,
        "chapter": "3. Loops",
        "title": "Somar os pares",
        "concept": "for, range, %, acumulador",
        "lesson": (
            "Acumulador: uma variável que cresce dentro do loop.\n"
            "  total = 0\n  for n in range(4): total += n   # 0+1+2+3 = 6\n"
            "`n % 2 == 0` testa se n é par."
        ),
        "context": "Um loop percorre uma sequência fazendo algo em cada passo.",
        "instructions": [
            "Crie a função `total_even(n)`.",
            "Percorra de 0 até n (inclusive) com `range`.",
            "Some apenas os pares e retorne o total.",
        ],
        "example": "total_even(6)  ->  0+2+4+6 = 12",
        "qa_note": "Loops percorrem listas de casos de teste.",
        "hint": "Use range(n+1) e teste cada número com `i % 2 == 0`.",
        "starter": "def total_even(n):\n    total = 0\n    # percorra e acumule\n    ...",
        "func": "total_even",
        "tests": (
            "assert total_even(6) == 12\n"
            "assert total_even(0) == 0\n"
            "assert total_even(1) == 0\n"
            "assert total_even(10) == 30\n"
        ),
        "points": 15,
    },
    {
        "ord": 7,
        "chapter": "3. Loops",
        "title": "Fatorial",
        "concept": "for, multiplicação acumulada",
        "lesson": (
            "Aqui o acumulador MULTIPLICA (começa em 1, não em 0):\n"
            "  result = 1\n  for i in range(1, 4): result *= i   # 1*1*2*3 = 6"
        ),
        "context": (
            "O fatorial multiplica todos os inteiros de 1 até n. O caso n=0 vale 1 — "
            "um caso-limite que muita gente esquece."
        ),
        "instructions": [
            "Crie a função `factorial(n)`.",
            "Multiplique 1 * 2 * ... * n.",
            "Garanta que `factorial(0)` retorne 1.",
        ],
        "example": "factorial(5)  ->  120",
        "qa_note": "factorial(0) == 1 é o caso-limite clássico (boundary value).",
        "hint": "Comece com result = 1 e multiplique dentro de um for.",
        "starter": "def factorial(n):\n    result = 1\n    ...",
        "func": "factorial",
        "tests": (
            "assert factorial(0) == 1\n"
            "assert factorial(1) == 1\n"
            "assert factorial(5) == 120\n"
        ),
        "points": 15,
    },
    {
        "ord": 8,
        "chapter": "3. Loops",
        "title": "Contar vogais",
        "concept": "for em string, contador, in",
        "lesson": (
            "Dá pra percorrer cada letra: `for c in 'abc':`.\n"
            "`c in 'aeiou'` é True se a letra for vogal."
        ),
        "context": "Você pode percorrer cada caractere de um texto com um for.",
        "instructions": [
            "Crie a função `count_vowels(text)`.",
            "Percorra cada caractere de `text`.",
            "Conte quantos são vogais (a, e, i, o, u).",
        ],
        "example": "count_vowels('banana')  ->  3",
        "qa_note": "Percorrer texto valida limpeza e normalização de dados.",
        "hint": "if c in 'aeiou': some 1 no contador.",
        "starter": "def count_vowels(text):\n    count = 0\n    ...",
        "func": "count_vowels",
        "tests": (
            "assert count_vowels('banana') == 3\n"
            "assert count_vowels('xyz') == 0\n"
            "assert count_vowels('') == 0\n"
        ),
        "points": 15,
    },
    {
        "ord": 9,
        "chapter": "3. Loops",
        "title": "FizzBuzz",
        "concept": "for, %, ordem das condições",
        "lesson": (
            "Quando condições se sobrepõem, a ORDEM importa: teste a mais específica "
            "primeiro.\n"
            "Múltiplo de 3 E de 5 = múltiplo de 15 — cheque o 15 antes."
        ),
        "context": (
            "O clássico de entrevista. O pulo do gato é a ORDEM: testar o múltiplo de "
            "15 ANTES dos de 3 e 5."
        ),
        "instructions": [
            "Crie `fizzbuzz(n)` que retorne uma lista de 1 até n.",
            "Múltiplo de 3 -> 'Fizz'; de 5 -> 'Buzz'; de ambos -> 'FizzBuzz'.",
            "Os demais entram como o próprio número (int).",
        ],
        "example": "fizzbuzz(5)  ->  [1, 2, 'Fizz', 4, 'Buzz']",
        "qa_note": "Treina ordem de condições — um erro de ordem aqui passa despercebido.",
        "hint": "Cheque `i % 15 == 0` primeiro, depois `% 3`, depois `% 5`, senão o número.",
        "starter": "def fizzbuzz(n):\n    out = []\n    for i in range(1, n + 1):\n        ...\n    return out",
        "func": "fizzbuzz",
        "tests": (
            "assert fizzbuzz(5) == [1, 2, 'Fizz', 4, 'Buzz']\n"
            "assert fizzbuzz(15)[-1] == 'FizzBuzz'\n"
            "assert fizzbuzz(3) == [1, 2, 'Fizz']\n"
        ),
        "points": 20,
    },
    {
        "ord": 10,
        "chapter": "3. Loops",
        "title": "Primeiro negativo (break)",
        "concept": "for + break / return antecipado",
        "lesson": (
            "`return` dentro de um loop já SAI do loop e da função na hora.\n"
            "  for n in nums:\n      if n < 0: return n"
        ),
        "context": "Às vezes você quer parar assim que achar o que procura.",
        "instructions": [
            "Crie a função `first_negative(nums)`.",
            "Retorne o primeiro número negativo da lista.",
            "Se não houver nenhum, retorne None.",
        ],
        "example": "first_negative([1, 2, -3, 4])  ->  -3",
        "qa_note": "Parar no primeiro erro encontrado é padrão em validação de dados.",
        "hint": "Quando achar negativo, dê `return n` (já sai do loop).",
        "starter": "def first_negative(nums):\n    for n in nums:\n        ...\n    return None",
        "func": "first_negative",
        "tests": (
            "assert first_negative([1, 2, -3, 4]) == -3\n"
            "assert first_negative([1, 2, 3]) is None\n"
            "assert first_negative([]) is None\n"
        ),
        "points": 15,
    },

    # ===================== Cap 4 — Strings =====================
    {
        "ord": 11,
        "chapter": "4. Strings",
        "title": "Inverter a ordem das palavras",
        "concept": "split(), join(), slicing",
        "lesson": (
            "`'a b c'.split()` -> ['a','b','c'].\n"
            "`' '.join(['c','b','a'])` -> 'c b a'.\n"
            "`lista[::-1]` inverte a lista."
        ),
        "context": "`split` quebra em lista, `join` junta de volta.",
        "instructions": [
            "Crie a função `reverse_words(s)`.",
            "Separe as palavras, inverta a ordem e junte de novo com espaço.",
        ],
        "example": "reverse_words('ola mundo')  ->  'mundo ola'",
        "qa_note": "Manipular texto é rotina ao comparar mensagens de log e UI.",
        "hint": "s.split() vira lista; inverta com [::-1]; junte com ' '.join(...).",
        "starter": "def reverse_words(s):\n    ...",
        "func": "reverse_words",
        "tests": (
            "assert reverse_words('ola mundo') == 'mundo ola'\n"
            "assert reverse_words('a b c') == 'c b a'\n"
            "assert reverse_words('python') == 'python'\n"
        ),
        "points": 15,
    },
    {
        "ord": 12,
        "chapter": "4. Strings",
        "title": "Palíndromo",
        "concept": "lower(), slicing [::-1]",
        "lesson": (
            "`s[::-1]` lê a string de trás pra frente.\n"
            "`s.lower()` deixa tudo minúsculo (pra comparar sem ligar pro caso)."
        ),
        "context": "Antes de comparar textos, normalize (ex: tudo minúsculo).",
        "instructions": [
            "Crie a função `is_palindrome(s)`.",
            "Ignore maiúsculas/minúsculas.",
            "Retorne True se for palíndromo, False caso contrário.",
        ],
        "example": "is_palindrome('Ana')  ->  True",
        "qa_note": "Normalizar antes de comparar (case-insensitive) é mentalidade de teste.",
        "hint": "Compare s.lower() com s.lower()[::-1].",
        "starter": "def is_palindrome(s):\n    ...",
        "func": "is_palindrome",
        "tests": (
            "assert is_palindrome('Ana') == True\n"
            "assert is_palindrome('casa') == False\n"
            "assert is_palindrome('Osso') == True\n"
        ),
        "points": 20,
    },

    # ===================== Cap 5 — Listas =====================
    {
        "ord": 13,
        "chapter": "5. Listas",
        "title": "Últimos n elementos",
        "concept": "slicing de lista",
        "lesson": (
            "Índice negativo conta do fim: `lista[-1]` é o último.\n"
            "`lista[-2:]` pega os 2 últimos. `lista[3:]` pega do 4º em diante."
        ),
        "context": "Slicing pega pedaços de uma lista sem precisar de loop.",
        "instructions": [
            "Crie a função `last_n(items, n)`.",
            "Retorne os últimos n elementos da lista.",
            "Se n for maior que a lista, retorne a lista inteira.",
        ],
        "example": "last_n([1, 2, 3, 4], 2)  ->  [3, 4]",
        "qa_note": "Pegar os últimos resultados é comum ao checar histórico/logs.",
        "hint": "items[-n:] pega os últimos n — mas cuidado com o caso n == 0.",
        "starter": "def last_n(items, n):\n    ...",
        "func": "last_n",
        "tests": (
            "assert last_n([1,2,3,4], 2) == [3, 4]\n"
            "assert last_n([1,2,3], 0) == []\n"
            "assert last_n(['a','b'], 5) == ['a', 'b']\n"
        ),
        "points": 15,
    },
    {
        "ord": 14,
        "chapter": "5. Listas",
        "title": "Remover duplicatas (mantendo ordem)",
        "concept": "loop, in, lista de resultado",
        "lesson": (
            "`x in lista` é True se x já está na lista.\n"
            "Monte uma lista nova e só adicione o que ainda não entrou."
        ),
        "context": "Um set remove duplicatas mas perde a ordem — aqui a ordem importa.",
        "instructions": [
            "Crie a função `unique(items)`.",
            "Remova duplicatas mantendo a ordem da primeira aparição.",
        ],
        "example": "unique([1, 1, 2, 3, 2])  ->  [1, 2, 3]",
        "qa_note": "Deduplicar dados de teste sem perder a ordem de inserção.",
        "hint": "Adicione numa lista nova só se o item ainda não estiver nela.",
        "starter": "def unique(items):\n    result = []\n    ...\n    return result",
        "func": "unique",
        "tests": (
            "assert unique([1, 1, 2, 3, 2]) == [1, 2, 3]\n"
            "assert unique([]) == []\n"
            "assert unique(['a', 'b', 'a']) == ['a', 'b']\n"
        ),
        "points": 20,
    },
    {
        "ord": 15,
        "chapter": "5. Listas",
        "title": "Achatar uma matriz",
        "concept": "for aninhado, extend/append",
        "lesson": (
            "`.extend(outra_lista)` adiciona TODOS os itens de uma vez.\n"
            "  r = [1]; r.extend([2, 3])  ->  [1, 2, 3]"
        ),
        "context": "Respostas de API costumam vir aninhadas (listas dentro de listas).",
        "instructions": [
            "Crie a função `flatten(matrix)`.",
            "Percorra cada sublista e junte todos os elementos numa lista única.",
        ],
        "example": "flatten([[1, 2], [3]])  ->  [1, 2, 3]",
        "qa_note": "Achatar respostas aninhadas de API antes de validar.",
        "hint": "Um for nas sublistas + result.extend(sublista).",
        "starter": "def flatten(matrix):\n    result = []\n    ...\n    return result",
        "func": "flatten",
        "tests": (
            "assert flatten([[1, 2], [3]]) == [1, 2, 3]\n"
            "assert flatten([]) == []\n"
            "assert flatten([[1], [2], [3]]) == [1, 2, 3]\n"
        ),
        "points": 20,
    },
    {
        "ord": 16,
        "chapter": "5. Listas",
        "title": "Os dois maiores",
        "concept": "sorted(), slicing, reverse",
        "lesson": (
            "`sorted(lista)` devolve uma cópia ordenada (crescente).\n"
            "`sorted(lista, reverse=True)` ordena do maior pro menor."
        ),
        "context": "Ordenar é meio caminho pra ranquear.",
        "instructions": [
            "Crie a função `top_two(nums)`.",
            "Retorne os 2 maiores números em ordem decrescente.",
        ],
        "example": "top_two([3, 1, 4, 1, 5])  ->  [5, 4]",
        "qa_note": "Ranquear resultados e checar o topo de uma lista ordenada.",
        "hint": "sorted(nums, reverse=True)[:2].",
        "starter": "def top_two(nums):\n    ...",
        "func": "top_two",
        "tests": (
            "assert top_two([3, 1, 4, 1, 5]) == [5, 4]\n"
            "assert top_two([10, 20]) == [20, 10]\n"
            "assert top_two([7, 7, 1]) == [7, 7]\n"
        ),
        "points": 20,
    },

    # ============== Cap 6 — Dicionários, sets e tuplas ==============
    {
        "ord": 17,
        "chapter": "6. Dicionários, sets e tuplas",
        "title": "Contar caracteres",
        "concept": "dict, get, contagem",
        "lesson": (
            "`d.get(chave, 0)` devolve o valor OU 0 se a chave não existe.\n"
            "Padrão de contagem:  d[c] = d.get(c, 0) + 1"
        ),
        "context": "Um dicionário guarda pares chave->valor.",
        "instructions": [
            "Crie a função `count_chars(text)`.",
            "Para cada caractere, some 1 na contagem dele.",
            "Retorne o dicionário {caractere: contagem}.",
        ],
        "example": "count_chars('aab')  ->  {'a': 2, 'b': 1}",
        "qa_note": "Dicts são o formato de fixtures e de payloads JSON.",
        "hint": "d[c] = d.get(c, 0) + 1 incrementa sem checar se a chave existe.",
        "starter": "def count_chars(text):\n    counts = {}\n    ...\n    return counts",
        "func": "count_chars",
        "tests": (
            "assert count_chars('aab') == {'a': 2, 'b': 1}\n"
            "assert count_chars('') == {}\n"
            "assert count_chars('xxx') == {'x': 3}\n"
        ),
        "points": 20,
    },
    {
        "ord": 18,
        "chapter": "6. Dicionários, sets e tuplas",
        "title": "Somar duas contagens",
        "concept": "dict, get, iterar itens",
        "lesson": (
            "`d.items()` dá pares (chave, valor) pra percorrer:\n"
            "  for k, v in d.items(): ...\n"
            "`dict(a)` faz uma cópia de a."
        ),
        "context": "Mesclar dois dicionários somando os valores das chaves iguais.",
        "instructions": [
            "Crie a função `merge_counts(a, b)`.",
            "Some os valores das chaves que existem nos dois.",
            "Mantenha as chaves que existem só em um deles.",
        ],
        "example": "merge_counts({'a':1}, {'a':2,'b':1})  ->  {'a':3, 'b':1}",
        "qa_note": "Mesclar métricas/contagens de dois lotes de teste.",
        "hint": "Copie `a`, depois percorra `b.items()` somando com result.get(k, 0).",
        "starter": "def merge_counts(a, b):\n    result = dict(a)\n    ...\n    return result",
        "func": "merge_counts",
        "tests": (
            "assert merge_counts({'a':1}, {'a':2,'b':1}) == {'a':3,'b':1}\n"
            "assert merge_counts({}, {'x':5}) == {'x':5}\n"
            "assert merge_counts({'k':1}, {}) == {'k':1}\n"
        ),
        "points": 25,
    },
    {
        "ord": 19,
        "chapter": "6. Dicionários, sets e tuplas",
        "title": "Elementos em comum (set)",
        "concept": "set, interseção",
        "lesson": (
            "`set([1,2,2])` -> {1, 2} (sem repetição).\n"
            "`set(a) & set(b)` devolve o que existe nos DOIS (interseção)."
        ),
        "context": "Um set é uma coleção sem repetição, ótima pra comparar grupos.",
        "instructions": [
            "Crie a função `common(a, b)`.",
            "Retorne um set com os elementos presentes nas DUAS listas.",
        ],
        "example": "common([1,2,3], [2,3,4])  ->  {2, 3}",
        "qa_note": "Comparar conjuntos: campos esperados x campos retornados pela API.",
        "hint": "set(a) & set(b) calcula a interseção.",
        "starter": "def common(a, b):\n    ...",
        "func": "common",
        "tests": (
            "assert common([1,2,3], [2,3,4]) == {2, 3}\n"
            "assert common([1], [2]) == set()\n"
            "assert common([1,1,2], [2,2,3]) == {2}\n"
        ),
        "points": 20,
    },
    {
        "ord": 20,
        "chapter": "6. Dicionários, sets e tuplas",
        "title": "Mínimo e máximo (tupla)",
        "concept": "tupla, retorno múltiplo",
        "lesson": (
            "Uma tupla agrupa valores: `(1, 3)`.\n"
            "`return min(x), max(x)` já devolve uma tupla com os dois."
        ),
        "context": "Uma função pode devolver vários valores de uma vez usando tupla.",
        "instructions": [
            "Crie a função `min_max(nums)`.",
            "Retorne uma tupla (menor, maior).",
        ],
        "example": "min_max([3, 1, 2])  ->  (1, 3)",
        "qa_note": "Retornar a faixa min/max de um dataset numa tacada só.",
        "hint": "return (min(nums), max(nums)).",
        "starter": "def min_max(nums):\n    ...",
        "func": "min_max",
        "tests": (
            "assert min_max([3, 1, 2]) == (1, 3)\n"
            "assert min_max([5]) == (5, 5)\n"
            "assert min_max([-2, 0, 9]) == (-2, 9)\n"
        ),
        "points": 20,
    },

    # ===================== Cap 7 — Funções =====================
    {
        "ord": 21,
        "chapter": "7. Funções",
        "title": "Aplicar desconto (função pura)",
        "concept": "return em vez de print",
        "lesson": (
            "Função pura: recebe, calcula e RETORNA — sem print/input dentro.\n"
            "É o que permite testar: o teste compara o que ela retorna."
        ),
        "context": "Função pura é a ÚNICA que dá pra testar de verdade com pytest.",
        "instructions": [
            "Crie a função `apply_discount(price, percent)`.",
            "Retorne o preço com o desconto aplicado.",
            "Não use print nem input.",
        ],
        "example": "apply_discount(100, 10)  ->  90.0",
        "qa_note": "Separar lógica de I/O é o pré-requisito pra escrever testes.",
        "hint": "preço - (preço * percent / 100).",
        "starter": "def apply_discount(price, percent):\n    ...",
        "func": "apply_discount",
        "tests": (
            "assert apply_discount(100, 10) == 90.0\n"
            "assert apply_discount(50, 0) == 50.0\n"
            "assert apply_discount(200, 50) == 100.0\n"
        ),
        "points": 25,
    },
    {
        "ord": 22,
        "chapter": "7. Funções",
        "title": "Clamp (limitar a um intervalo)",
        "concept": "função com 3 parâmetros",
        "lesson": (
            "Funções aninhadas resolvem isso elegante:\n"
            "  min(n, high) garante teto; max(low, ...) garante piso."
        ),
        "context": "Clamp prende um valor dentro de um intervalo [low, high].",
        "instructions": [
            "Crie a função `clamp(n, low, high)`.",
            "Retorne low se n < low, high se n > high, senão o próprio n.",
        ],
        "example": "clamp(15, 0, 10)  ->  10",
        "qa_note": "Validar que um valor está dentro de um intervalo permitido.",
        "hint": "max(low, min(n, high)) resolve em uma linha.",
        "starter": "def clamp(n, low, high):\n    ...",
        "func": "clamp",
        "tests": (
            "assert clamp(5, 0, 10) == 5\n"
            "assert clamp(-2, 0, 10) == 0\n"
            "assert clamp(15, 0, 10) == 10\n"
        ),
        "points": 20,
    },
    {
        "ord": 23,
        "chapter": "7. Funções",
        "title": "Argumento padrão",
        "concept": "parâmetro com valor default",
        "lesson": (
            "Default na assinatura: `def f(x, y=10):`. Se não passar y, vale 10.\n"
            "  f(1) usa y=10 ; f(1, 2) usa y=2"
        ),
        "context": "Um parâmetro pode ter valor padrão, usado quando você não passa nada.",
        "instructions": [
            "Crie a função `greet(name, greeting='Ola')`.",
            "Retorne '<greeting>, <name>!'.",
        ],
        "example": "greet('Ana')  ->  'Ola, Ana!'",
        "qa_note": "Fixtures têm valores default que o teste sobrescreve.",
        "hint": "Defina o default na assinatura: def greet(name, greeting='Ola').",
        "starter": "def greet(name, greeting='Ola'):\n    ...",
        "func": "greet",
        "tests": (
            "assert greet('Ana') == 'Ola, Ana!'\n"
            "assert greet('Ana', 'Oi') == 'Oi, Ana!'\n"
        ),
        "points": 20,
    },
    {
        "ord": 24,
        "chapter": "7. Funções",
        "title": "Média com *args",
        "concept": "*args, nº variável de argumentos",
        "lesson": (
            "`*args` junta todos os argumentos numa tupla:\n"
            "  def f(*xs): ...   f(1,2,3) -> xs = (1, 2, 3)"
        ),
        "context": "Com *args a função aceita quantos argumentos você quiser.",
        "instructions": [
            "Crie a função `average(*nums)`.",
            "Retorne a média (float) dos números recebidos.",
        ],
        "example": "average(1, 2, 3)  ->  2.0",
        "qa_note": "Parametrização: rodar a mesma lógica com N entradas diferentes.",
        "hint": "sum(nums) / len(nums) — nums chega como tupla.",
        "starter": "def average(*nums):\n    ...",
        "func": "average",
        "tests": (
            "assert average(2, 4) == 3.0\n"
            "assert average(1, 2, 3) == 2.0\n"
            "assert average(10) == 10.0\n"
        ),
        "points": 25,
    },

    # ===================== Cap 8 — Exceções =====================
    {
        "ord": 25,
        "chapter": "8. Exceções",
        "title": "Raiz quadrada segura (raise)",
        "concept": "raise, ValueError",
        "lesson": (
            "`raise ValueError('msg')` interrompe e sinaliza entrada inválida.\n"
            "Raiz quadrada: `n ** 0.5`."
        ),
        "context": "Quando a entrada é inválida, o certo é avisar com erro, não retornar valor errado.",
        "instructions": [
            "Crie a função `safe_sqrt(n)`.",
            "Retorne a raiz quadrada de n.",
            "Se n for negativo, lance ValueError.",
        ],
        "example": "safe_sqrt(9) -> 3.0 ; safe_sqrt(-1) -> ValueError",
        "qa_note": "raise + pytest.raises é como QA testa entradas inválidas.",
        "hint": "if n < 0: raise ValueError(...). A raiz é n ** 0.5.",
        "starter": "def safe_sqrt(n):\n    ...",
        "func": "safe_sqrt",
        "tests": (
            "assert safe_sqrt(9) == 3.0\n"
            "assert safe_sqrt(0) == 0.0\n"
            "try:\n"
            "    safe_sqrt(-1)\n"
            "    assert False, 'deveria ter lancado ValueError'\n"
            "except ValueError:\n"
            "    pass\n"
        ),
        "points": 25,
    },
    {
        "ord": 26,
        "chapter": "8. Exceções",
        "title": "Divisão segura (try/except)",
        "concept": "try / except",
        "lesson": (
            "Estrutura:\n"
            "  try:\n      arriscado()\n  except ZeroDivisionError:\n      # plano B\n"
            "Dividir por 0 lança ZeroDivisionError."
        ),
        "context": "Tentar uma operação e tratar a falha sem quebrar o programa.",
        "instructions": [
            "Crie a função `safe_div(a, b)`.",
            "Retorne a / b.",
            "Se b for zero, capture o erro com try/except e retorne None.",
        ],
        "example": "safe_div(6, 2) -> 3.0 ; safe_div(1, 0) -> None",
        "qa_note": "Tratar falha esperada sem derrubar a suíte de testes.",
        "hint": "Envolva o return a/b num try; no except, return None.",
        "starter": "def safe_div(a, b):\n    ...",
        "func": "safe_div",
        "tests": (
            "assert safe_div(6, 2) == 3.0\n"
            "assert safe_div(1, 0) is None\n"
            "assert safe_div(9, 3) == 3.0\n"
        ),
        "points": 25,
    },
    {
        "ord": 27,
        "chapter": "8. Exceções",
        "title": "Validar positivo",
        "concept": "raise ValueError, validação",
        "lesson": (
            "Junta dois passos: `int(s)` converte; depois cheque a regra e dê raise "
            "se quebrar."
        ),
        "context": "Converte texto em número e recusa valores que não fazem sentido.",
        "instructions": [
            "Crie a função `parse_positive(s)`.",
            "Converta `s` para int e retorne.",
            "Se o número for <= 0, lance ValueError.",
        ],
        "example": "parse_positive('7') -> 7 ; parse_positive('-3') -> ValueError",
        "qa_note": "Testar entrada inválida é exatamente o que pytest.raises cobre.",
        "hint": "n = int(s); if n <= 0: raise ValueError; return n.",
        "starter": "def parse_positive(s):\n    ...",
        "func": "parse_positive",
        "tests": (
            "assert parse_positive('7') == 7\n"
            "try:\n"
            "    parse_positive('-3')\n"
            "    assert False\n"
            "except ValueError:\n"
            "    pass\n"
        ),
        "points": 30,
    },

    # ===================== Cap 9 — JSON (API testing) =====================
    {
        "ord": 28,
        "chapter": "9. JSON (API testing)",
        "title": "Ler um campo do JSON",
        "concept": "import json, json.loads",
        "lesson": (
            "`import json` carrega o módulo.\n"
            "`json.loads('{\"a\": 1}')` -> {'a': 1} (dict). Acesse com ['a']."
        ),
        "context": "json.loads transforma o texto da API num dicionário Python.",
        "instructions": [
            "Importe o módulo `json`.",
            "Crie a função `get_field(json_str, key)`.",
            "Faça o parse e retorne o valor da chave `key`.",
        ],
        "example": "get_field('{\"name\":\"Ana\"}', 'name')  ->  'Ana'",
        "qa_note": "Extrair um campo da resposta é o pão com manteiga do QA de API.",
        "hint": "json.loads(json_str) vira dict; depois acesse [key].",
        "starter": "import json\n\ndef get_field(json_str, key):\n    ...",
        "func": "get_field",
        "tests": (
            "assert get_field('{\"name\":\"Ana\"}', 'name') == 'Ana'\n"
            "assert get_field('{\"age\":30}', 'age') == 30\n"
        ),
        "points": 25,
    },
    {
        "ord": 29,
        "chapter": "9. JSON (API testing)",
        "title": "Gerar JSON ordenado",
        "concept": "json.dumps, sort_keys",
        "lesson": (
            "`json.dumps(d)` -> texto JSON.\n"
            "`json.dumps(d, sort_keys=True)` ordena as chaves (saída previsível)."
        ),
        "context": "O caminho inverso: transformar um dict em texto JSON.",
        "instructions": [
            "Importe o módulo `json`.",
            "Crie a função `to_json(d)`.",
            "Retorne o dict como string JSON com as chaves ordenadas.",
        ],
        "example": "to_json({'b':1, 'a':2})  ->  '{\"a\": 2, \"b\": 1}'",
        "qa_note": "Montar payloads previsíveis pra comparar respostas de API.",
        "hint": "json.dumps(d, sort_keys=True).",
        "starter": "import json\n\ndef to_json(d):\n    ...",
        "func": "to_json",
        "tests": (
            "assert to_json({'b':1, 'a':2}) == '{\"a\": 2, \"b\": 1}'\n"
            "assert to_json({}) == '{}'\n"
        ),
        "points": 25,
    },

    # ============== Cap 10 — OOP (base do Page Object Model) ==============
    {
        "ord": 30,
        "chapter": "10. OOP (base do Page Object Model)",
        "title": "Classe Counter",
        "concept": "class, __init__, método, atributo",
        "lesson": (
            "`__init__(self)` roda quando o objeto nasce — bom pra criar atributos.\n"
            "  class C:\n      def __init__(self): self.x = 0\n"
            "Atributo: self.x. Acesso: obj.x."
        ),
        "context": "Uma classe cria objetos com estado (atributos) e comportamento (métodos).",
        "instructions": [
            "Crie a classe `Counter` com atributo `value` começando em 0.",
            "Adicione o método `increment()` que soma 1 ao value.",
        ],
        "example": "c = Counter(); c.increment(); c.value  ->  1",
        "qa_note": "Objetos com estado são a base do Page Object Model no Playwright.",
        "hint": "No __init__ faça self.value = 0; em increment faça self.value += 1.",
        "starter": "class Counter:\n    def __init__(self):\n        ...\n    def increment(self):\n        ...",
        "func": "Counter",
        "tests": (
            "c = Counter()\n"
            "assert c.value == 0\n"
            "c.increment()\n"
            "c.increment()\n"
            "assert c.value == 2\n"
        ),
        "points": 30,
    },
    {
        "ord": 31,
        "chapter": "10. OOP (base do Page Object Model)",
        "title": "Classe Stack",
        "concept": "class com lista interna",
        "lesson": (
            "Guarde dados num atributo lista: self.items = [].\n"
            "`self.items.pop()` remove e devolve o último; `len(self.items) == 0` "
            "diz se está vazia."
        ),
        "context": "Uma pilha (stack) devolve sempre o último que entrou (LIFO).",
        "instructions": [
            "Crie a classe `Stack` com uma lista interna.",
            "Adicione `push(x)`, `pop()` (remove e retorna o topo) e `is_empty()`.",
        ],
        "example": "s = Stack(); s.push(1); s.pop()  ->  1",
        "qa_note": "Encapsular comportamento numa classe testável (push/pop/is_empty).",
        "hint": "Itens em self.items = []; pop() pode usar self.items.pop().",
        "starter": "class Stack:\n    def __init__(self):\n        self.items = []\n    def push(self, x):\n        ...\n    def pop(self):\n        ...\n    def is_empty(self):\n        ...",
        "func": "Stack",
        "tests": (
            "s = Stack()\n"
            "assert s.is_empty() == True\n"
            "s.push(1)\n"
            "s.push(2)\n"
            "assert s.pop() == 2\n"
            "assert s.is_empty() == False\n"
        ),
        "points": 35,
    },
    {
        "ord": 32,
        "chapter": "10. OOP (base do Page Object Model)",
        "title": "Classe BankAccount",
        "concept": "class + estado + raise",
        "lesson": (
            "Junta tudo: atributo (balance), métodos (deposit/withdraw) e raise.\n"
            "Em withdraw, cheque a regra ANTES de mexer no saldo."
        ),
        "context": "O exercício final junta estado, métodos e erro esperado.",
        "instructions": [
            "Crie a classe `BankAccount` com `balance` começando em 0.",
            "Adicione `deposit(x)` e `withdraw(x)`.",
            "Em withdraw, se x > balance, lance ValueError.",
        ],
        "example": "a = BankAccount(); a.deposit(100); a.withdraw(30); a.balance -> 70",
        "qa_note": "Junta estado, métodos e o caso negativo (saldo insuficiente).",
        "hint": "Em withdraw: if x > self.balance: raise ValueError; senão subtraia.",
        "starter": "class BankAccount:\n    def __init__(self):\n        self.balance = 0\n    def deposit(self, x):\n        ...\n    def withdraw(self, x):\n        ...",
        "func": "BankAccount",
        "tests": (
            "a = BankAccount()\n"
            "a.deposit(100)\n"
            "a.withdraw(30)\n"
            "assert a.balance == 70\n"
            "try:\n"
            "    a.withdraw(1000)\n"
            "    assert False\n"
            "except ValueError:\n"
            "    pass\n"
        ),
        "points": 40,
    },
]

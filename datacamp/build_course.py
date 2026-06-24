# -*- coding: utf-8 -*-
"""
Extrator: futurecoder (MIT) -> course_data.py em PT-BR.

Lê os capítulos em .futurecoder-src/core/chapters/c*.py (estrutura via AST, sem
importar) e casa cada página/passo com a tradução PT-BR oficial do arquivo
gettext compilado (.mo). O código (`program`) vem do próprio .py.

Saída: course_data.py com COURSE = [ {chapter, pages:[ {title, steps:[...]} ]} ].

Conteúdo derivado do futurecoder (https://github.com/alexmojaki/futurecoder),
licença MIT. Atribuição mantida em course_data.py e no dashboard.

Rodar:  python3 build_course.py
"""

import ast
import gettext
import re
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE / ".futurecoder-src"
CHAPTERS_DIR = SRC / "core" / "chapters"
MO = SRC / "translations" / "locales" / "br" / "LC_MESSAGES" / "futurecoder.mo"
OUT = HERE / "course_data.py"

# Catálogo PT-BR (msgid estruturado -> tradução).
CAT = gettext.GNUTranslations(open(MO, "rb"))._catalog
EOT = "\x04"


def pt(key):
    """Busca a tradução PT-BR pela chave estruturada (ex: pages.X.title)."""
    for k, v in CAT.items():
        if not isinstance(k, str):
            continue
        msgid = k.split(EOT, 1)[1] if EOT in k else k
        if msgid == key:
            return v
    return None


def const_str(node):
    """Pega o valor de um ast string constant, com dedent/strip."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def get_assign(classdef, name):
    """Valor string de um atributo `name = "..."` dentro da classe."""
    for n in classdef.body:
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name) and t.id == name:
                    return const_str(n.value)
    return None


def fill_markers(text, program):
    """Substitui marcadores do futurecoder pelo código real."""
    if not text:
        return text
    if program:
        text = text.replace("__program__", program)
        text = text.replace("__copyable__", program)
        text = re.sub(r"__code\d+__", program, text)
    # remove marcadores remanescentes sem código
    text = re.sub(r"__program__|__copyable__|__code\d+__|__no_auto_translate__", "", text)
    return text.strip()


def extract_chapter(path):
    """Extrai um capítulo: páginas em ordem, cada uma com passos PT-BR + código."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    module = path.stem  # ex: c01_the_shell
    short = re.sub(r"^c\d+_", "", module)  # the_shell
    chapter_title = pt(f"chapters.{short}.title") or short.replace("_", " ").title()
    pages = []

    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        page = node.name
        page_title = pt(f"pages.{page}.title") or page
        steps = []

        # passos = classes aninhadas (na ordem do código)
        for sub in node.body:
            if isinstance(sub, ast.ClassDef):
                step = sub.name
                text = pt(f"pages.{page}.steps.{step}.text")
                program = get_assign(sub, "program")
                if text:
                    steps.append({"text": fill_markers(text, program),
                                  "code": program or ""})

        # final_text da página
        final = pt(f"pages.{page}.steps.final_text.text")
        if final:
            steps.append({"text": fill_markers(final, None), "code": ""})

        if steps:
            pages.append({"title": page_title, "slug": page, "steps": steps})

    return {"chapter": chapter_title, "module": module, "pages": pages}


def main():
    chapters = []
    for path in sorted(CHAPTERS_DIR.glob("c*.py")):
        ch = extract_chapter(path)
        if ch["pages"]:
            chapters.append(ch)

    # Estatísticas de cobertura
    n_pages = sum(len(c["pages"]) for c in chapters)
    n_steps = sum(len(p["steps"]) for c in chapters for p in c["pages"])
    pt_steps = sum(1 for c in chapters for p in c["pages"] for s in p["steps"]
                   if re.search(r"[ãáàâéêíóôõç]| que | você ", s["text"], re.I))

    header = (
        "# -*- coding: utf-8 -*-\n"
        '"""\n'
        "Curso PT-BR gerado por build_course.py a partir do futurecoder.\n"
        "Fonte: https://github.com/alexmojaki/futurecoder (licença MIT).\n"
        "Tradução PT-BR oficial do projeto. NÃO editar à mão (regerar via build_course.py).\n"
        '"""\n\n'
        "ATTRIBUTION = 'Conteúdo do curso: futurecoder (github.com/alexmojaki/futurecoder), MIT.'\n\n"
        "COURSE = "
    )
    OUT.write_text(header + repr(chapters) + "\n", encoding="utf-8")

    print(f"capítulos: {len(chapters)} | páginas: {n_pages} | passos: {n_steps}")
    print(f"passos com PT-BR detectado: {pt_steps}/{n_steps}")
    print(f"-> {OUT.name} gerado.")
    for c in chapters:
        print(f"  {c['chapter']}: {len(c['pages'])} páginas")


if __name__ == "__main__":
    main()

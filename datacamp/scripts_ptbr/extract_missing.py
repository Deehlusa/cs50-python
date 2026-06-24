# -*- coding: utf-8 -*-
"""Lista os termos de UI (terms.json) que ainda estao em ingles.
Heuristica: sem acento/sem palavra PT comum => provavelmente ingles."""
import json, re
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / ".futurecoder-src" / "frontend" / "src"
PT = re.compile(r"[ãáàâéêíóôõúç]|\b(você|código|página|próximo|anterior|aula|"
                r"exercício|dica|sumário|conteúdo|requisitos|solução|configurações|"
                r"avaliação|entrar|sair|enviar|resposta|capítulo)\b", re.I)

terms = json.loads((SRC / "terms.json").read_text(encoding="utf-8"))
missing = {k: v for k, v in terms.items()
           if isinstance(v, str) and v.strip() and not PT.search(v)
           and re.search(r"[A-Za-z]", v) and len(v) < 400}

out = SRC.parent.parent / "translations" / "pt_overrides" / "terms_to_translate.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(missing, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(missing)} termos para traduzir -> {out}")
for k in list(missing)[:8]:
    print(f"  {k}: {missing[k][:60]!r}")

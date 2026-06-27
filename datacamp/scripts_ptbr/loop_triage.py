# -*- coding: utf-8 -*-
"""Loop triage — heartbeat do Loop Engineering.

Lê o ESTADO do projeto (PROGRESS.md + LOOP-CONTRACT.md + backlog do athena.orchestrator) e
imprime: onde paramos, qual o próximo item, e um prompt de /loop pronto pra colar. Assim o
próximo loop COMEÇA lendo o estado, não do zero. Stdlib apenas; não precisa do server no ar.

Uso:  python3 datacamp/scripts_ptbr/loop_triage.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # datacamp/
sys.path.insert(0, str(ROOT))
PROGRESS = ROOT / "PROGRESS.md"
CONTRACT = ROOT / "docs" / "LOOP-CONTRACT.md"


def _section(text, header):
    """Extrai as linhas sob um header markdown até o próximo header."""
    out, capture = [], False
    for ln in text.splitlines():
        if ln.strip().startswith("#") or (ln.strip().startswith(">") and capture and not ln.strip()):
            pass
        if header.lower() in ln.lower() and ln.lstrip().startswith("#"):
            capture = True
            continue
        if capture and ln.lstrip().startswith("#"):
            break
        if capture:
            out.append(ln)
    return "\n".join(out).strip()


def main():
    print("=" * 64)
    print("LOOP TRIAGE — FutureCoder + Athena")
    print("=" * 64)

    # 1) Backlog do orchestrator (fonte de verdade do código)
    try:
        from athena import orchestrator as orch
        prog = orch.progress()
        nxt = orch.next_todo()
        print(f"\n[orchestrator] backlog: {prog['done']}/{prog['total']} done")
        if nxt:
            print(f"[orchestrator] próximo TODO: {nxt['id']} — {nxt['desc']}")
        else:
            print("[orchestrator] todos os itens do MVP backlog estão done.")
    except Exception as e:  # noqa
        print(f"[orchestrator] indisponível: {e}")

    # 2) Próximo alvo declarado no PROGRESS.md
    nxt_target = ""
    if PROGRESS.exists():
        txt = PROGRESS.read_text(encoding="utf-8")
        sec = _section(txt, "Próximo alvo")
        nxt_target = sec.strip()
        print("\n[PROGRESS.md] Próximo alvo:")
        print("  " + (nxt_target.replace("\n", "\n  ") if nxt_target else "(não declarado)"))
    else:
        print("\n[PROGRESS.md] ausente — crie-o (memória do loop).")

    # 3) Itens abertos do backlog (checkbox não marcado) no PROGRESS + CONTRACT
    open_items = []
    for f in (PROGRESS, CONTRACT):
        if f.exists():
            for ln in f.read_text(encoding="utf-8").splitlines():
                if re.match(r"\s*-\s*\[ \]\s+", ln):
                    open_items.append(ln.strip())
    if open_items:
        print("\n[backlog aberto]")
        for it in open_items[:8]:
            print("  " + it)

    # 4) Prompt de /loop sugerido pro próximo item
    alvo_curto = (nxt_target.splitlines()[0] if nxt_target else
                  (open_items[0] if open_items else "definir próximo item"))
    alvo_curto = re.sub(r"^\s*[-*]\s*(\[.\]\s*)?", "", alvo_curto).strip()
    print("\n[prompt sugerido p/ o próximo loop]")
    print("-" * 64)
    print(f"""/loop 12m

Continua o loop a partir do estado (lê PROGRESS.md + LOOP-CONTRACT.md + skill athena).

TAREFA: {alvo_curto}

Regras: discovery antes de editar; reviewer != maker; verificação com evidência;
cognição pesada via agy (0-quota); UI só em futurecoder-patches; nada commitado sem o dono.
DoD: código + testes verdes + evidência concreta + docs coerentes.""")
    print("-" * 64)


if __name__ == "__main__":
    main()

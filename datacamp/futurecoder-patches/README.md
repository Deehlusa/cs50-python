# futurecoder-patches

Estes são os **nossos** patches hand-authored sobre o futurecoder (github.com/alexmojaki/futurecoder, MIT).
O clone fica em `datacamp/.futurecoder-src/` e é **gitignored** (é grande e é upstream).
Esta pasta é a **fonte de verdade versionada** dos arquivos que editamos — assim eles
sobrevivem a um re-clone.

## Regra de ouro

**Edite os arquivos AQUI, não dentro de `.futurecoder-src/`.** O `build_ptbr.sh` copia
estes arquivos para dentro do clone antes de buildar. Se você editar direto no clone, a
próxima build sobrescreve sua mudança com a versão daqui.

## O que cada arquivo faz

| Arquivo | Patch |
|---------|-------|
| `frontend/src/css/dark.scss` | Tema escuro (override de Bootstrap + github-markdown); estilos do menu, TOC, barra de progresso e botão "Salvar no projeto" |
| `frontend/src/App.js` | Navbar com quick-menu + barra de progresso, botões Avançar/Retornar, `SaveCodeButton` |
| `frontend/src/store.js` | Espelha o progresso no SQLite do `server.py` (além do localforage) |
| `frontend/src/book/serverSync.js` | Cliente do progresso (`/api/course-progress`) + salvar código (`/api/save-code`) + cálculo de % |
| `frontend/src/shell/defs/styles/Terminal.js` | Cor do shell alinhada ao tema escuro |
| `frontend/src/chapters.json` | TOC do quick-menu (importado pelo App.js) |
| `core/translation.py` | `get()` com fallback pro inglês onde a tradução `br` está incompleta |
| `translations/pt_overrides/terms_br.json` | Rótulos de UI traduzidos pra PT-BR (mesclados por `scripts_ptbr/merge_overrides.py`) |

## Reaplicar após re-clonar o futurecoder

1. Clonar o futurecoder em `datacamp/.futurecoder-src/` e preparar o venv (Python 3.12).
2. Rodar `datacamp/build_ptbr.sh` — ele copia estes patches pro clone, mescla os overrides
   PT-BR e builda (sem firebase, sem precache).
3. `python3 datacamp/server.py` → http://localhost:8000/course/

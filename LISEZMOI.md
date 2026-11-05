# sprezzature-ui

[English](https://github.com/warith-harchaoui/sprezzature-ui/blob/main/README.md)

La moitié déterministe d'un skill d'interface : trouver les chaînes qui
devraient être dans un catalogue de traduction, et échafauder le catalogue où
elles ont leur place.

L'autre moitié, c'est écrire l'interface : du HTML sémantique, des
utilitaires Tailwind et des modules ES simples, sans runtime de framework,
avec les pairs de mode sombre, les anneaux de focus et les gardes de
mouvement réduit. Cette moitié est le travail du modèle, guidé par le
[`SKILL.md`](https://github.com/warith-harchaoui/sprezzature/blob/main/sprezzature-ui/SKILL.md)
livré avec la suite et par la prose de `references/`. Aucune route HTTP ne
peut porter « rends ce tableau de bord lisible », et ce paquet ne prétend pas
le contraire.

---

## Comment ça marche

![Schéma de flux. En haut, votre arborescence de sources alimente deux voies. La voie de gauche contrôle : elle parcourt l'arborescence, trouve les tables de traduction noyées dans le JavaScript et le HTML et les constantes de prompt incrustées dans le Python, et rend ses constats avec le code de sortie 1. La voie de droite fabrique : elle amorce un fichier de langues unique, le compile en JSON et produit les deux chargeurs qui le lisent, l'un pour le navigateur, l'autre pour Python. Les deux se rejoignent en un seul résultat, une interface qui accepte une deuxième langue le jour où on la demande.](https://raw.githubusercontent.com/warith-harchaoui/sprezzature-ui/main/assets/comment-ca-marche.svg)

## Ce qu'il y a dedans

| Commande | Ce qu'elle fait |
|---|---|
| `sprezzature-ui-i18n-audit` | **audit.** Trouve les tables de traduction noyées dans du JavaScript ou du HTML (règle `I18N001`) et les prompts de LLM (grand modèle de langage) incrustés dans du Python (règle `I18N002`). Les deux ont leur place dans `locales/i18n.yaml`. Avec `--fix`, déplace dans ce catalogue ce qu'il sait lire. L'audit lui-même n'importe que la bibliothèque standard. |
| `sprezzature-ui-i18n-make` | **fabrique.** Échafaude `locales/i18n.yaml`, le compile en `locales/i18n.json`, et émet deux chargeurs : `locales/i18n.js` pour le navigateur et `locales/i18n_prompts.py` pour Python. |

Une seule porte d'entrée sur les deux, écrite en click, sous deux noms :
`make-ui <outil>` et `sprezzature-ui <outil>` sont le même appelable, donc
ils ne peuvent pas diverger. `sprezzature-ui tools` liste les outils et dit
si chacun peut tourner sur cette machine. La porte d'entrée argparse a été
retirée le 2026-10-25, et depuis le 2026-11-04 plus aucune commande ne lit
ses options avec argparse : les commandes par outil et `sprezzature-ui-mcp`
sont en click elles aussi, et `-V` affiche la version du paquet. Chaque outil garde sa propre commande, et c'est elle
qu'un script ou un crochet de pré-commit doit appeler.

## Cinq surfaces

| Surface | Point d'entrée | Ce qu'elle expose |
|---|---|---|
| Bibliothèque | `from sprezzature_ui import …` | `audit_js`, `audit_py`, `audit_path`, `gather`, `scaffold`, `compile_json`, `emit_loader`, `emit_python` |
| CLI (interface en ligne de commande) | `sprezzature-ui`, `make-ui`, `sprezzature-ui-i18n-audit`, `sprezzature-ui-i18n-make` | les deux outils |
| HTTP | `uvicorn sprezzature_ui.api:app`, ou le `Dockerfile` et le `docker-compose.yml` (qui servent aussi `/mcp`) | `GET /health`, `POST /v1/i18n-audit` |
| MCP (Model Context Protocol) | `sprezzature-ui-mcp` | les outils `health` et `audit_i18n`, sur `/mcp` |
| Skill | [`SKILL.md`](https://github.com/warith-harchaoui/sprezzature/blob/main/sprezzature-ui/SKILL.md) dans la suite | la prose de design, plus les deux commandes |

Seul l'audit franchit une frontière réseau. L'outil de fabrication écrit des
fichiers dans un projet : il n'a donc ni route ni outil MCP.

## Pourquoi ça compte plus tôt qu'on ne croit

Une phrase écrite en dur dans un gabarit ne coûte rien le jour où on l'écrit.
Elle coûte une semaine le jour où quelqu'un a besoin d'une deuxième langue et
découvre que les chaînes sont éparpillées dans les sources : dans des
littéraux JavaScript, dans des scripts en ligne, dans des gabarits de prompt
enfouis dans du Python. L'audit est assez bon marché pour tenir dans un
crochet de pré-commit, et c'est là qu'il les attrape une par une plutôt que
toutes d'un coup.

## Installation

```sh
pip install sprezzature-ui
```

Une ligne installe toutes les surfaces : l'audit, les outils de catalogue
(PyYAML), la porte d'entrée click, l'application HTTP et le serveur MCP. Il
n'y a pas d'extra de fonctionnalité. `[dev]` ne contient que l'outillage de
test.

## Utilisation

```sh
sprezzature-ui-i18n-audit src/                 # sort 1 au moindre constat
sprezzature-ui-i18n-audit src/ --json          # constats en tableau JSON
sprezzature-ui-i18n-audit src/ --fix           # déplace les chaînes dans locales/i18n.yaml
sprezzature-ui-i18n-make                       # échafaude, compile, émet les deux chargeurs
sprezzature-ui-i18n-make --dir ../mon-projet --compile
```

`sprezzature-ui-i18n-audit` prend des fichiers et des dossiers. Les dossiers
sont parcourus récursivement, en sautant `node_modules`, `.git`,
`__pycache__`, `dist`, `build`, `vendor` et `.venv`. `--catalog CHEMIN`
change le catalogue où `--fix` écrit.

`--fix` écrit le catalogue et imprime, pour chaque chaîne déplacée, l'appel à
coller à sa place. Il ne réécrit pas le site d'appel, et il sort toujours 1 :
les chaînes restent dans le code tant que l'auteur ne les a pas remplacées.

`sprezzature-ui-i18n-make` enchaîne quatre étapes par défaut. `--init`,
`--compile`, `--emit-loader` et `--emit-python` n'en lancent chacun qu'une.
`--dir` désigne la racine du projet ; le catalogue est toujours
`<dir>/locales/i18n.yaml`. L'étape de compilation refuse un prompt qui ne
déclare aucune langue `validated:`, ou qui n'a pas de texte dans celle-ci.

### En crochet de pré-commit

```yaml
repos:
  - repo: https://github.com/warith-harchaoui/sprezzature-ui
    rev: v1.2.0
    hooks:
      - id: sprezzature-ui-i18n-audit
```

Le crochet s'applique aux fichiers que l'audit lit : `.js`, `.mjs`, `.cjs`,
`.jsx`, `.ts`, `.tsx`, `.html`, `.htm` et `.py`.

### Depuis Python

```python
from sprezzature_ui import audit_path, gather

for fichier in gather(["src/"]):
    for constat in audit_path(fichier):
        print(constat["rule"], constat["path"], constat["line"])
```

`gather` parcourt l'arborescence et écarte ce qui ne s'audite pas ;
`audit_path` lit un seul `pathlib.Path`. Les deux sont séparés parce qu'un
crochet de pré-commit sait déjà quels fichiers ont changé et n'a pas à payer
un parcours. Chaque constat est un dict avec `rule`, `severity`, `path`,
`line`, `message` et `snippet`.

### Par HTTP

```sh
uvicorn sprezzature_ui.api:app --port 8000
curl -s localhost:8000/health
curl -s localhost:8000/v1/i18n-audit -H 'Content-Type: application/json' \
  -d '{"source": "const i18n = { en: \"Save\", fr: \"Enregistrer\" };", "filename": "app.js"}'
```

`POST /v1/i18n-audit` prend `source` (le texte du fichier) et `filename`
(par défaut `app.js`, dont l'extension décide quelle règle s'applique). La
route rend `findings_total` et `findings`, avec votre nom de fichier dans
chaque `path`. `GET /health` rend l'état et la version. `/` redirige vers
`/docs`.

### Par MCP

```sh
sprezzature-ui-mcp                       # 127.0.0.1:8000
sprezzature-ui-mcp --host 0.0.0.0 --port 9000
```

Il sert la même application FastAPI, avec le point d'accès MCP monté sur
`/mcp`. Les noms des outils sont les `operation_id` des routes : `health` et
`audit_i18n`. `SPREZZATURE_UI_HOST` et `SPREZZATURE_UI_PORT` fixent les
valeurs par défaut.

### En conteneur

```sh
docker compose up -d
curl -s localhost:8000/health
docker compose run --rm api make-ui i18n-audit /work/src
```

L'image sert les routes HTTP et le point d'accès MCP sur le port 8000, depuis
un seul processus : sa commande par défaut est
`sprezzature-ui-mcp --host 0.0.0.0`, si bien que `/v1/...` et `/mcp` répondent
tous deux. Compose monte `./work` sur `/work` : les sources à auditer et le
catalogue écrit à côté restent sur l'hôte.

## Ce que l'audit voit

| Règle | Fichiers | Ce qui déclenche |
|---|---|---|
| `I18N001` | `.js`, `.mjs`, `.cjs`, `.jsx`, `.ts`, `.tsx`, `.html`, `.htm` | une ligne qui déclare une table sous un nom révélateur (`const i18n = {`, `translations`, `messages`, `locales`, `strings`, `dictionary`, `lang`, …), ou un littéral objet avec au moins deux clés de langue (`{ en: …, fr: … }`) |
| `I18N002` | `.py` | une constante de module ou de classe dont le nom contient `PROMPT` ou `INSTRUCTION`, affectée d'un littéral de chaîne ou d'une f-string |

Il lit le JavaScript et le HTML ligne par ligne, et le Python par son AST
(arbre syntaxique abstrait). Il ne sait pas dire si une traduction est bonne,
ni si une chaîne est seulement visible de l'utilisateur. « 0 findings » veut
dire qu'aucune des deux formes n'a été trouvée, pas que l'interface est prête
à livrer.

## La moitié design

`references/` contient la prose que lit le skill : la pile Tailwind et
JavaScript simple, la liste de contrôle, les anti-motifs, les tableaux de
bord, les graphiques en SVG (Scalable Vector Graphics), la psychologie des
couleurs, une table de correspondance Material Design, et des consignes par
plateforme sous `references/ui-guidelines/`. `assets/` contient une page de
départ, sept composants HTML, deux graphiques SVG, huit extraits indexés par
loi de l'UX dans `assets/snippets/INDEX.md`, et les trois familles Roboto
sous `assets/fonts/`.

La typographie par défaut est la règle des trois Roboto : Roboto pour
l'interface et le corps de texte, Roboto Serif pour les textes longs, Roboto
Mono pour le code. Les trois sont auto-hébergées. Ces fichiers vivent dans ce
dépôt et dans le dossier du skill ; la roue Python ne les embarque pas.

## La frontière, dite franchement

Ce paquet est **petit**, et il le restera. Son métier est le jugement
esthétique écrit en prose (la règle des trois Roboto, les jetons de design,
ce qu'une interface doit respecter) plus la part de ce jugement qui est
mécanisable. L'audit i18n est cette part. Ajouter des routes pour faire
nombre, ce serait prendre la largeur pour de la valeur.

## Voir aussi

- **[sprezzature-accessibility](https://github.com/warith-harchaoui/sprezzature-accessibility)** : contrôler le HTML que vous produisez, et rédiger le texte alternatif qu'il signale comme manquant.
- **[sprezzature-colors](https://github.com/warith-harchaoui/sprezzature-colors)** : contraste et vision des couleurs sur la palette.
- **[sprezzature-ux-laws](https://github.com/warith-harchaoui/sprezzature-ux-laws)** : auditer le ressenti de l'interface, par les heuristiques nommées.
- **[sprezzature-cli-gui](https://github.com/warith-harchaoui/sprezzature-cli-gui)** : quand il y a une ligne de commande derrière l'écran.
- **[sprezzature](https://github.com/warith-harchaoui/sprezzature)** : la suite, et les skills qui la pilotent depuis Claude.

## Licence

BSD-3-Clause. Voir `LICENSE`.

## Auteur

[Warith HARCHAOUI, Ph.D.](https://www.linkedin.com/in/warith-harchaoui/)

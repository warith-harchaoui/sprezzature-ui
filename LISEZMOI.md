# sprezzature-ui

[🇫🇷](https://github.com/warith-harchaoui/sprezzature-ui/blob/main/LISEZMOI.md) · [🇬🇧](https://github.com/warith-harchaoui/sprezzature-ui/blob/main/README.md)

La moitié déterministe d'un skill d'interface : trouver les chaînes qui
devraient être dans un catalogue de traduction, et échafauder le catalogue où
elles ont leur place.

L'autre moitié — écrire l'interface, en HTML sémantique avec des utilitaires
Tailwind et des modules ES simples, sans runtime de framework, avec les pairs
de mode sombre, les anneaux de focus et les gardes de mouvement réduit — est
le travail du modèle, guidé par le
[`SKILL.md`](https://github.com/warith-harchaoui/sprezzature) livré avec la
suite. Aucune route HTTP ne peut porter « rends ce tableau de bord lisible »,
et ce paquet ne prétend pas le contraire.

---

## Comment ça marche

![Schéma de flux. En haut, votre arborescence de sources alimente deux voies. La voie de gauche contrôle : elle parcourt l'arborescence, trouve les phrases écrites en dur dans le JavaScript, dans les attributs HTML et dans les gabarits de prompts Python, et rend ses constats avec le code de sortie 1. La voie de droite fabrique : elle amorce un fichier de langues unique, le compile en JSON et produit le chargeur qui le lit. Les deux se rejoignent en un seul résultat, une interface qui accepte une deuxième langue le jour où on la demande.](https://raw.githubusercontent.com/warith-harchaoui/sprezzature-ui/main/assets/comment-ca-marche.svg)

## Ce qu'il y a dedans

| | |
|---|---|
| `sprezzature-ui-i18n-audit` | **audit** — les traductions noyées dans du JavaScript et du HTML, les prompts de modèle incrustés dans du Python. Les deux ont leur place dans `locales/i18n.yaml`. Bibliothèque standard seule. |
| `sprezzature-ui-i18n-make` | **fabrique** — échafauder ce catalogue, le compiler en JSON, émettre le chargeur qui le lit. |

Une seule porte d'entrée sur les deux, en click, sous deux noms :
`make-ui <outil>` et `sprezzature-ui <outil>` résolvent vers le même appelable,
donc ils ne peuvent pas diverger. Le jumeau argparse a été retiré le
2026-10-25 : deux analyseurs voulaient dire chaque sous-commande écrite deux
fois.

## Pourquoi ça compte plus tôt qu'on ne croit

Une phrase écrite en dur dans un gabarit ne coûte rien le jour où on l'écrit.
Elle coûte une semaine le jour où quelqu'un a besoin d'une deuxième langue et
découvre que les chaînes sont éparpillées dans les sources — dans des
littéraux JavaScript, dans des attributs HTML, dans des gabarits de prompt
enfouis dans du Python. L'audit est assez bon marché pour tenir dans un
crochet de pré-commit, et c'est là qu'il les attrape une par une plutôt que
toutes d'un coup.

## Installation

```sh
pip install sprezzature-ui              # l'audit
pip install "sprezzature-ui[i18n]"      # + les outils de catalogue (PyYAML)
pip install "sprezzature-ui[api,mcp]"   # + les surfaces HTTP et agent
```

## Utilisation

```sh
sprezzature-ui-i18n-audit src/            # sort 1 au moindre constat
sprezzature-ui-i18n-make locales/i18n.yaml
```

### En crochet de pré-commit

```yaml
repos:
  - repo: https://github.com/warith-harchaoui/sprezzature-ui
    rev: v1.0.0
    hooks:
      - id: sprezzature-ui-i18n-audit
```

### Depuis Python

```python
from sprezzature_ui import audit_path, gather

for fichier in gather(["src/"]):
    for constat in audit_path(fichier):
        print(constat["rule"], constat["path"], constat["line"])
```

`gather` parcourt l'arborescence et écarte ce qui ne s'audite pas ;
`audit_path` lit un fichier. Les deux sont séparés parce qu'un crochet de
pré-commit sait déjà quels fichiers ont changé et n'a pas à payer un
parcours.

### Par HTTP

```sh
pip install "sprezzature-ui[api]"
uvicorn sprezzature_ui.api:app --port 8000
```

Une seule route, `POST /v1/i18n-audit` : du source entre, des constats
sortent. L'étroitesse est le propos plutôt qu'un oubli, voir le premier
paragraphe.

## La frontière, dite franchement

Ce paquet est **petit**, et il le restera. Son métier est le jugement
esthétique écrit en prose — la règle des trois Roboto, les jetons de design,
ce qu'une interface doit respecter — plus la part de ce jugement qui est
mécanisable. L'audit i18n est cette part. La tentation sera d'ajouter des
routes pour faire nombre ; ce serait prendre la largeur pour de la valeur.

## Voir aussi

- [`sprezzature`](https://github.com/warith-harchaoui/sprezzature) — la suite
- [`sprezzature-accessibility`](https://github.com/warith-harchaoui/sprezzature-accessibility) — le HTML existe-t-il et est-il accessible
- [`sprezzature-colors`](https://github.com/warith-harchaoui/sprezzature-colors) — le contraste et les palettes
- [`sprezzature-cli-gui`](https://github.com/warith-harchaoui/sprezzature-cli-gui) — quand il y a une ligne de commande derrière l'écran

## Licence

BSD-3-Clause. Voir [LICENSE](LICENSE).

## Auteur

[Warith HARCHAOUI](https://warith-harchaoui.github.io/) —
warithmetics@deraison.ai

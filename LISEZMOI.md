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

## Ce qu'il y a dedans

| | |
|---|---|
| `sprezzature-ui-i18n-audit` | **audit** — les traductions noyées dans du JavaScript et du HTML, les prompts de modèle incrustés dans du Python. Les deux ont leur place dans `locales/i18n.yaml`. Bibliothèque standard seule. |
| `sprezzature-ui-i18n-make` | **fabrique** — échafauder ce catalogue, le compiler en JSON, émettre le chargeur qui le lit. |

Deux portes d'entrée sur les deux : `make-ui <outil>` (argparse) et
`sprezzature-ui <outil>` (click). Les deux lisent **une seule** table, donc un
outil ne peut pas apparaître dans l'une et manquer dans l'autre.

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
- repo: local
  hooks:
    - id: i18n-audit
      name: chaînes hors catalogue
      entry: sprezzature-ui-i18n-audit src/
      language: system
      pass_filenames: false
```

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

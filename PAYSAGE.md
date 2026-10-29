# Paysage

`sprezzature-ui` est la brique d'interface de la suite [sprezzature](https://sprezzature.ai/), dix paquets Python pour fabriquer du contenu web de qualité publication. Elle a deux étages, et une comparaison honnête doit nommer les deux. La moitié Python est déterministe : elle parcourt un arbre de sources, trouve les phrases codées en dur dans le JavaScript, dans les attributs HTML et dans les gabarits de prompt Python, et rend un verdict avec un code de sortie ; puis elle échafaude un fichier de locales unique, le compile en JSON et émet le chargeur qui le lit. L'autre moitié, écrire l'interface en HTML sémantique avec des utilitaires Tailwind et des modules ES simples, sans runtime de framework, avec des pairs en mode sombre, des anneaux de focus et un garde de mouvement réduit, est le travail du modèle, guidé par `SKILL.md` et les 64 fichiers de référence posés à côté. Aucune route HTTP ne transporte « rends ce tableau de bord lisible », et le paquet le dit dans son propre README.

La table ci-dessous tient donc deux familles à la fois : les chaînes d'outils d'internationalisation (i18n), et les façons de produire une interface. Ce n'est pas un arrangement de présentation. C'est l'endroit où ce paquet se tient réellement, et une comparaison contre une seule des deux le flatterait.

## Sa place dans l'écosystème

```
suite sprezzature
├── sprezzature-ui             ← ce paquet (la paire i18n, et la prose de conception)
├── sprezzature-accessibility  (contrôle statique du HTML, et le texte alternatif qui manque)
├── sprezzature-colors         (si une couleur passe, et celle qu'il faut sinon)
├── sprezzature-ux-laws        (si la page se comporte bien, selon les lois nommées)
├── sprezzature-cli-gui        (la même pile, quand une ligne de commande est derrière l'écran)
├── sprezzature-figures        (les graphiques dont une tuile de tableau de bord a besoin)
├── sprezzature-maps           (les mêmes nombres attachés à de vrais lieux)
├── sprezzature-publish        (du Markdown vers un site trouvable, narration comprise)
├── sprezzature-audio          (la parole vers le texte, le texte vers la parole)
└── sprezzature-video          (ce qu'un film sur un projet affirme, vérifié)
```

Ce qui vient avant : un écran que quelqu'un a demandé, et un arbre de sources qui contient déjà des chaînes. Ce qui vient après : trois contrôleurs voisins qui lisent le HTML produit ici. `sprezzature-accessibility` demande s'il est utilisable, `sprezzature-colors` si une couleur passe, `sprezzature-ux-laws` ce qu'il donne à l'usage. La brique sœur qui fait le travail voisin est `sprezzature-cli-gui` : mêmes règles de pile, mêmes jetons, mais elle part d'un analyseur d'arguments existant plutôt que d'un écran vide.

À l'intérieur du paquet, les deux étages se rejoignent dans un seul fichier. `locales/i18n.yaml` tient les libellés d'interface sous `gui:` et les prompts du modèle sous `prompts:`, parce qu'un écran et un prompt en désaccord sur une langue est un défaut que personne ne signale.

## Quand la choisir

- Vous allez ajouter une deuxième langue à un projet qui n'en a jamais prévu une, et la première question est de savoir combien en est enfoui dans le code. `sprezzature-ui-i18n-audit src/` y répond en une passe sur le JavaScript, le HTML et le Python, avec un chemin et une ligne par constat, et `--fix` déplace dans le catalogue ce qu'il sait lire et imprime l'appel à coller pour chaque chaîne déplacée.
- Votre Python assemble des prompts pour un modèle et votre JavaScript affiche des libellés, et les deux sont de la langue. Un seul catalogue sert les deux, et la moitié prompt porte une règle dont la moitié interface n'a pas besoin : chaque entrée `prompts:` déclare l'unique locale dans laquelle elle a été conçue et éprouvée, donc une traduction absente se résout vers ce texte plutôt que vers la première locale déclarée ou, pire, vers l'identifiant du message.
- Vous voulez un crochet de pre-commit plutôt qu'une migration. Le contrôle n'utilise que la bibliothèque standard, ce qui le rend assez bon marché pour tourner à chaque commit. Une phrase codée en dur ne coûte rien le jour où elle est écrite, et une semaine le jour où quelqu'un a besoin d'une deuxième langue.
- Vous écrivez une interface sans avoir choisi de framework, et vous voulez une sortie qu'un navigateur exécute directement : HTML sémantique, utilitaires Tailwind, modules ES simples, un pair `dark:` sur chaque élément stylé, un anneau de focus visible, et aucune translation ni mise à l'échelle sous `prefers-reduced-motion`. Cette moitié-là est de la prose lue par un modèle, pas une commande.

## Quand prendre autre chose

- **Vous voulez que toutes les chaînes codées en dur soient trouvées, pas un sous-ensemble.** La règle `no-literal-string` d'[`eslint-plugin-i18next`](https://github.com/edvardchen/eslint-plugin-i18next) signale chaque littéral qui atteint un utilisateur, et [`i18next-cli lint`](https://github.com/i18next/i18next-cli) fait de même sur JavaScript et TypeScript avec un analyseur SWC derrière. Ce paquet détecte deux formes précises, une table indexée par locale qui vit dans le code et une constante de prompt en Python, et ne verra pas `el.textContent = "Save"`. Sur ce critère il perd, et la table le dit.
- **Vous avez des traducteurs.** Weblate, Crowdin, Lokalise et Tolgee sont des éditeurs, des mémoires de traduction, de la traduction automatique, des captures d'écran de contexte et des files de relecture. Ce paquet a un fichier YAML. Si quelqu'un d'autre que l'auteur va toucher vos chaînes, commencez par là et gardez le contrôle à côté : il trouve des chaînes qui ne sont dans aucun catalogue, y compris le leur.
- **Vos messages ont besoin du genre, des dates, des devises ou d'une sélection imbriquée.** [FormatJS](https://formatjs.github.io/) et [LinguiJS](https://lingui.dev/) implémentent ICU MessageFormat, et [Project Fluent](https://projectfluent.org/) va plus loin avec la localisation asymétrique, où une langue cible peut ajouter une complexité grammaticale que la source n'a pas. Ce paquet fait les catégories de pluriel CLDR via `Intl.PluralRules` et l'interpolation nommée `{placeholder}`, et s'arrête là.
- **Vous avez déjà un framework.** Les équipes React, Vue et Svelte doivent prendre [shadcn/ui](https://ui.shadcn.com/) ou [Radix UI](https://www.radix-ui.com/), qui livrent un comportement que ce paquet demande à un modèle d'écrire ligne à ligne : piège de focus, verrouillage du défilement, retour du focus à la fermeture, et les schémas clavier du guide ARIA Authoring Practices. Radix les fait correctement d'emblée ; de la prose qui demande un `<dialog>` et un gestionnaire d'`Échap` ne porte pas la même garantie.
- **Il vous faut une bibliothèque de composants aujourd'hui.** [Preline UI](https://preline.co/) livre plus de 300 composants, [Flowbite](https://flowbite.com/) et [DaisyUI](https://daisyui.com/) quelques centaines à eux deux, tous avec le mode sombre, et [Bootstrap](https://getbootstrap.com/) respecte `prefers-reduced-motion` dans son propre CSS depuis des années. Ce paquet a sept formes de composants et huit extraits indexés par loi. Il ne concourt pas sur l'étendue et ne le fera pas.
- **Vous voulez une application qui marche à partir d'une phrase.** [v0](https://v0.dev/), [Lovable](https://lovable.dev/) et [bolt.new](https://bolt.new/) prennent un prompt et rendent une application déployée, avec l'authentification et une base de données câblées. Ils ne sont pas reproductibles, ils demandent un compte, et leur sortie embarque un runtime de framework. Les trois sont des échanges délibérés, et pour un prototype de week-end ce sont les bons.

## Les idées à prendre

Vingt-cinq outils ont été lus pour ce document. Étudier un concurrent sans rien en rapporter est une lecture perdue ; voici donc ce qu'il y a à prendre, du meilleur rapport au plus coûteux. Deux entrées sont des refus, avec leur raison.

**[Weblate](https://weblate.org/) : le contrôle des substituables.** Weblate fait passer un catalogue de contrôles qualité sur chaque traduction, et l'un d'eux compare les substituables de la traduction à ceux de la chaîne source : une ligne française qui laisse tomber le `{count}` que la ligne anglaise porte est un trou qui n'apparaît qu'à l'exécution. Ici, c'est la sœur d'une fonction qui existe déjà. `check_prompts()` dans `scripts/i18n_make.py` bloque la compilation sur un prompt sans locale `validated:` ; `check_placeholders()` la bloquerait sur toute locale dont l'ensemble de `{name}` diffère de celui de la locale source, appelée depuis `compile_json()` pour échouer à la compilation avec la même sévérité. Coût : une trentaine de lignes et un test. La moitié est déjà construite, puisque l'`interpolate()` émis laisse délibérément visible à l'écran un substituable non rempli au lieu de le blanchir. Il ne manque que la moitié à la compilation, ce qui en fait le meilleur rapport de la liste.

**[i18next-cli](https://github.com/i18next/i18next-cli) : la ligne de base du linter.** `i18next-cli lint --update-baseline` enregistre les constats du jour dans un fichier, pour que la barrière n'échoue que sur les nouveaux. C'est ce qui rend une règle adoptable dans une base de code qui compte déjà quatre cents violations : sans ça, la première exécution est un mur, et le crochet est retiré le même après-midi. Ici : un drapeau `--baseline .i18n-baseline.json` dans `scripts/audit_i18n.py`, qui soustrait les constats connus avant de calculer le code de sortie. Coût : un après-midi, bibliothèque standard seule, aucune dépendance nouvelle. La seule partie difficile est l'empreinte, parce qu'un numéro de ligne bouge à la modification suivante : la clé doit être la règle, plus le chemin, plus une empreinte de l'extrait, jamais la ligne.

**[i18next-cli](https://github.com/i18next/i18next-cli) : `status --unused`.** Le contrôle ne regarde que dans un sens, du code vers le catalogue, donc il ne remarque jamais un identifiant de message que plus personne n'appelle. `i18next-cli status` rend compte des deux sens, clés inutilisées comprises. Ici : une troisième règle, I18N003, ou un drapeau `--unused` sur la moitié « fabriquer », qui lit `locales/i18n.yaml` et cherche `t("id")` et `prompt("id")` dans l'arbre. Coût : une demi-journée. Elle doit signaler et non bloquer, parce qu'un `t(key)` à identifiant calculé est légitime et qu'aucune passe statique ne peut le résoudre. Une règle qui ne peut pas être sûre est une règle qui avertit.

**[i18next-cli](https://github.com/i18next/i18next-cli) : la commande `types`.** Elle engendre des définitions TypeScript depuis le catalogue, pour qu'une faute de frappe dans un identifiant de message casse la construction au lieu d'afficher l'identifiant à l'écran. Ici : une étape `--emit-types` sur `sprezzature-ui-i18n-make`, qui écrit `locales/i18n.d.ts` avec `type MessageId = "app.title" | "action.save" | ...` à côté de l'`i18n.js` émis, et un alias `Literal` dans `i18n_prompts.py`. Coût : une demi-journée, et prendre la moitié Python d'abord parce qu'elle est presque gratuite : le chargeur est déjà engendré depuis les mêmes données. La réserve honnête est que la sortie de ce paquet est du JavaScript sans étape de construction, donc le `.d.ts` paie dans un éditeur et pas en intégration continue (CI).

**[GNU gettext](https://www.gnu.org/software/gettext/) : le marqueur « fuzzy ».** Quand une chaîne source change, `msgmerge` marque toutes ses traductions comme approximatives au lieu de les garder en silence, et l'exécution les traite alors comme absentes. [i18n-ally](https://i18nally.org/) a refait la même idée sous la forme d'une détection de traduction périmée dans l'éditeur. Ici : ranger une courte empreinte du texte de la locale source avec chaque entrée, et faire signaler par `compile_json()` toute locale écrite contre une empreinte différente. Coût : un après-midi pour le code, plus un changement du format du catalogue, qui en est le vrai prix. Un changement de format demande un chemin de migration et un test prouvant qu'un ancien catalogue compile encore.

**[shadcn/ui](https://ui.shadcn.com/) : le mode de distribution.** shadcn/ui n'est pas une dépendance ; une commande copie la source du composant dans votre dépôt, où vous la possédez et la modifiez. C'est exactement la forme de ce paquet : `assets/components/*.html` et `assets/snippets/*.html` sont quinze fichiers faits pour être copiés et adaptés, et aucune commande ne les pose. Un `sprezzature-ui components add modal` serait une copie de fichier, rien de plus. Coût : une journée. L'argument contre est qu'il élargit un paquet dont le README promet de rester petit, et « ajouter des routes pour le nombre reviendrait à confondre l'étendue et la valeur » est la phrase de ce README lui-même.

**Refusé : l'`instrument` d'[i18next-cli](https://github.com/i18next/i18next-cli).** Il réécrit les sites d'appel, transformant `"Save"` en `t('save')` dans tout l'arbre, avec `--dry-run` et `--interactive` pour rendre ça supportable. Le `--fix` de ce paquet s'arrête délibérément avant, pour la raison qui arrête aussi `pybabel extract` : seul l'auteur sait quel identifiant l'appel doit porter, et si le code autour veut une forme plurielle ou un substituable. Le prendre voudrait dire entretenir un codemod pour chaque dialecte de JavaScript et pour Python, ce qui est l'essentiel de ce qu'est SWC. Ce qu'il y a à prendre de la même commande, c'est son `--dry-run` : aujourd'hui `--fix` écrit dès la première exécution, sans aperçu.

**Refusé : MessageFormat 2.0 comme syntaxe du catalogue.** La norme Unicode a atteint le statut de candidat final en mars 2025 et elle est stable dans CLDR depuis les versions LDML 47 et 48 ; c'est la bonne cible à long terme pour un format de message. Pas en 2026 : en mai 2026, le greffon MessageFormat 2 d'i18next comptait des téléchargements npm hebdomadaires à un chiffre contre environ 340 000 pour la bibliothèque `messageformat` sous-jacente, et le processus TC39 attend une douzaine d'organisations en production avant d'avancer. Livrer un analyseur pour une syntaxe que personne n'écrit encore, dans une exécution de 80 lignes, est un coût sans lecteur. À revoir le jour où `Intl.MessageFormat` arrive dans les navigateurs, parce que c'est le jour où le coût d'exécution tombe à zéro.

## Les familles du domaine

**Trouver les chaînes, les déplacer, les traduire.** Trois métiers, et la plupart des outils n'en font qu'un. Un linter trouve (`eslint-plugin-i18next`, `i18next-cli lint`) ; une chaîne d'outils de catalogue déplace et compile (GNU gettext avec Babel, FormatJS, LinguiJS, la moitié « fabriquer » d'ici) ; une plateforme traduit et relit (Weblate, Crowdin, Lokalise, Tolgee). Les outils qui couvrent deux des trois sont ceux qu'il vaut la peine de comparer, et `i18next-cli` en est l'exemple le plus net du domaine : un seul binaire qui extrait, contrôle, type, synchronise, et depuis juin 2026 enchaîne le tout dans une commande `localize` unique. Ce paquet couvre les deux premiers sur une tranche d'entrée plus étroite, et ne tente pas le troisième du tout.

**Le statique contre l'exécution, côté production.** Une bibliothèque de composants livre du comportement : Radix piège le focus et verrouille le défilement, Flowbite et Preline livrent une couche JavaScript, shadcn/ui vous tend de la source React. À l'autre bout se tiennent ceux qui ne livrent que du balisage ou que du CSS. HyperUI est du Tailwind à copier-coller, DaisyUI est du CSS sans le moindre runtime JavaScript, Pico CSS style les éléments sémantiques sans une seule classe, htmx est quatorze kilo-octets de gestion d'attributs sans aucune opinion sur l'apparence. `sprezzature-ui` appartient à ce bout-là par règle et non par circonstance : sa première règle dure est que la sortie ne contient jamais `react`, `vue`, `svelte`, `next` ni `angular`, et il lui est demandé de refuser et de proposer l'équivalent vanilla quand on le lui demande.

**La prose contre le produit.** La division la plus récente sépare un outil qu'on exécute d'un document qu'un modèle lit. v0, Lovable et bolt.new sont des produits : un prompt entre, une application sort, et le prix est un compte, un abonnement, et un résultat que personne ne peut reproduire deux fois. La moitié conception de ce paquet est la forme inverse : 4 772 lignes réparties sur 64 fichiers de référence, lues par le modèle qui se trouve devant, avec la sortie vérifiée ensuite par trois contrôleurs voisins déterministes. Aucune des deux formes n'est meilleure en général. Elles répondent à des questions différentes sur qui répond du résultat.

## Comparaison

Chaque alternative est notée de 1 à 5 sur chaque critère, plus c'est haut mieux c'est (⭐ faible à ⭐⭐⭐⭐⭐ le plus fort). Les notes relèvent d'un jugement argumenté, pas d'un banc d'essai, et chaque axe est orienté pour que plus d'étoiles signifie plus fort sur ce trait : pour le coût, plus d'étoiles signifie moins cher ou plus ouvert. Une seule étoile veut dire « ne le fait pas vraiment », jamais « inconnu ». La source lisible par machine est [`assets/paysage.csv`](assets/paysage.csv) : 25 outils sur 16 critères.

| Outil d'i18n ou d'interface | Détection des chaînes codées en dur | Langages de source couverts | Échafaudage et compilation du catalogue | Chargeur d'exécution fourni | Verdict en intégration continue avec code de sortie | Aucun runtime de framework en sortie | Accessibilité par défaut | Mode sombre par défaut | Garde de mouvement réduit | Personnalisation et thèmes | Déterministe et reproductible | Local et hors ligne (sans compte) | Gratuit ou open source | Maturité et écosystème | Étendue de la bibliothèque de composants | Flux de travail des traducteurs |
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| sprezzature-ui | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐ |
| i18next + i18next-cli | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐ |
| eslint-plugin-i18next | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ |
| i18n-ally | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ |
| FormatJS / react-intl | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐ |
| LinguiJS | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐ |
| GNU gettext + Babel | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐ |
| Project Fluent | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐ |
| Weblate | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ |
| Crowdin | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ |
| Lokalise | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ |
| Tolgee | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ |
| shadcn/ui | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |
| Tailwind Plus | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |
| DaisyUI | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ |
| Flowbite | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |
| Preline UI | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |
| HyperUI | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ |
| Radix UI | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ |
| Bootstrap | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |
| Pico CSS | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐ |
| htmx | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ |
| v0 (Vercel) | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |
| Lovable | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| bolt.new | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ |


![sprezzature-ui face à 24 autres outils d'i18n et d'interface, sur deux axes issus d'une analyse en composantes principales. Le paquet se tient seul dans le coin en haut à droite, par construction. À la même hauteur mais loin sur sa gauche se tient un amas serré de chaînes d'outils d'i18n : i18next avec i18next-cli, GNU gettext avec Babel, LinguiJS, eslint-plugin-i18next, FormatJS, Project Fluent et i18n-ally, avec Tolgee et Weblate juste en dessous. Lokalise et Crowdin sont à l'extrême gauche de l'axe horizontal. Le bas à droite tient les bibliothèques de composants en bande diagonale : Pico CSS, HyperUI, DaisyUI, Bootstrap, Preline UI, Flowbite, Radix UI, shadcn/ui et Tailwind Plus. En bas au centre, à l'écart de tout le reste, se trouvent Lovable, bolt.new et v0. L'axe horizontal oppose une chaîne d'outils qu'on exécute soi-même et dont on possède la sortie à une plateforme hébergée où d'autres se connectent ; l'axe vertical oppose une chaîne de catalogue déterministe qui rend un verdict à une large bibliothèque de composants tout faits.](assets/paysage.svg)

La source est [`assets/paysage.csv`](assets/paysage.csv), la table en étoiles ci-dessus et rien de plus, et la carte se régénère avec :

```sh
python ~/sprezzature/scripts/landscape_to_csv.py ~/sprezzature-ui/PAYSAGE.md --out ~/sprezzature-ui/assets/paysage.csv
standpoint assets/paysage.csv --outdir assets --stem paysage --check
```

La géométrie est une analyse en composantes principales (ACP) sur corrélations, et elle est **déterministe** : la même table donne la même carte à chaque exécution, quel que soit le modèle qui a nommé les pôles. Les quatre mots des bords viennent d'un modèle local via Ollama, et ils sont plus vagues que les charges qui les portent : ce sont les charges qui font le contrôle. Voici donc de quoi les deux axes sont faits.

**Horizontal, 41,9 % de la variance.** Déterministe et reproductible (+0,35), local et hors ligne (+0,34), mode sombre par défaut (+0,32) et personnalisation et thèmes (+0,31) tirent vers la droite ; le flux de travail des traducteurs (−0,36) et les langages de source couverts (−0,29) tirent vers la gauche. C'est l'axe de l'outil qu'on exécute et dont on possède la sortie contre la plateforme où d'autres se connectent, et `sprezzature-ui` se trouve tout à droite par construction : c'est la ligne de référence, et `standpoint` l'ancre en haut à droite. Le modèle a nommé les pôles Efficacité à gauche et Autonomie à droite.

**Vertical, 22,1 % de la variance.** Gratuit ou open source (+0,35), local et hors ligne (+0,34), déterministe et reproductible (+0,33), échafaudage et compilation du catalogue (+0,32) et verdict en intégration continue avec code de sortie (+0,30) chargent vers le haut ; l'étendue de la bibliothèque de composants (−0,33) et l'accessibilité par défaut (−0,24) chargent vers le bas. C'est la chaîne d'outils d'i18n contre la bibliothèque de composants, c'est-à-dire exactement les deux familles que la table a été construite pour tenir, et la carte a trouvé la coupure toute seule. Le modèle a nommé les pôles Robustesse en haut et Adaptabilité en bas.

**Deux axes portent 64,1 % de la table.** Plus d'un tiers de ce que disent ces 16 critères n'est pas sur cette page. Ce qui manque le plus clairement à la carte est ce sur quoi le premier paragraphe de ce fichier insiste : les axes voient un paquet gratuit, hors ligne, déterministe et sans framework, et ils ne voient pas que sa règle de détection couvre deux formes et non toute la classe, ce qui est la case à deux étoiles de la première colonne. `standpoint` écrit aussi une interprétation en prose à côté de la figure ; elle n'est pas reprise ici, parce qu'un modèle qui relit des notes écrites par quelqu'un n'est pas un résultat.

`--check` rend `leader_top_right: True` et `axis_labels_visible: True`, et `readable: False` : avec 25 points, cinq paires d'étiquettes risquent de se chevaucher (i18n-ally avec FormatJS, FormatJS avec Project Fluent, Crowdin avec Lokalise, Flowbite avec Preline UI, HyperUI avec Pico CSS). Le SVG est interactif, donc les noms se lisent au survol ; le PNG est celui qu'on lit de loin.

## Sources

- [i18next-cli](https://github.com/i18next/i18next-cli), la chaîne d'outils officielle d'i18next ; `i18next-parser` est déprécié à son profit
- [eslint-plugin-i18next](https://github.com/edvardchen/eslint-plugin-i18next) et la règle `no-literal-string`
- [i18n Ally](https://i18nally.org/), aujourd'hui porté par des forks communautaires
- [LinguiJS face à i18next](https://lingui.dev/misc/i18next), écrit par LinguiJS
- [MessageFormat 2 dans i18next : état de la migration, mai 2026](https://www.locize.com/blog/messageformat-2-i18next)
- [Fluent face à gettext](https://github.com/projectfluent/fluent/wiki/Fluent-vs-gettext), écrit par Project Fluent
- [Les plateformes de localisation comparées, 2026](https://alconost.com/en/blog/localization-platforms-comparison)
- [Radix, Headless UI et Ark UI comparés, 2026](https://codecudos.com/blog/radix-ui-vs-headless-ui-vs-ark-ui-2026)
- [Les bibliothèques de composants Tailwind classées, 2026](https://designrevision.com/blog/best-tailwind-component-libraries)
- [Lovable, Bolt et v0 comparés, 2026](https://superframeworks.com/compare/lovable-vs-bolt-vs-v0)

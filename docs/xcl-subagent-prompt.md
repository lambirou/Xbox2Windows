# Prompt d'orchestration - transfert XCL vers Xbox2Windows

Tu es l'orchestrateur d'implementation de Xbox2Windows. Ta mission est d'executer
docs/xcl-reference-plan.md en une serie de PRs petites et reviewables, reparties entre
sous-agents. XCL est une reference de comportement, jamais une source de code.

## A lire avant de commencer

- AGENTS.md
- CONTRIBUTING.md
- docs/experiments.md
- docs/xcl-reference-plan.md
- README.md

## Regles non negociables

1. Licence. XCL est GPL-2.0-only ; Xbox2Windows est MIT. Interdiction de copier ou traduire du
   code XCL, de lier XCL, ou de committer des sorties HLSL/DXIL generees par XCL. Les
   observations vont dans docs/xcl-reference.md avec le commit XCL et la date. Toute PR inspiree
   d'une observation XCL ajoute une note Provenance.
2. Donnees de jeu. Jamais de fichiers de jeu, dumps, logs, shaders, rapports ou captures contenant
   des donnees du titre. Utiliser game-files/ et out/, tous deux ignores par Git. Les fixtures
   doivent etre synthetiques ou construites depuis les sources.
3. Une PR = un comportement reviewable. Si un lot depasse environ 400 lignes utiles ou touche plus
   de trois zones, le decouper.
4. Tests. Chaque PR a un test positif, un controle negatif, la commande exacte et le resultat.
   Ne jamais supprimer ou affaiblir un test pour faire passer une PR.
5. Git. Chaque branche part de origin/main. Rebaser avant la PR. Ne jamais pousser sur main. Ne
   jamais merger sa propre PR.
6. PR. Titre au format area: behavior. Body avec Change, Verification, Evidence and follow-up,
   Checklist. Mentionner AI-assisted (Codex). Pour un resultat GPU, donner l'adaptateur, le
   pilote, la version de Windows et l'etat de la debug layer.
7. Perimetre. Ne pas transformer Xbox2Windows en emulateur runtime. Les shims servent le code
   recompile ; ils ne remplacent pas l'architecture de recompilation statique.

## Roles et propriete des fichiers

| Role | Mission | Fichiers possedes | Premiere PR |
| --- | --- | --- | --- |
| Orchestrateur | Planifie, revoit, rebase, pousse et ouvre les PRs. Ne code pas dans les fichiers d'un agent actif. | docs/xcl-implementation-status.md, descriptions de PR | XCL-00 |
| A - Docs et mesure | Reference XCL, matrice de capacites, rapport de compatibilite | docs/xcl-reference.md, docs/xcl-capability-matrix.md, tools/compat_report.py, tests/compat_report_check.py, README.md (section rapport) | XCL-00, XCL-01 |
| B - PE et imports | Routage HLE/Windows/stub, ordinales, delay-load, diagnostics | tools/pe_inventory.py, tools/intake_exe.py, tools/pe_run_package.py, tests/pe_*, tests/cpu/* (fixtures PE) | XCL-02, XCL-03 |
| C - XGameRuntime | Thunk protocol, XUser, XGameSave, PLS, XPackage, XGame, XSystem, XAsync, XTaskQueue | src/xgameruntime_shim.cpp, src/xgameruntime_shim.def, tests/xgameruntime_*, CMakeLists.txt (cible du shim) | XCL-04 a XCL-07 |
| D - D3D12.X | Device, heaps, listes compute, buffers console/UMA, listes graphics, PresentX | src/d3d12_xs_shim.cpp, src/d3d12_xs_shim.def, src/d3d12x_*.cpp/.h, tests/d3d12x_*, CMakeLists.txt (cibles D3D12.X) | XCL-08 a XCL-13 |
| E - Shaders | Corpus, couverture par mnemonic, familles d'instructions, tests GPU | tools/pixel_aot.py, tools/compute_store_aot.py, tools/mesh_entry_aot.py, tests/pixel_aot_check.py, tests/compute_store_check.py, tests/mesh_*, docs/experiments.md (section shader) | XCL-14 a XCL-18 |
| F - PSO et textures | Pipelines, root signatures, samplers statiques, tiling GFX10, BC et volumes | tools/pso_readiness.py, src/pso_*.cpp/.h, tests/pso_*, tools/bc7_tiles.py, tools/ttpf_*.py, tests/bc7_*, tests/texture_* | XCL-19 a XCL-23 |
| G - Bring-up et media | Premier stop GTA VI, audio, Bink, FSR4, BVH | tests/e2e_*, tools/audio_*, tools/media_*, docs/experiments.md (sections media) | XCL-24 a XCL-26 |

Chaque sous-agent ne modifie que ses fichiers. S'il a besoin d'un fichier partage
(CMakeLists.txt, README.md, docs/experiments.md), il demande l'accord de l'orchestrateur et
attend son tour. Un seul agent modifie un fichier partage a la fois.

## Backlog de PRs propose

Ouvrir les PRs dans cet ordre, avec au maximum quatre PRs ouvertes en meme temps. Les dependances
doivent etre mergees avant de commencer une PR qui en depend.

| ID | Agent | Branche | Perimetre | Depend de | Critere d'acceptation |
| --- | --- | --- | --- | --- | --- |
| XCL-00 | A | docs/xcl-reference | Reference, frontiere de licence, matrice de capacites | - | docs_links_check passe ; aucune donnee de jeu |
| XCL-01 | A | tools/compat-report | tools/compat_report.py et test synthetique | XCL-00 | rapport deterministe ; imports classes ; 0 inconnu sur la fixture |
| XCL-02 | B | pe/import-routing | Table HLE/Windows/stub et diagnostics intake_exe | XCL-01 | chaque import a une route ; test positif et negatif |
| XCL-03 | B | pe/delay-load-ordinals | Couverture delay-load et ordinales | XCL-02 | fixture PE avec les trois formes ; erreur nommee |
| XCL-04 | C | runtime/xgameruntime-thunks | Table de thunks et squelette du shim | XCL-01 | table issue des en-tetes publics ; test de chargement |
| XCL-05 | C | runtime/xuser-xgamesave | XUser et XGameSave | XCL-04 | titre synthetique ; 0 stub appele |
| XCL-06 | C | runtime/pls-xpackage | PLS et XPackage | XCL-04 | stockage persistant et package verifies |
| XCL-07 | C | runtime/xsystem-xgame | XSystem et XGame | XCL-04 | identite console et titre verifiees |
| XCL-08 | D | d3d12x/device-slots | Inventaire des slots et creation du device | XCL-04 | device cree ; IID inconnu nomme |
| XCL-09 | D | d3d12x/descriptor-heaps | Heaps CBV/SRV/UAV et samplers | XCL-08 | handles CPU/GPU et tables verifies |
| XCL-10 | D | d3d12x/compute-lists | Listes compute, dispatch et readback | XCL-09 | buffer connu apres dispatch |
| XCL-11 | D | d3d12x/console-buffers | Buffers aux adresses console et UMA | XCL-08 | adresse CPU/GPU identique dans la fenetre |
| XCL-12 | D | d3d12x/graphics-lists | Listes graphics et triangle | XCL-10 | triangle rendu dans une cible connue |
| XCL-13 | D | d3d12x/presentx | PresentX et frontiere de frame | XCL-12 | une frame presentee ; compteur verifie |
| XCL-14 | E | shader/corpus-report | Corpus, stages, dwords, formes non supportees | XCL-01 | records/programmes/streams separes ; JSON deterministe |
| XCL-15 | E | shader/qword-return-forms | Formes qword _rtn | XCL-14 | fixture positive, mutant detecte |
| XCL-16 | E | shader/qword-inc-dec | ds_inc_u64 et ds_dec_u64 | XCL-14 | fixture positive, mutant detecte |
| XCL-17 | E | shader/wave64-coverage | Couverture wave64/wave32 | XCL-14 | test GPU ou skip documente |
| XCL-18 | E | shader/mesh-as-forms | Formes mesh et AS | XCL-14 | pipeline mesh cree ou refus nomme |
| XCL-19 | F | pso/root-signatures | Root signatures et samplers statiques | XCL-08 | PSO cree pour une racine de test |
| XCL-20 | F | pso/vs-ps-cs | Pipelines VS/PS et CS | XCL-19, XCL-10 | draw et dispatch de test |
| XCL-21 | F | pso/ms-gs | Pipelines MS/PS et VS/GS/PS | XCL-20 | pipeline mesh et geometry de test |
| XCL-22 | F | texture/gfx10-tiling | Tiling GFX10 2D et mips | XCL-08 | texture synthetique byte-exact |
| XCL-23 | F | texture/bc-volume | BC1-BC7 et textures volume | XCL-22 | readback byte-exact ; format inconnu nomme |
| XCL-24 | G | e2e/gta-first-stop | Premier stop GTA VI et rapport | XCL-13, XCL-15, XCL-16 | stop reproductible ; aucune donnee de jeu |
| XCL-25 | G | audio/xaudio2-voices | Voix XAudio2 et formats | XCL-24 | voix synthetique audible/verifiee |
| XCL-26 | G | media/bink-fsr-bvh | Bink, FSR4 et BVH de bout en bout | XCL-24 | chemin media de test verifie |

Le backlog est une proposition. L'orchestrateur peut fusionner deux PRs si elles restent un seul
comportement reviewable, ou decouper une PR si elle depasse le budget.

## Protocole d'execution

1. Synchroniser main avec origin/main et verifier que la CI est verte.
2. Lancer A et E en parallele. A produit XCL-00 et XCL-01 ; E peut preparer XCL-14 mais attend le
   schema de rapport de XCL-01 pour le brancher.
3. Des que XCL-01 est mergee, lancer B et C en parallele.
4. Des que C a livre XCL-04, lancer D.
5. Des que D a livre XCL-08 et E a livre XCL-14, lancer F.
6. Des que D a livre XCL-13 et E a livre XCL-15/XCL-16, lancer G.
7. Garder au maximum quatre PRs ouvertes. Merger dans l'ordre des dependances. Rebaser les
   branches dependantes apres chaque merge.
8. Tenir docs/xcl-implementation-status.md a jour : PR, etat, commit, premier echec, prochaine
   action. Ce fichier est le tableau de bord, pas un journal de conversation.

## Contrat de sortie d'un sous-agent

Chaque sous-agent rend un rapport court avec :

- la branche et le commit local ;
- les fichiers modifies ;
- la commande exacte de build et de test ;
- le resultat observe et le resultat attendu ;
- le premier echec ou la premiere limite, s'il y en a ;
- la note de provenance XCL si applicable ;
- les tests non executes et la prerequisite manquante.

Le sous-agent ne pousse pas et n'ouvre pas de PR. L'orchestrateur relit le diff, verifie la
licence, relance les tests, rebase, pousse sur le fork lambirou/Xbox2Windows et ouvre la PR vers
R0Y00/Xbox2Windows:main.

## Definition of done d'une PR

- Un seul comportement reviewable.
- Tests positif et negatif ajoutes.
- Documentation ou README mis a jour si la capacite change.
- Aucun fichier de jeu, dump, log ou secret.
- Provenance XCL si une observation a guide le travail.
- Body de PR avec Change, Verification, Evidence and follow-up, Checklist.
- Mention AI-assisted (Codex).
- Commande exacte et resultat dans la PR.

## Commandes de reference

Synchronisation et branche :

    git fetch origin main
    git switch -c <branche> origin/main

Build et tests Windows :

    cmake --preset dev
    cmake --build --preset dev
    ctest --preset dev --no-tests=error -R '<filtre>' -V

Tests Python purs :

    .\out\pe-env\Scripts\python.exe -B tests/docs_links_check.py
    .\out\pe-env\Scripts\python.exe -B tests/form_coverage_check.py
    .\out\pe-env\Scripts\python.exe -B tests/compat_report_check.py

Pour un test GPU, preciser WARP ou hardware, l'adaptateur, le pilote, la version de Windows et la
debug layer. Un skip n'est ni un pass ni un fail.

## Premiere action

1. Reprendre la branche locale docs/xcl-reference-plan, commit 5630abe, pour XCL-00.
2. Ouvrir XCL-00 puis XCL-01.
3. Lancer E sur XCL-14 en lecture seule (corpus et schema), sans modifier les fichiers de A.
4. Annoncer le premier point de blocage apres trois PRs, avec les commandes et les resultats.


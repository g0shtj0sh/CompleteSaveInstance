<p align="center">
  <img src="assets/brand/banner.png" alt="CompleteSaveInstance — archivage d’instances Roblox" width="100%" />
</p>

# CompleteSaveInstance

**Une base claire pour sauvegarder les instances Roblox accessibles.**

[English](README.md) · [Utilisation](docs/USAGE.md) · [Dépannage](docs/TROUBLESHOOTING.md) · [Feuille de route](docs/ROADMAP.md)

CompleteSaveInstance est un projet Luau d’export de places et de modèles Roblox.
Cette première étape apporte son identité visuelle, sa documentation, ses
espaces de noms et les contrôles du dépôt. La fiabilité des exports dans Roblox
et leur ouverture dans Studio restent à valider pour cette distribution.

## Ce qui est présent

- Export binaire et XML hérité du moteur existant.
- Sélection des instances et exclusion de propriétés.
- Script principal `saveinstance.luau` et variante Lua plus ancienne.
- Logo, bannière, guides, modèles de tickets et contrôles automatiques.

## Premier essai

Commencer par une petite place possédée ou autorisée. Lire le
[guide d’utilisation](docs/USAGE.md), vérifier les API d’écriture sur un fichier
témoin et utiliser les options explicites du [README principal](README.md#getting-started).

Le dépôt est privé : son URL GitHub brute nécessite un accès autorisé depuis
un runtime Roblox. Utiliser une copie locale authentifiée ; ne jamais intégrer
un token GitHub au script.

Une fonction terminée ne garantit pas l’existence du fichier. Vérifier sa
présence, puis son ouverture et son contenu dans Roblox Studio. Les références
d’assets ne constituent pas une copie de leurs fichiers binaires.

## Suite du développement

La priorité est le diagnostic : inventaire, logs bufferisés, rapport précis,
validation du fichier et reprise après interruption. Ces fonctionnalités sont
des objectifs ; elles ne sont pas annoncées comme terminées.

Le client ne dispose pas des scripts serveur non répliqués, des DataStores
privés ou des objets jamais chargés. Pour ses propres projets, examiner
d’abord les exports proposés par Roblox Studio.

## Licence et origine

Licence [AGPL-3.0](LICENSE). Code hérité de
[UniversalSynSaveInstance](https://github.com/luau/UniversalSynSaveInstance).
Crédit conservé : **UniversalSynSaveInstance https://discord.gg/wx4ThpAsmw**.
Les détails de provenance figurent dans [NOTICE.md](NOTICE.md).

Projet indépendant, sans affiliation avec Roblox Corporation.

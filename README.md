# ecospheres-scripts

Collection de scripts pour manipuler les données d'Ecosphères sur data.gouv.fr.

## Installation

Ajouter la configuration en variable d'environnement :

```shell
export DATAGOUVFR_API_KEY=xxx
```

```shell
python3 -mvenv pyenv
source pyenv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Scripts

### Bouquets

#### Copy

Copie un bouquet d'un environnement à l'autre.

```shell
python ecospheres/bouquets.py copy itineraires-fraicheur [--source prod] [--destination demo]
```

`source` et `destination` peuvent valoir `demo` ou `prod` et on récupère dans ce cas la configuration depuis le dépôt github. Il est aussi possible de fournir le chemin d'un fichier de configuration local.


### Harvest

Helpers pour gérer une série de moissonneurs data.gouv.


#### Mise en place

Éditer `harvests.yaml` pour y configurer l'environnement, ou utiliser un ficher d'environnement séparé.

Dans le cas d'un fichier d'environnement séparé (`env.yaml` dans les exemples ci-dessous), le fichier doit uniquement contenir la section `api` de la config :

```yaml
api:
  url: https://demo.data.gouv.fr
  token: ...
```

#### Création des moissonneurs

Seuls les moissonneurs manquants sont créés.
Les moissonneurs existants ne sont pas modifiés.

```shell
python create-harvesters.py [--dry-run] harvests.yaml [env.yaml]
```

#### Suppression des jeux de données associés aux moissonneurs

*Script hacké un peu vite, à manipuler avec précaution.*

À exécuter avant de supprimer une organisation ou un de ses moissonneurs.

```shell
python delete-datasets.py [--dry-run] harvests.yaml [env.yaml]
```


### Metadata

*Temporary test script to apply XSL.*


### Migrations

#### Migration du schema des extras

Première étape : duplication des anciens extras vers les nouveaux.

```shell
python ecospheres/migrations/20240529_1_extras_schema.py migrate [--dry-run] [slug]
```

Deuxième étape : déploiement de la version utilisant les nouveaux extras.

Troisème étape : suppression des anciens extras.

```shell
python ecospheres/migrations/20240529_2_extras_schema.py migrate [--dry-run] [slug]
```

### Universe

#### Mise en place

Éditer `universe.yaml` pour y configurer l'environnement, ou utiliser un ficher d'environnement séparé.

Dans le cas d'un fichier d'environnement séparé (`env.yaml` dans les exemples ci-dessous), le fichier doit uniquement contenir la section `api` de la config :

```yaml
api:
  url: https://demo.data.gouv.fr
  token: ...
```

#### Créer ou mettre à jour un univers

```shell
python feed-universe.py [--dry-run] [options] universe.yaml [env.yaml]
```

Options :
- `--fail-on-error` : Abort on error.
- `--keep-empty` : Conserve les organisations ne contenant pas de datasets pour la génération de la section `organizations`.
- `--reset` : Vide l'univers de tous ses datasets avant de le repeupler. Si la conservation de l'id du topic existant n'a pas d'importance, il est plus simple de supprimer/recréer le topic.
- `--slow` : À combiner avec `--reset` si l'univers contient beaucoup de jeux de données (milliers+) pour éviter les timeouts de l'API data.gouv.


#### Mettre à jour le déploiement correspondant

Une fois le script terminé, il faut mettre à jour la section `organizations` du fichier de config [`udata-front-kit`](https://github.com/opendatateam/udata-front-kit/blob/main/configs/ecospheres/config.yaml) correspondant à l'environnement data.gouv mis à jour.

Pour ecologie.data.gouv :
- demo.data.gouv.fr : Mettre à jour la config de la branche `main`, puis merger dans la branche `ecospheres-demo`.
- www.data.gouv.fr : Mettre à jour la config de la branche `ecospheres-prod`.

Puis, dans le cas où la config a changé, faire une release et déploiement de l'environnement mis à jour.

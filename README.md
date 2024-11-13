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

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

### Harvest

XXX

### Metadata

XXX

### Universe

XXX

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

### Bouquets

#### Copy

Copie un bouquet d'un environnement à l'autre.

```shell
python ecospheres/bouquets.py copy itineraires-fraicheur [--source prod] [--destination demo]
```

`source` et `destination` peuvent valoir `demo` ou `prod` et on récupère dans ce cas la configuration depuis le dépôt github. Il est aussi possible de fournir le chemin d'un fichier de configuration local.

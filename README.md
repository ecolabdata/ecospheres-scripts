# ecospheres-scripts

Collection de scripts pour manipuler les données d'Ecosphères sur data.gouv.fr.

## Installation

Ajouter la configuration en variable d'environnement :

```shell
export DATAGOUVFR_URL=https://demo.data.gouv.fr
export DATAGOUVFR_API_KEY=xxx
export ECOSPHERES_TAG=ecospheres
```

```shell
python3 -mvenv pyenv
source pyenv/bin/activate
pip install -r requirements.txt
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
python migrations/20240529_1_extras_schema.py migrate [--dry-run] [slug]
```

Deuxième étape : déploiement de la version utilisant les nouveaux extras.

Troisème étape : suppression des anciens extras.

```shell
python migrations/20240529_2_extras_schema.py migrate [--dry-run] [slug]
```

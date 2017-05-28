# Publication ERDF

## Pourquoi ?

Le but est d'automatiser les calculs de relevés de compte à partir des mesures de ERDF envoyé dans un .zip chaque mois.

## Comment ?

Il suffit de transferer l'email de `bnpr-pub@distribution.edf.fr` vers `	bnpr-pub@mg.turbinealternateur.fr`. Un mail de retour sera renvoyé à l'expéditeur avec le total de kW pour chaque compteur.

### Oui mais techniquement ?

Les entrées DNS MX pour sous domaine `mg.turbinealternateur.fr` redirige les mails vers le service https://www.mailgun.com/ qui route les données vers une [fonction Azure](https://azure.microsoft.com/fr-fr/services/functions/).
Cette fonction Azure, dont le code est dans cette repositorie, analyse le .zip et renvoie un mail avec le détail. 

### Options

Le service supporte des options passé dans l'adresse email. Le format est
`bnpr-pub+clef=valeur(|clef=valeur...)@distribution.edf.fr`.

| Function | Clef | Valeur | Example
| ------ | ------ | ------ | ------ |
| Ecrêtage  | cap | entier kW | écrêtage à 400 kW `bnpr-pub+cap=400@mg.turbinealternateur.fr `|

## Installation

### Configuration de mailgun

Suivre la doc pour l'enregistrement d'un nom de domaine.

### Configuration de Azure Function

Suivre la doc pour la création d'un compte.

Pensez à ajouter la variable d'environement `MG_KEY_API` pour que Azure puisse:

* lire les emails (par défault, une notification est envoyée)
* envoyer des emails

### Build

```sh
$ make build
```

# FermeGest — Application web de gestion d'une ferme

Projet de fin d'année (2ᵉ année, cycle ingénieur - programmation) · Django 5.2 (MVT) · SQLite

Trois acteurs : **Fermier**, **Expert** (agronome / vétérinaire) et **Administrateur Django**.

## Installation (Windows, Linux ou macOS)

```bash
python -m venv venv
source venv/bin/activate          # Windows : venv\Scripts\activate
pip install -r requirements.txt   # (gunicorn n'est nécessaire qu'en production Linux)
python manage.py migrate          # crée db.sqlite3
python manage.py seed_demo        # (facultatif) données de démonstration
python manage.py runserver
```

Ouvrir http://127.0.0.1:8000/ .

## Comptes de démonstration (après `seed_demo`)

| Rôle | Identifiant | Mot de passe |
|---|---|---|
| Administrateur Django (/admin/) | `admin` | `Admin2026!` |
| Fermier | `mbadinga` | `Ferme2026!` |
| Expert agronome | `dr.nze` | `Expert2026!` |
| Expert vétérinaire | `dr.ondo` | `Expert2026!` |
| Expert en attente de validation | `expert.attente` | `Expert2026!` |

> Ces mots de passe sont réservés à la démonstration : à changer avant toute mise en ligne.

## Tests

```bash
python manage.py test        # 22 tests (règles de gestion, cloisonnement, permissions, workflow)
```

## Structure

```
config/         paramètres, routage principal, WSGI
comptes/        utilisateurs : profil + rôle, inscription, connexion, permissions
exploitation/   cœur métier : ferme, parcelles, cultures, récoltes, troupeaux, soins, stock, finances, tâches
conseils/       demandes de conseil, fil de discussion, fiches techniques
templates/      gabarits Django (base, crud génériques, pages par module)
static/         Bootstrap 5, Bootstrap Icons, Chart.js (embarqués : fonctionne hors ligne), CSS
deploy/         exemples de configuration Gunicorn, Nginx et script de sauvegarde
```

## Production (rappel)

Définir `DJANGO_DEBUG=0`, `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, puis
`python manage.py collectstatic` et servir `staticfiles/` et `media/` par Nginx (voir `deploy/`).

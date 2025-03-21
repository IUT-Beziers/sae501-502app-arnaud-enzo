# Documentation Développeur

## Table des matières
1. Introduction
2. Structure du projet
3. Installation
4. Configuration
5. Utilisation
6. Documentation de l'API
7. Tests
8. Déploiement
9. Contribution
10. Support
11. Licence

## Introduction
Ce projet est une application Django qui permet de surveiller les paquets ARP et de détecter les attaques sur ce même protocol. Il comprend une interface utilisateur pour gérer les agents et visualiser les données, ainsi qu'une API REST pour interagir avec les données.

## Structure du projet
Voici la structure du projet :

```
App/
    .env
    docker-compose.yml
    Dockerfile
    manage.py
    nginx.conf
    polls/
    requirements.txt
    API/
        __init__.py
        admin.py
        apps.py
        models.py
        serializers.py
        tests.py
        views.py
        management/
            commands/
                createadminuser.py
                processpackets.py
    App/
        __init__.py
        asgi.py
        settings.py
        urls.py
        wsgi.py
    Frontend/
        __init__.py
        admin.py
        apps.py
        models.py
        tests.py
        views.py
        migrations/
    staticfiles/
    templates/
        base.html
        dashboard/
            index.html
            home.html
            agent.html
            settings.html
```

## Installation
### Prérequis
- Docker
- Docker Compose

### Étapes d'installation
1. Clonez le dépôt :
    ```sh
    git clone https://github.com/IUT-Beziers/sae501-502app-arnaud-enzo.git
    cd sae501-502app-arnaud-enzo/App
    ```

2. Créez un fichier `.env` à la racine du dossier `App` en utilisant le modèle fourni dans `.env.example`.

3. Construisez et démarrez les conteneurs Docker :
    ```sh
    docker-compose up --build
    ```

## Configuration
La configuration de l'application se fait principalement via le fichier `.env`. Voici les variables de configuration importantes :

- `DJANGO_SECRET_KEY` : Clé secrète Django.
- `DEBUG` : Mode debug (True/False).
- `DJANGO_ALLOWED_HOSTS` : Hôtes autorisés.
- `DATABASE_ENGINE` : Moteur de base de données (ex: `postgresql_psycopg2`).
- `DATABASE_NAME` : Nom de la base de données.
- `DATABASE_USERNAME` : Nom d'utilisateur de la base de données.
- `DATABASE_PASSWORD` : Mot de passe de la base de données.
- `DATABASE_HOST` : Hôte de la base de données.
- `DATABASE_PORT` : Port de la base de données.
- `DJANGO_SUPERUSER_USERNAME` : Nom d'utilisateur du superutilisateur.
- `DJANGO_SUPERUSER_PASSWORD` : Mot de passe du superutilisateur.
- `DJANGO_SUPERUSER_EMAIL` : Email du superutilisateur.
- `APP_FQDN` : Nom de domaine complet de l'application.
- `SCRIPT_URL` : URL du script d'installation de l'agent.
- `ARP_FLOOD_THRESHOLD` : Seuil de détection des spams ARP.

## Utilisation
### Démarrage de l'application
Pour démarrer l'application, utilisez la commande suivante :
```sh
docker-compose up
```

### Accès à l'application
- Interface utilisateur : `http://fqdn/`
- API : `http://fqdn/api/`

## Documentation de l'API
L'API REST est construite avec Django REST Framework. Voici les principaux points de terminaison :

- `GET /api/users/` : Liste des utilisateurs.
- `GET /api/groups/` : Liste des groupes.
- `GET /api/packets/` : Liste des paquets ARP.
- `POST /api/packets/` : Ajouter un paquet ARP.
- `GET /api/agents/` : Liste des agents.
- `POST /api/agents/` : Ajouter un agent.
- `GET /api/analysis/` : Liste des analyses d'attaques.


## Déploiement
Pour déployer l'application en production, assurez-vous de configurer les variables d'environnement appropriées dans le fichier `.env` et de désactiver le mode debug (`DEBUG=False`). Utilisez ensuite Docker Compose pour démarrer les conteneurs :
```sh
docker-compose up -d
```

## Support
Pour toute question ou problème, veuillez ouvrir une issue sur GitHub.

## Licence
Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.
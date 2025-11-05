# ROYAL Bank - SPHINX

Application bancaire en ligne Django avec authentification sécurisée, gestion de comptes, transactions, et support client.

## Fonctionnalités

- 🔐 Authentification à deux facteurs (2FA) avec OTP par email
- 💰 Gestion de compte bancaire avec solde et transactions
- 📊 Tableau de bord avec aperçu des finances
- 🏦 Relevé d'Identité Bancaire (RIB) format canadien
- 💱 Convertisseur de devises en temps réel (CAD, EUR, USD)
- 📧 Emails transactionnels avec templates HTML professionnels
- 💬 Support client intégré
- 🔔 Système de notifications

## Installation locale

1. Cloner le dépôt :
```bash
git clone https://github.com/Chaka06/ROYALBANK-SYNDOU.git
cd ROYALBANK-SYNDOU
```

2. Créer un environnement virtuel :
```bash
python -m venv .venv
source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Configurer les variables d'environnement :
Créer un fichier `.env` à la racine :
```env
DEBUG=1
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=127.0.0.1,localhost
DEFAULT_FROM_EMAIL=support@virement.net
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-password
EMAIL_USE_TLS=1
```

5. Appliquer les migrations :
```bash
python manage.py migrate
```

6. Créer un superuser :
```bash
python manage.py createsuperuser
```

7. Lancer le serveur de développement :
```bash
python manage.py runserver
```

## Déploiement sur Render

1. Connecter le dépôt GitHub à Render
2. Le fichier `render.yaml` configurera automatiquement :
   - Service web Django
   - Base de données PostgreSQL
   - Variables d'environnement

3. Configurer les variables d'environnement dans Render :
   - `DEBUG=0`
   - `SECRET_KEY` (généré automatiquement)
   - `ALLOWED_HOSTS` (configuré automatiquement)
   - `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` (pour les emails SMTP)

## Notifications par email

Les utilisateurs reçoivent un email automatiquement à chaque création d'une notification par l'administrateur.

- Le signal est défini dans `notifications/models.py` et envoie un email HTML avec le template `templates/emails/notification.html`.
- En développement (sans SMTP), les emails sont écrits dans `tmp/emails/` grâce au backend "filebased".
- En production, configurez les variables SMTP suivantes pour activer l'envoi réel :

```env
DEFAULT_FROM_EMAIL=support@virement.net
EMAIL_HOST=mail.virement.net
EMAIL_PORT=587
EMAIL_HOST_USER=support@virement.net
EMAIL_HOST_PASSWORD=***  # à renseigner dans Render en tant que Secret
EMAIL_USE_TLS=1
EMAIL_USE_SSL=0
```

Sans `EMAIL_HOST_PASSWORD`, Django basculera automatiquement sur l'écriture de fichiers dans `tmp/emails/` et aucun email ne sera expédié.

## Structure du projet

```
SPHINX/
├── accounts/          # Gestion des comptes et authentification
├── transactions/      # Gestion des transactions
├── notifications/     # Système de notifications
├── support/          # Support client et chat
├── profiles/         # Profils utilisateurs
├── sphinx/           # Configuration Django
├── templates/        # Templates HTML
├── static/           # Fichiers statiques (CSS, images)
└── manage.py
```

## Technologies utilisées

- Django 4.2
- PostgreSQL (production) / SQLite (développement)
- Bootstrap 5
- Gunicorn (production)
- WhiteNoise (fichiers statiques)

## Licence

Propriétaire - Royal Bank of Canada


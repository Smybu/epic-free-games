# 🎮 Epic Games — Alertes de jeux gratuits par e-mail

Un script Python qui surveille les offres de jeux gratuits de l’**Epic Games Store** et envoie un e-mail lorsqu’il détecte de nouveaux jeux gratuits.

Le message contient les titres des jeux, leurs descriptions, les dates de l’offre et un lien pour accéder à chaque jeu sur l’Epic Games Store.

## ✨ Fonctionnalités

- 🇫🇷 Récupération des offres en français pour la France.
- 🎁 Détection des jeux dont le prix promotionnel est de **0 €**.
- 🕔 Vérification prévue le jeudi à partir de **17 h, heure de Paris**.
- 📧 Envoi d’un e-mail via Gmail, avec une version texte et une présentation HTML.
- 🔗 Liens directs vers les pages des jeux.
- 🧠 Historique local dans `seen_games.json` pour éviter de renvoyer une alerte pour un jeu déjà enregistré.
- 🔐 Configuration des identifiants par variables d’environnement, sans les écrire en dur dans le code.

## 🧰 Prérequis

- Python 3.9 ou plus récent recommandé.
- Un compte Gmail.
- Un mot de passe d’application Gmail si la validation en deux étapes est activée.
- Git, si vous souhaitez cloner le dépôt.

## 🚀 Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/VOTRE-PSEUDO/VOTRE-DEPOT.git
cd VOTRE-DEPOT
```

Remplacez l’adresse par celle de votre dépôt GitHub.

### 2. Installer les dépendances

```bash
pip install requests python-dotenv
```

Vous pouvez aussi créer un fichier `requirements.txt` contenant :

```text
requests
python-dotenv
```

Puis installer les dépendances avec :

```bash
pip install -r requirements.txt
```

### 3. Configurer les variables d’environnement

Pour une exécution locale, créez un fichier `.env` à la racine du projet :

```env
EMAIL_FROM=votre-adresse@gmail.com
EMAIL_TO=adresse-de-destination@example.com
EMAIL_PASSWORD=votre-mot-de-passe-application
```

- `EMAIL_FROM` : adresse Gmail utilisée pour envoyer les messages.
- `EMAIL_TO` : adresse qui reçoit les alertes.
- `EMAIL_PASSWORD` : mot de passe d’application Gmail utilisé pour l’envoi SMTP.

**Sécurité :** ne mettez jamais vos vrais identifiants dans le code ni dans un fichier publié sur GitHub. Ajoutez `.env` à votre `.gitignore` et ne partagez jamais votre mot de passe d’application. Pour Gmail, utilisez de préférence un mot de passe d’application lorsque cette option est disponible, et non le mot de passe habituel de votre compte.

### 4. Lancer le script

Remplacez `main.py` par le nom réel de votre fichier Python si nécessaire :

```bash
python main.py
```

Le script vérifie l’heure française. S’il n’est pas jeudi à partir de 17 h, il s’arrête sans rechercher les offres ni envoyer d’e-mail.

## ⚙️ Utilisation avec GitHub Actions

Pour exécuter le script automatiquement sur GitHub, configurez les secrets du dépôt :

1. Ouvrez votre dépôt GitHub.
2. Allez dans **Settings → Secrets and variables → Actions**.
3. Cliquez sur **New repository secret**.
4. Créez les secrets suivants avec les valeurs adaptées à votre compte :

| Nom du secret | Utilité |
|---|---|
| `EMAIL_FROM` | Adresse Gmail expéditrice |
| `EMAIL_TO` | Adresse e-mail destinataire |
| `EMAIL_PASSWORD` | Mot de passe d’application Gmail |

Dans le workflow qui exécute le script, transmettez les secrets comme variables d’environnement à l’étape concernée :

```yaml
- name: Installer les dépendances
  run: pip install requests python-dotenv

- name: Exécuter le script
  env:
    EMAIL_FROM: ${{ secrets.EMAIL_FROM }}
    EMAIL_TO: ${{ secrets.EMAIL_TO }}
    EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
  run: python main.py
```

Adaptez `main.py` au nom de votre script et intégrez ces étapes à votre workflow existant.

**Important :** le script ne s’exécute réellement que si le workflow GitHub Actions le lance. La vérification interne du jeudi à 17 h ne remplace pas la planification du workflow. Configurez donc le déclencheur `schedule` de votre workflow pour qu’il lance le script au moment voulu. Les horaires `schedule` de GitHub Actions sont exprimés en UTC ; tenez compte du changement entre l’heure d’hiver et l’heure d’été en France.

Si le workflow utilise un fichier `seen_games.json`, vérifiez également comment cet historique est conservé entre deux exécutions : l’environnement d’un runner GitHub Actions est généralement éphémère. Sans persistance de ce fichier, l’historique peut être perdu d’une exécution à l’autre.
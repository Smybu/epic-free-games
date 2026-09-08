from datetime import datetime
import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
from dotenv import load_dotenv


# ============================================================
# Configuration
# ============================================================

load_dotenv()

EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

SEEN_FILE = "seen_games.json"

EPIC_API_URL = (
    "https://store-site-backend-static-ipv4.ak.epicgames.com"
    "/freeGamesPromotions"
)


# ============================================================
# Récupération des jeux gratuits Epic
# ============================================================

def get_free_games():
    params = {
        "locale": "fr-FR",
        "country": "FR",
        "allowCountries": "FR",
    }

    print("🌐 Connexion à l'API Epic Games...")

    response = requests.get(
        EPIC_API_URL,
        params=params,
        timeout=20,
    )

    response.raise_for_status()

    data = response.json()

    elements = (
        data.get("data", {})
        .get("Catalog", {})
        .get("searchStore", {})
        .get("elements", [])
    )

    games = []

    print(f"📦 {len(elements)} offres récupérées.")

    for game in elements:
        title = game.get("title")

        if not title:
            continue

        promotions = game.get("promotions")

        if not promotions:
            continue

        # Promotions actuellement actives
        active_promotions = promotions.get(
            "promotionalOffers",
            []
        )

        if not active_promotions:
            continue

        for promotion in active_promotions:
            offers = promotion.get(
                "promotionalOffers",
                []
            )

            for offer in offers:
                start_date = offer.get("startDate")
                end_date = offer.get("endDate")

                if not start_date or not end_date:
                    continue

                # ====================================================
                # Vérification du prix
                # ====================================================

                price = game.get(
                    "price",
                    {}
                ).get(
                    "totalPrice",
                    {}
                )

                discount_price = price.get(
                    "discountPrice"
                )

                # Le jeu doit coûter 0 €
                if discount_price != 0:
                    continue

                # ====================================================
                # URL Epic Games
                # ====================================================

                page_slug = (
                    game.get("catalogNs", {})
                    .get("mappings", [{}])[0]
                    .get("pageSlug")
                )

                if page_slug:
                    game_url = (
                        "https://store.epicgames.com/fr/p/"
                        + page_slug
                    )

                elif game.get("productSlug"):
                    game_url = (
                        "https://store.epicgames.com/fr/p/"
                        + game["productSlug"]
                    )

                else:
                    game_url = (
                        "https://store.epicgames.com/fr/free-games"
                    )

                games.append(
                    {
                        "id": game.get("id"),
                        "title": title,
                        "description": game.get(
                            "description",
                            ""
                        ),
                        "start": start_date,
                        "end": end_date,
                        "url": game_url,
                    }
                )

    # ============================================================
    # Évite les doublons
    # ============================================================

    unique_games = {}

    for game in games:
        game_id = game["id"] or game["title"]
        unique_games[game_id] = game

    return list(unique_games.values())


# ============================================================
# Jeux déjà envoyés
# ============================================================

def load_seen_games():
    if not os.path.exists(SEEN_FILE):
        return set()

    try:
        with open(
            SEEN_FILE,
            "r",
            encoding="utf-8",
        ) as file:
            return set(json.load(file))

    except (
        json.JSONDecodeError,
        OSError,
    ):
        return set()


def save_seen_games(seen_games):
    with open(
        SEEN_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            sorted(seen_games),
            file,
            indent=2,
            ensure_ascii=False,
        )


# ============================================================
# Envoi du mail
# ============================================================

def send_email(games):

    if (
        not EMAIL_FROM
        or not EMAIL_TO
        or not EMAIL_PASSWORD
    ):
        raise RuntimeError(
            "Variables EMAIL_FROM, EMAIL_TO ou "
            "EMAIL_PASSWORD manquantes."
        )

    if not games:

        subject = (
            "🎮 Epic Games — aucun nouveau jeu gratuit"
        )

        html_body = """
        <html>
        <body style="
            font-family: Arial, sans-serif;
            color: #222;
            max-width: 700px;
            margin: auto;
            padding: 20px;
        ">

            <h2>🎮 Epic Games Store</h2>

            <p>
                Aucun nouveau jeu gratuit n'a été
                détecté cette semaine.
            </p>

            <p>
                Bonne journée et bon jeu !
            </p>

        </body>
        </html>
        """

        text_body = (
            "Epic Games Store\n\n"
            "Aucun nouveau jeu gratuit n'a été "
            "détecté cette semaine."
        )

    else:

        subject = (
            "🎮 Nouveaux jeux gratuits Epic Games !"
        )

        game_cards = ""

        text_body = (
            "🎮 Nouveaux jeux gratuits Epic Games !\n\n"
        )

        for game in games:

            title = game["title"]

            description = (
                game.get("description")
                or "Aucune description disponible."
            )

            url = game["url"]

            start = datetime.fromisoformat(
                game["start"].replace(
                    "Z",
                    "+00:00",
                )
            ).strftime("%d/%m/%Y")

            end = datetime.fromisoformat(
                game["end"].replace(
                    "Z",
                    "+00:00",
                )
            ).strftime("%d/%m/%Y")

            # ====================================================
            # Version texte
            # ====================================================

            text_body += (
                f"🎮 {title}\n\n"
                f"{description}\n\n"
                f"📅 Gratuit du : {start}\n"
                f"📅 Jusqu'au : {end}\n\n"
                f"🔗 {url}\n\n"
                f"{'-' * 50}\n\n"
            )

            # ====================================================
            # Carte HTML
            # ====================================================

            game_cards += f"""
            <div style="
                border: 1px solid #ddd;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 20px;
                background-color: #f8f8f8;
            ">

                <h2 style="
                    margin-top: 0;
                    margin-bottom: 10px;
                    color: #222;
                ">
                    🎮 <strong>{title}</strong>
                </h2>

                <p style="
                    line-height: 1.6;
                    font-size: 15px;
                ">
                    {description}
                </p>

                <p style="
                    font-size: 14px;
                    color: #555;
                ">
                    📅 <strong>Gratuit du :</strong>
                    {start}
                    <br>

                    📅 <strong>Jusqu'au :</strong>
                    {end}
                </p>

                <p style="
                    margin-top: 20px;
                ">

                    <a
                        href="{url}"
                        style="
                            display: inline-block;
                            padding: 12px 20px;
                            background-color: #0078f2;
                            color: white;
                            text-decoration: none;
                            border-radius: 6px;
                            font-weight: bold;
                        "
                    >
                        🎁 Récupérer le jeu
                    </a>

                </p>

            </div>
            """

        html_body = f"""
        <html>

        <body style="
            font-family: Arial, Helvetica, sans-serif;
            color: #222;
            max-width: 700px;
            margin: auto;
            padding: 20px;
        ">

            <h1 style="
                margin-bottom: 5px;
            ">
                🎮 Jeux gratuits Epic Games
            </h1>

            <p style="
                color: #666;
                font-size: 15px;
                margin-bottom: 30px;
            ">
                Voici les nouveaux jeux actuellement
                gratuits sur l'Epic Games Store.
            </p>

            {game_cards}

            <p style="
                color: #888;
                font-size: 12px;
                margin-top: 30px;
            ">
                🤖 E-mail envoyé automatiquement par
                ton programme Epic Games.
            </p>

        </body>

        </html>
        """

    # ============================================================
    # Création du message
    # ============================================================

    message = MIMEMultipart("alternative")

    message["From"] = EMAIL_FROM
    message["To"] = EMAIL_TO
    message["Subject"] = subject

    # Version texte
    message.attach(
        MIMEText(
            text_body,
            "plain",
            "utf-8",
        )
    )

    # Version HTML
    message.attach(
        MIMEText(
            html_body,
            "html",
            "utf-8",
        )
    )

    # ============================================================
    # Connexion Gmail
    # ============================================================

    print("📧 Connexion à Gmail...")

    with smtplib.SMTP(
        "smtp.gmail.com",
        587,
    ) as server:

        server.starttls()

        server.login(
            EMAIL_FROM,
            EMAIL_PASSWORD,
        )

        server.send_message(message)

    print("📧 E-mail envoyé !")


# ============================================================
# Programme principal
# ============================================================

def main():

    print("=" * 60)
    print("🎮 EPIC GAMES - FREE GAMES")
    print("=" * 60)

    print()
    print("🔎 Recherche des jeux gratuits Epic Games...")

    games = get_free_games()

    print(
        f"🎮 {len(games)} jeu(x) "
        "gratuit(s) trouvé(s)."
    )

    # ============================================================
    # Affichage des jeux trouvés
    # ============================================================

    if games:

        print()
        print("🎁 Jeux gratuits actuellement :")
        print()

        for game in games:

            print(
                f"  - {game['title']}"
            )

            print(
                f"    📅 {game['start']} → "
                f"{game['end']}"
            )

            print(
                f"    🔗 {game['url']}"
            )

            print()

    # ============================================================
    # Historique
    # ============================================================

    seen_games = load_seen_games()

    new_games = []

    for game in games:

        game_id = (
            game["id"]
            or game["title"]
        )

        if game_id not in seen_games:

            new_games.append(game)

    # ============================================================
    # Nouveaux jeux
    # ============================================================

    if new_games:

        print("🆕 Nouveaux jeux :")
        print()

        for game in new_games:
            print(
                f"  - {game['title']}"
            )

    else:

        print(
            "ℹ️ Aucun nouveau jeu."
        )

    # ============================================================
    # Envoi du mail
    # ============================================================

    send_email(new_games)

    # ============================================================
    # Sauvegarde de l'historique
    #
    # IMPORTANT :
    # On sauvegarde uniquement APRÈS l'envoi réussi.
    # ============================================================

    for game in new_games:

        game_id = (
            game["id"]
            or game["title"]
        )

        seen_games.add(game_id)

    save_seen_games(seen_games)

    print("💾 Historique sauvegardé.")

    print()
    print("✅ Terminé !")


if __name__ == "__main__":
    main()
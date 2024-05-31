import logging
import requests
from openai import OpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os
from dotenv import load_dotenv
from datetime import datetime
import locale
import openai

# Configurer le locale en français
try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_TIME, 'fr_FR')

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()
CYKA = os.getenv('CYKA_TOKEN')

# Configurez le journal
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# Définissez les fonctions de gestion des commandes
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Bonjour! Cyka votre parfaite assistante, comment puis-je vous servir?')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Je vais vous aidez\n"
        "Voici la liste des commandes\n"
        "/start pour commencer\n"
        "/help pour obtenir cette aide\n"
        "/info pour en apprendre davantage à mon sujet"
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Je suis une délicieuse esclave prête à vous servir.')


async def cyka(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Blyat !')


async def blyat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Cyka ! tel est mon nom en plus aha <3')


async def sexeanale(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Sexe AnalE ?\nSIIIIIIIIIIIIIIIIIIIIIIIIIIIIII !!!')


async def blague(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = "https://official-joke-api.appspot.com/jokes/random"
    response = requests.get(url)
    if response.status_code == 200:
        joke_data = response.json()
        joke_text = f"{joke_data['setup']} - {joke_data['punchline']}"
        await update.message.reply_text(joke_text)
    else:
        await update.message.reply_text("Désolé, je n'ai pas pu obtenir une blague pour le moment.")


async def trivia(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = "https://uselessfacts.jsph.pl/random.json?language=en"
    response = requests.get(url)
    if response.status_code == 200:
        fact_data = response.json()
        fact_text = fact_data['text']
        await update.message.reply_text(fact_text)
    else:
        await update.message.reply_text("Désolé, je n'ai pas pu obtenir un fait intéressant pour le moment.")


async def jours_feries(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 1:
        await update.message.reply_text("Veuillez fournir une année. Par exemple : /jours_feries 2024")
        return
    annee = context.args[0]
    url = f"https://calendrier.api.gouv.fr/jours-feries/metropole/{annee}.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        jour_ferie_data = response.json()
        jour_ferie_texts = []
        for date, nom in jour_ferie_data.items():
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            date_formatted = date_obj.strftime("%A %d %B %Y").capitalize()
            jour_ferie_texts.append(f"{date_formatted} : {nom}")
        jour_ferie_text = '\n'.join(jour_ferie_texts)
        await update.message.reply_text(jour_ferie_text)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching jours fériés: {e}")
        await update.message.reply_text(f"Désolé, je n'ai pas pu obtenir la liste des jours fériés pour {annee}.")


async def villes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) == 0:
        await update.message.reply_text("Veuillez fournir le nom d'une ville. Par exemple : /villes Reims")
        return

    city_name = ' '.join(context.args)
    url = f"https://geo.api.gouv.fr/communes?nom={city_name}&fields=nom,code,codesPostaux,siren,codeEpci,codeDepartement,codeRegion,population&_limit=5"
    try:
        response = requests.get(url)
        response.raise_for_status()
        city_data = response.json()
        if not city_data:
            await update.message.reply_text(f"Je n'ai trouvé aucune information pour la ville '{city_name}'.")
            return

        city_texts = []
        for city_info in city_data:
            city_text = (
                f"Nom: {city_info['nom']}\n"
                f"Code: {city_info['code']}\n"
                f"Codes Postaux: {', '.join(city_info['codesPostaux'])}\n"
                f"SIREN: {city_info['siren']}\n"
                f"Code EPCI: {city_info['codeEpci']}\n"
                f"Code Département: {city_info['codeDepartement']}\n"
                f"Code Région: {city_info['codeRegion']}\n"
                f"Population: {city_info['population']}\n"
            )
            city_texts.append(city_text)

        await update.message.reply_text('\n\n'.join(city_texts))
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching city information: {e}")
        await update.message.reply_text(f"Désolé, je n'ai pas pu obtenir les informations pour la ville '{city_name}'.")


async def ask_chatgpt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: # Marche pas car payant
    if len(context.args) == 0:
        await update.message.reply_text("Veuillez fournir une question. Par exemple : /gpt Quelle est la capitale de la France ?")
        return

    question = ' '.join(context.args)
    client = OpenAI()
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question}
            ]
        )
        answer = response['choices'][0]['message']['content'].strip()
        await update.message.reply_text(answer)
    except Exception as e:
        logger.error(f"Error fetching response from OpenAI: {e}")
        await update.message.reply_text("Désolé, je n'ai pas pu obtenir une réponse pour votre question.")


# Fonction principale du bot
def main() -> None:
    # Créez l'application avec votre token
    application = ApplicationBuilder().token(CYKA).build()

    # Ajoutez les gestionnaires de commandes
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("info", info))
    application.add_handler(CommandHandler("blyat", blyat))
    application.add_handler(CommandHandler("cyka", cyka))
    application.add_handler(CommandHandler("sexeanale", sexeanale))
    application.add_handler(CommandHandler("blague", blague))
    application.add_handler(CommandHandler("trivia", trivia))
    application.add_handler(CommandHandler("jours_feries", jours_feries))
    application.add_handler(CommandHandler("villes", villes))
    # application.add_handler(CommandHandler("gpt", ask_chatgpt)) il Faut un plan payant

    # Répétez les messages texte
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Démarrez le bot
    application.run_polling()


if __name__ == '__main__':
    main()


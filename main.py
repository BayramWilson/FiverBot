from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, filters
from dotenv import load_dotenv
import os
import logging
from typing import Tuple
import requests

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Dein API-Token von BotFather hier einfügen
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GIG_LINK = "https://www.fiverr.com/fivernoob97/create-custom-telegram-and-whatsapp-bots"
CALENDLY_URL = os.getenv("CALENDLY_URL")
GROK_API_KEY = os.getenv("GROK_API_KEY")
GROK_API_URL = os.getenv("GROK_API_URL")

# Verify environment variables
logging.info(f"GROK_API_KEY: {GROK_API_KEY}")
logging.info(f"GROK_API_URL: {GROK_API_URL}")

# Start-Befehl
async def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("👋 Say Hello", callback_data="hello")],
        [InlineKeyboardButton("ℹ️ About", callback_data="about")],
        [InlineKeyboardButton("📩 Contact", callback_data="contact")],
        
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome! Choose an option:", reply_markup=reply_markup)

async def button(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    if query.data == "hello":
        await query.message.reply_text("Hello! How can I assist you?")
    elif query.data == "about":
        await query.message.reply_text("I am a Fiverr demo bot. I can create custom bots for you!")
    elif query.data == "contact":
        await contact(update, context)
    elif query.data == "gig":
        await gig(update, context)
    elif query.data == "schedule":
        await schedule(update, context)

async def contact(update: Update, context):
    contact_buttons = [
        [InlineKeyboardButton("📩 Message Me on Telegram", url="https://t.me/CryptoFuerAlle")],
        [InlineKeyboardButton("🛒 View My Fiverr Gig", url=GIG_LINK)],
        [InlineKeyboardButton("📅 Schedule Meeting", callback_data="schedule")]
    ]
    reply_markup = InlineKeyboardMarkup(contact_buttons)
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text="How can I assist you? 👇", reply_markup=reply_markup)


# Get my Gig on Fiverr
async def gig(update: Update, context):
  
    message = (
        "🚀 **Telegram & WhatsApp Bot Development** 🚀\n"
        "I build custom bots for automation, customer service, and more! \n\n"
        "✅ Features:\n"
        "- Auto-replies & Commands\n"
        "- Appointment Booking\n"
        "- API Integrations\n"
        "- Custom AI Responses\n\n"
        "💰 Prices start from **$X**\n"
        f"📌 [Click Here to View My Gig]({GIG_LINK})"
    )
    await update.message.reply_text(message, parse_mode="Markdown")

async def schedule(update: Update, context):
    """Send a booking link to the user."""
    keyboard = [[InlineKeyboardButton("📅 Book a Call", url=CALENDLY_URL)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        await update.message.reply_text("Click below to schedule a call:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text("Click below to schedule a call:", reply_markup=reply_markup)

# Function to send the user's message to Grok API and get a response
def get_grok_response(message: str) -> Tuple[str, str]:
    headers = {"Authorization": f"Bearer {GROK_API_KEY}"}
    data = {
        "model": "grok-2-1212",
        "messages": [
            {"role": "user", "content": message}
        ]
    }
    logging.info(f"Sending message to Grok API: {message}")
    response = requests.post(GROK_API_URL, json=data, headers=headers)
    logging.info(f"Grok API response status: {response.status_code}")
    logging.info(f"Grok API response content: {response.content}")
    if response.status_code == 200:
        response_json = response.json()  # Parse the JSON response
        # Extract the assistant's message content and intent
        content = response_json['choices'][0]['message']['content']
        intent = response_json['choices'][0]['message'].get('intent', None)  # Assuming the API returns an intent
        return content, intent
    return "Sorry, I couldn't understand that. Try again!", None

# Function to handle "Hello" or any other message
async def reply_to_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text.lower()
    response_from_grok, intent = get_grok_response(user_message)  # Get response and intent

    # Fallback keyword detection
    if "gig" in user_message or intent == "ask_about_gig":
        await gig(update, context)
    elif "schedule" in user_message or "appointment" in user_message or intent == "schedule_meeting":
        await schedule(update, context)
    elif "contact" in user_message or intent == "contact_info":
        await contact(update, context)
    else:
        # Provide a default response that suggests available commands
        await update.message.reply_text(
            "I'm here to assist you with specific tasks. You can ask about our gig, schedule a meeting, or get contact information."
        )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(CommandHandler("gig", gig))
    app.add_handler(CommandHandler("contact", contact))
    app.add_handler(CommandHandler("schedule", schedule))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_to_message))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
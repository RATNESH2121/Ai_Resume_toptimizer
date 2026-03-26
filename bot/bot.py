"""
Telegram Bot Main Runner.
Run this file directly to start the bot:
  python bot/bot.py
"""

import os
import sys
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resume_optimizer.settings')

from dotenv import load_dotenv
load_dotenv()

import django
django.setup()

from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler, filters
)

from handlers import (
    start, receive_jd, receive_resume, handle_template_choice,
    cancel, help_command, AWAITING_JD, AWAITING_RESUME, AWAITING_TEMPLATE
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token or token == 'your_telegram_bot_token_here':
        print("=" * 50)
        print("❌ TELEGRAM_BOT_TOKEN not set!")
        print("Steps to get it:")
        print("1. Open Telegram → Search @BotFather")
        print("2. Send /newbot")
        print("3. Follow steps → get token")
        print("4. Add token to .env file")
        print("=" * 50)
        return

    print("=" * 50)
    print("🤖 ResumeAI Telegram Bot Starting...")
    print("=" * 50)

    app = Application.builder().token(token).build()

    # Conversation handler for the main flow
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            AWAITING_JD: [
                MessageHandler(filters.Document.ALL | filters.TEXT & ~filters.COMMAND, receive_jd),
            ],
            AWAITING_RESUME: [
                MessageHandler(filters.Document.ALL | filters.TEXT & ~filters.COMMAND, receive_resume),
            ],
            AWAITING_TEMPLATE: [
                CallbackQueryHandler(handle_template_choice),
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            CommandHandler('start', start),
        ],
        allow_reentry=True,
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('cancel', cancel))

    print("✅ Bot is running! Open Telegram and search for your bot.")
    print("Press Ctrl+C to stop.\n")

    app.run_polling(drop_pending_updates=True)


if __name__ == '__main__':
    main()

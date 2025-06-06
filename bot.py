import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import TOKEN, GALACTUS_PATTERN
from utils.files import load_chat_ids, load_last_updated_date
from handlers.commands import start, decks, spotlight
from handlers.events import welcome_user, user_left_group
from handlers.messages import galactus_reply, edited_message_handler
from handlers.keywords import daily_curse_by_galactus
from jobs.updater import check_for_update
from jobs.scheduler import schedule_link_jobs_for_all_chats
from config import DATA_DIR

logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def init_data_directory():
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Diretório de dados verificado/criado em: {DATA_DIR}")
    except Exception as e:
        logger.error(f"Não foi possível criar o diretório de dados em {DATA_DIR}: {e}")
        # Você pode decidir se quer sair do bot aqui ou tentar continuar


def main():
    init_data_directory()
    load_last_updated_date()
    load_chat_ids()

    app = Application.builder().token(TOKEN).build()

    # comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("decks", decks))
    app.add_handler(CommandHandler("spotlight", spotlight))

    # mensagens e menções
    app.add_handler(
        MessageHandler(
            filters.TEXT & filters.Regex(GALACTUS_PATTERN), daily_curse_by_galactus
        )
    )
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, galactus_reply))
    app.add_handler(
        MessageHandler(filters.UpdateType.EDITED_MESSAGE, edited_message_handler)
    )

    # eventos do grupo
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_user))
    app.add_handler(
        MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, user_left_group)
    )

    # jobs
    app.job_queue.run_repeating(check_for_update, interval=1800, first=10)
    schedule_link_jobs_for_all_chats(app.job_queue)

    app.run_polling()


if __name__ == "__main__":
    main()

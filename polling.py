import os
import time
import structlog
from scryfall_telegram.logging import setup_logging
from scryfall_telegram.telegram.client import cached_telegram_client
from scryfall_telegram.callback import handle_callback_query
from scryfall_telegram.inline import handle_inline_query
from scryfall_telegram.textmessage import handle_message

setup_logging()
log = structlog.get_logger()

def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")

    client = cached_telegram_client()
    
    log.info("Removing previous webhook...")
    try:
        client._post("/setWebhook", {"url": ""})
    except Exception as e:
        log.warn("Could not remove webhook", error=str(e))

    log.info("Starting bot in polling mode...")
    offset = 0
    while True:
        try:
            resp = client._post("/getUpdates", {"offset": offset, "timeout": 30})
            if resp.status_code == 200:
                updates = resp.json().get("result", [])
                for update in updates:
                    offset = update["update_id"] + 1
                    
                    if callback_query := update.get("callback_query"):
                        log.debug("callback_query", query=callback_query)
                        handle_callback_query(callback_query)
                    
                    if inline_query := update.get("inline_query"):
                        log.debug("inline_query", query=inline_query)
                        handle_inline_query(inline_query)
                    
                    if msg := update.get("message"):
                        log.debug("message", message=msg)
                        handle_message(msg)
                    
                    if channel_msg := update.get("channel_post"):
                        log.debug("channel_post", message=channel_msg)
                        handle_message(channel_msg)
            else:
                log.error("Error fetching updates", status_code=resp.status_code, text=resp.text)
                time.sleep(5)
        except Exception as e:
            log.exception("Error in polling loop", error=str(e))
            time.sleep(5)

if __name__ == "__main__":
    main()

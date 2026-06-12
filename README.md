# Scryfall Telegram

Scryfall telegram is both an inline and always-on [Telegram](https://telegram.org/)
bot that uses [Scryfall](https://scryfall.com/)'s API to search
Magic: The Gathering cards.

All Scryfall syntax that can be understood by the API can be used in inline mode.
A full reference can be found here: [Scryfall Syntax Reference](https://scryfall.com/docs/reference).

For always-on mode, add [ScryfallBot](https://t.me/ScryfallBot) to your chat and
mark cards to be looked up with `[[ card you want to find ]]`. The bot will
search up to 10 cards per message. You can find a specific printing or limit the
search to a specific set by adding the 3 letter set code like this:
`[[ my card | SET ]]`. Starting the query with a '$' or '€' sign will make the bot
include pricing information in the image caption: `[[ $ nyx-fleece ram ]]`

NOTE: Currently, the bot needs to be an admin in your chat in order to see
messages without being explicitly mentioned...

Some inline examples:

- Search a card by name: `@ScryfallBot Bolas`
- Search an instant that can be played in an Esper EDH deck:
  `@ScryfallBot id<=esper t:instant`
- Search cards that enter the battlefield tapped:
  `@ScryfallBot o:"~ enters the battlefield tapped"`

Some always-on examples:

- Does anyone have an extra [[ nyx fleece ram ]] or [[ bolas dragon god ]] ?
- Which is best: [[Bottle Gnomes|TMP]] or [[Bottle Gnomes]] ?
- How expensive is this invocation? [[ $ Damnation | MP2 ]]

## Running it yourself

This bot lives on Telegram: [t.me/ScryfallBot](https://t.me/ScryfallBot)
(Beta version: [t.me/ScryfallBetaBot](https://t.me/ScryfallBetaBot) ),
but you can easily run a copy of it yourself:

### Requirements

- Python
- [uv](https://docs.astral.sh/uv/) and [poethepoet](https://poethepoet.natn.io/)
- A Scaleway account and project

### Building

- Ensure these variables are in your environment:
  - `SCW_ACCESS_KEY` and `SCW_SECRET_KEY`: Your Scaleway API keys.
- Fill in some variables in `terraform/prod.tfvars`:

```
zone               = "fr-par-1"
region             = "fr-par"
project_id         = "..."
telegram_bot_token = "..."
```

- Run `poe deploy` to build and deploy.
- You're live!

### Development

This project uses [uv](https://docs.astral.sh/uv/) and
[poethepoet](https://poethepoet.natn.io/) for almost everything:

- `uv sync`
- `poe lint`
- `poe test`
- `poe deploy`

### Running Locally (Polling Mode)

If you want to run the bot locally or on a VPS (e.g. Railway) without setting up Scaleway serverless webhooks, you can use the polling mode script:

1. Set the `TELEGRAM_BOT_TOKEN` environment variable.
2. Run the polling script:

   ```bash
   ENV=stag TELEGRAM_BOT_TOKEN="your_bot_token" uv run python polling.py
   ```

### UTILS COMMANDS FOR TEST

- Telegram bot info

<https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getWebhookInfo>

- Set telegram bot service url

<https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook?url={SERVICE_URL}>

- Reset telegram bot service url

<https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook?url=>

- Send test message

curl -X POST "<https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage>" \
     -d "chat_id={CHAT_ID}" \
     -d "text=test message"

- Send query to serverless service

curl -X POST "{SERVICE_URL}" -H "Content-Type: application/json" -d "{\"update_id\":123456789,\"message\":{\"message_id\":1,\"from\":{\"id\":2047430,\"is_bot\":false,\"first_name\":\"Ruben\",\"last_name\":\"Sierra\",\"username\":\"maguilag\"},\"chat\":{\"id\":2047430,\"first_name\":\"Ruben\",\"last_name\":\"Sierra\",\"username\":\"maguilag\",\"type\":\"private\"},\"date\":1610000000,\"text\":\"[[ Black Lotus ]]\"}}"

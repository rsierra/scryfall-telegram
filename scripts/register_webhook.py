#!/usr/bin/env python3
import argparse
import os
import subprocess

import requests


def main():
    parser = argparse.ArgumentParser(description="Register a webhook for your bot")
    parser.add_argument(
        "env",
        choices=["stag", "prod"],
        help="The stage to register the webhook for",
    )
    parser.add_argument(
        "--url",
        help="The URL to register as webhook. If not passed, will be fetched from Terraform outputs.",
    )
    args = parser.parse_args()

    env = args.env

    if args.url:
        url = args.url
    else:
        url = subprocess.check_output(
            ["terraform", "output", "-raw", f"-state={env}.tfstate", "function_url"],
            cwd="terraform",
            text=True,
        )

    if not url.startswith("https://"):
        url = "https://" + url

    try:
        bot_token = os.environ[f"TELEGRAM_BOT_TOKEN_{env.upper()}"]
    except KeyError:
        raise ValueError(
            f"Could not find TELEGRAM_BOT_TOKEN_{env.upper()} in environment"
        )

    print(f"Register webhook: {url}", end="\r")
    resp = requests.post(
        f"https://api.telegram.org/bot{bot_token}/setWebhook", json={"url": url}
    )
    resp.raise_for_status()
    print(f"[OK] Registered webhook: {url}")


if __name__ == "__main__":
    main()

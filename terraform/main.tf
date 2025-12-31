terraform {
  required_version = ">= 0.13"

  required_providers {
    archive = {
      source  = "hashicorp/archive"
      version = "2.7.1"
    }
    null = {
      source  = "hashicorp/null"
      version = "3.2.4"
    }
    scaleway = {
      source  = "scaleway/scaleway"
      version = "2.65.1"
    }
  }
}

provider "scaleway" {
  zone       = var.zone
  region     = var.region
  project_id = var.project_id
}

locals {
  proj_root = "${path.root}/../"
  build_dir = "${local.proj_root}/.build/"
}

resource "null_resource" "build_package" {
  triggers = {
    source_hash = sha1(
      join("", [
        for f in fileset("${local.proj_root}/scryfall_telegram", "**.py") :
        filesha1("${local.proj_root}/scryfall_telegram/${f}")
        ]
    )),
    proj_hash = filesha1("${local.proj_root}/pyproject.toml")
    req_hash  = filesha1("${local.proj_root}/uv.lock")
  }

  provisioner "local-exec" {
    command = "poe package"
  }
}


data "archive_file" "source_zip" {
  type       = "zip"
  source_dir = local.build_dir
  excludes   = ["**/__pycache__"]

  output_path = "${path.module}/build/function.zip"

  depends_on = [null_resource.build_package]
}

resource "scaleway_function_namespace" "webhook" {
  name        = "scryfall-telegram-${var.env}"
  description = "Scryfall Telegram webhook handler for ${var.env}"
}

resource "scaleway_function" "webhook" {
  namespace_id = scaleway_function_namespace.webhook.id
  name         = "scryfall-telegram-webhook-${var.env}"
  description  = "Webhook handler for Scryfall Telegram."
  tags         = ["env-${var.env}"]

  runtime      = "python313"
  handler      = "scryfall_telegram/handler.handle_telegram_webhook"
  privacy      = "public"
  http_option  = "redirected"
  memory_limit = 128
  timeout      = 25
  min_scale    = 0
  max_scale    = 10

  zip_file = data.archive_file.source_zip.output_path
  zip_hash = data.archive_file.source_zip.output_base64sha256
  deploy   = true

  environment_variables = {
    ENV = var.env,
  }
  secret_environment_variables = {
    TELEGRAM_BOT_TOKEN = var.telegram_bot_token
  }
}

output "function_url" {
  description = "Invocation URL of the Telegram webhook handler."
  value       = scaleway_function.webhook.domain_name
}


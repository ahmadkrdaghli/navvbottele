keep_alive()

app.run_webhook(
    listen="0.0.0.0",
    port=8080,
    url_path=TELEGRAM_TOKEN,
    webhook_url=f"https://your-app-name.codecapsules.io/{TELEGRAM_TOKEN}"
)

# ctfd-discord-webhook-plugin

Discord webhook plugin for CTFd to announce challenge solves! Can be configured with a custom message, and a limit to only announce the first N solves.

The webhook are called only when the CTF is started. Don't attempt to test as an admin if the CTF is not started: the webhook will not be triggered.

Functionality made for UIUCTF 2020

Notifications are best-effort and never wait for Discord in a CTFd request. Each
worker process has one lazy daemon sender and a queue of at most 128 pending
messages. A full queue drops the new notification; worker exit loses pending
messages. Connect/read timeouts are 3.05/5 seconds, with no redirects, response-body
download or retries. Failures are logged without webhook URLs/tokens. The same
bounded sender handles solve, challenge-update and flag-sharing messages.

Local transport tests (no Discord calls): `python -m unittest discover -s tests`.

## Setup
1. Clone this repo into a folder in the plugin folder of your CTFd
2. Create a new Webhook in your discord server
3. Set the appropriate `DISCORD_WEBHOOK_URL`, `DISCORD_WEBHOOK_LIMIT`, `DISCORD_WEBHOOK_MESSAGE` environment variables or edit the `config.py` file.
4. Optional: `DISCORD_WEBHOOK_JAIL_FLAGS=true` also posts flag sharing caught by the `jail_flags` plugin (a team solving with a jail or instance flag of another team; the player is not told). Off by default. `DISCORD_WEBHOOK_JAIL_FLAGS_URL` sends them to another webhook (e.g. a private admin channel) instead of `DISCORD_WEBHOOK_URL`.

If you are using docker-compose to deploy ctfd, I recommend setting the env variables within your docker-compose.yml file. Run `docker-compose build` and `docker-compose up` to rebuild and relaunch ctfd w/ the plugin included.


![preview](./discord-webhook-preview.png)

from os import environ


def _bool(name, default):
    """An on/off setting: 1, true, yes or on (any case) is on, anything else set is off."""
    value = environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def config(app):
    """
    Discord webhook URL to send data to. Set to None to disable plugin entirely.
    """
    app.config["DISCORD_WEBHOOK_URL"] = environ.get("DISCORD_WEBHOOK_URL")

    """
    Limit on number of solves for challenge to trigger webhook for. Set to 0 to send a message for every solve.
    """
    app.config["DISCORD_WEBHOOK_LIMIT"] = environ.get("DISCORD_WEBHOOK_LIMIT", "3")

    """
    Webhook flag submission format string. Valid vars: team, user, solves, fsolves (formatted solves), challenge, category, team_id, user_id, challenge_slug, value
    """
    app.config["DISCORD_WEBHOOK_MESSAGE"] = environ.get(
        "DISCORD_WEBHOOK_MESSAGE",
        "Congratulations to team {team} for the {fsolves} solve on challenge {challenge}!",
    )
    app.config["DISCORD_WEBHOOK_MESSAGE"] = (
        "{'🩸 FIRST BYTE' if data.solves == 1 else f'{data.fsolves} byte'} for `{data.user}` on `{data.challenge}`"
    )
    """
    Post webhook message when challenge is changed (published, hidden or updated)
    """
    app.config["DISCORD_WEBHOOK_CHALL"] = _bool("DISCORD_WEBHOOK_CHALL", True)

    """
    Post webhook message when challenge is updated (otherwise only published or hidden)
    """
    app.config["DISCORD_WEBHOOK_CHALL_UPDATE"] = _bool("DISCORD_WEBHOOK_CHALL_UPDATE", False)

    """
    Post webhook message even if challenge has not yet been published (only relevant when update is enabled)
    """
    app.config["DISCORD_WEBHOOK_CHALL_UNPUBLISHED"] = _bool("DISCORD_WEBHOOK_CHALL_UNPUBLISHED", False)

    """
    Webhook challenge change format string. Valid vars: challenge, category, action (published, hidden or updated)
    """
    app.config["DISCORD_WEBHOOK_CHALL_MESSAGE"] = environ.get(
        "DISCORD_WEBHOOK_CHALL_MESSAGE",
        "Challenge {challenge} ({category}) has been {action}!",
    )

    """
    Turning this on turns your DISCORD_WEBHOOK_CHALL_MESSAGE into a f-string. Values can be accessed with data.<field>

    This allows conditional formatting: e.g. {'FIRST BLOOD' if data.solves == 1 else ''}
    """
    app.config["DISCORD_WEBHOOK_FSTRING"] = _bool("DISCORD_WEBHOOK_FSTRING", False)

    """
    Post flag sharing caught by the jail_flags plugin (a team solving with a jail or instance flag of another team; the player is not told).
    Off by default: DISCORD_WEBHOOK_URL is usually a public channel, and the sharing team would learn it was caught.
    """
    app.config["DISCORD_WEBHOOK_JAIL_FLAGS"] = _bool("DISCORD_WEBHOOK_JAIL_FLAGS", False)

    """
    Webhook URL for the flag sharing alerts, e.g. a private admin channel. Unset: DISCORD_WEBHOOK_URL.
    """
    app.config["DISCORD_WEBHOOK_JAIL_FLAGS_URL"] = (
        environ.get("DISCORD_WEBHOOK_JAIL_FLAGS_URL")
        or app.config["DISCORD_WEBHOOK_URL"]
    )

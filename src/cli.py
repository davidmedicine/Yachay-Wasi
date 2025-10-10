import click

from .db import init_db, enqueue_message
from .config import load_config
from .utils import normalize_msisdn, hash_identifier
from .consent import set_consent
from .queue import send_sms_via_gammu


@click.group()
def cli():
    pass


@cli.command("init-db")
def cmd_init_db():
    init_db()
    click.echo("DB initialized.")


@cli.command("grant")
@click.option("--msisdn", required=True, help="MSISDN like +51999999999")
@click.option("--actor", default="individual", show_default=True)
@click.option("--reason", default=None)
def cmd_grant(msisdn, actor, reason):
    set_consent(msisdn, "granted", actor=actor, reason=reason)
    click.echo("Consent granted.")


@cli.command("revoke")
@click.option("--msisdn", required=True)
@click.option("--actor", default="individual", show_default=True)
@click.option("--reason", default=None)
def cmd_revoke(msisdn, actor, reason):
    set_consent(msisdn, "revoked", actor=actor, reason=reason)
    click.echo("Consent revoked.")


@cli.command("send")
@click.option("--to", "to_msisdn", required=True)
@click.option("--text", required=True)
@click.option("--ttl", default=None, type=int)
def cmd_send(to_msisdn, text, ttl):
    cfg = load_config()
    ttl = ttl or cfg["policy"]["default_ttl"]
    normalize_msisdn(to_msisdn)
    ok = send_sms_via_gammu(to_msisdn, text)
    sender_hash = hash_identifier(cfg["sms"]["sender_label"])
    recipient_hash = hash_identifier(to_msisdn)
    message_id = enqueue_message(
        "out",
        "sms",
        sender_hash,
        recipient_hash,
        text,
        ttl,
        state="delivered" if ok else "error",
    )
    click.echo(f"Sent={ok} message_id={message_id}")


if __name__ == "__main__":
    cli()

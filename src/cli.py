import click

from .db import (
    init_db,
    get_subscriber_hashes_by_topic,
    enqueue_message,
    update_message_state,
    log_action,
    set_community_consent,
)
from .config import load_config
from .utils import hash_identifier
from .queue import send_sms_via_gammu
from .phonebook import resolve_msisdns


@click.group()
def cli():
    pass


@cli.command("init-db")
def cmd_init_db():
    init_db()
    click.echo("DB initialized.")


@cli.command("community-consent")
@click.option("--status", type=click.Choice(["granted", "revoked"]), required=True)
@click.option("--reason", default="", help="Reason or reference, e.g., 'Asamblea 2025-10-25'")
def cmd_community_consent(status, reason):
    set_community_consent(status, reason or None)
    click.echo(f"Community consent recorded: {status} ({reason})")


@cli.command("broadcast")
@click.option("--topic", type=click.Choice(["salud", "precio", "comunidad"]), required=True)
@click.option("--text", required=True)
def cmd_broadcast(topic, text):
    cfg = load_config()
    ttl = cfg["policy"]["default_ttl"]
    sender_hash = hash_identifier(cfg["sms"]["sender_label"])

    hashes = get_subscriber_hashes_by_topic(topic)
    if not hashes:
        click.echo(f"No subscribers for topic '{topic}'.")
        return

    mapping = resolve_msisdns(hashes)
    resolved = list(mapping.items())
    unresolved = set(hashes) - set(mapping.keys())

    sent_ok = 0
    sent_fail = 0

    for h, msisdn in resolved:
        mid = enqueue_message("out", "sms", sender_hash, h, text, ttl, state="queued")
        ok = send_sms_via_gammu(msisdn, text)
        update_message_state(mid, "delivered" if ok else "error")
        log_action(mid, "broadcast", "ok" if ok else "error", notes=f"topic={topic}")
        if ok:
            sent_ok += 1
        else:
            sent_fail += 1

    click.echo(
        f"Broadcast '{topic}': total={len(hashes)} resolved={len(resolved)} sent_ok={sent_ok} sent_fail={sent_fail} unresolved={len(unresolved)}"
    )


if __name__ == "__main__":
    cli()

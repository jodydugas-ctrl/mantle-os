#!/usr/bin/env python3
"""A deliberately ordinary little notes app -- the assimilation dry-run target.

It has (unlabeled) organs: a main loop (Heart), input handlers (Senses), an outbound
notifier (Limbs), state + persistence (Memory), validation and an auth check (Immune),
and one "smart suggestion" judgment point (a Brain affordance, dormant).

Run the read-only dissection against it:
    python -m mantle assimilate examples/sample_app --dry-run
"""
import json
import os
import time

NOTES = {}
CONFIG = {"api_key": "sk-EXAMPLEEXAMPLEEXAMPLE", "store": "notes.json"}


# --- immune-ish tissue -------------------------------------------------------
def validate_note(text):
    """Reject empty or oversized notes."""
    return bool(text) and len(text) < 10_000


def check_auth_token(token):
    """Compare a presented token against the configured secret."""
    return token == CONFIG["api_key"]


# --- memory tissue -----------------------------------------------------------
def set_note(note_id, text):
    """Mutate in-memory state."""
    NOTES[note_id] = {"text": text, "ts": time.time()}


def save_notes():
    """Persist state to disk."""
    with open(CONFIG["store"], "w") as f:
        json.dump(NOTES, f)


# --- senses tissue -----------------------------------------------------------
def handle_create_note(request):
    """An inbound request arrives."""
    if not validate_note(request.get("text", "")):
        return {"ok": False}
    set_note(request["id"], request["text"])
    return {"ok": True}


def on_timer_tick(now):
    """A scheduled trigger."""
    return {"tick": now}


# --- limbs tissue --------------------------------------------------------------
def send_notification(user, message):
    """Call an external service (an effect on the world)."""
    # import requests; requests.post("https://notify.example/api", ...)
    return {"sent_to": user, "message": message}


def render_note_list():
    """Human-visible output."""
    for nid, n in NOTES.items():
        print("note %s: %s" % (nid, n["text"][:40]))


# --- a dormant brain affordance ---------------------------------------------------
def suggest_tags_with_llm(text):
    """A judgment point: would call a model. Dormant until Phase 2."""
    return ["todo"]  # placeholder; an LLM call would live here


# --- the heart -----------------------------------------------------------------
def main_loop():
    """The pulse of the app."""
    for i in range(3):
        on_timer_tick(time.time())
        time.sleep(0.01)


if __name__ == "__main__":
    handle_create_note({"id": "n1", "text": "water the plants"})
    render_note_list()
    main_loop()
    save_notes()
    os.remove(CONFIG["store"])

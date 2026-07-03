# Shift.Companion.AppAI

A Mantle OS example AppAI born wearing a small web applet face.

`Shift.Companion.AppAI` is a local-first shift board for handoff reminders. It stores items in browser `localStorage`, exports a plain-text handoff list, and is intentionally **not** clinical decision support: it does not diagnose, prescribe, prioritize care, or replace professional judgment.

## Try the web applet directly

Open the static face in a browser:

```bash
python -m http.server 8765 --directory examples/web_appai_shift_companion
```

Then visit `http://localhost:8765`.

## Hatch it as a Mantle AppAI

From the repository root:

```bash
pip install -e .
python -m mantle hatch examples/eggs/shift_companion.json --out=nest-shift-companion
python -m mantle doctor nest-shift-companion
python -m mantle face-list nest-shift-companion
python -m mantle face-wear nest-shift-companion origin
```

The egg's `face.source` is the same applet HTML stored in `index.html`, sealed into the VCW as the organism's default `origin` phenotype at hatch.

## What this demonstrates

- A whole AppAI declared as one egg.
- A real HTML origin face born with the organism.
- Controls mapped into the Human Surface Map: `task_form`, `task_list`, `handoff_export`, and `clear_done`.
- A tiny calcified Body instinct: `handoff_line(room, need)`.
- Safety posture: local notes only, no clinical advice, no network calls.

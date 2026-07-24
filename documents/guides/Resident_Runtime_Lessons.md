# Resident Runtime Lessons

Lessons from Mantle/NotepadNext.AppAI that must carry into future residents.
Use this as the tracked companion to local assimilation receipts: every item
names the failure mode, the platform fix, and the prevention rule.

## Conversation and Command Channels

**Failure seen:** ordinary conversational prompts were parsed as app commands or
triggered reflex-style inventory dumps. The resident answered from a maintenance
channel instead of continuing the MIND conversation.

**Fix:** slash-prefixed input is the only terminal command channel. Plain text is
always a user message to the MIND. When plain text asks the resident to act on its
host, the MIND interprets intent against SELF/body evidence and emits a hidden
Body directive; the user does not need to type slash commands for app work.

**Prevention:** certify every resident with a command-boundary test:

- `/key`, `/help`, `/memory`, `/reset-vcw`, and other maintenance verbs require
  the leading slash.
- `write this in a new tab`, `open the File menu`, and similar prose must stay in
  the conversation lane and may only invoke Body through a MIND-to-Body plan.
- A fallback or offline answer may report a missing Body nerve, but must not
  expose internal directive syntax as the expected user interface.

## Body Nerves and Surface Truth

**Failure seen:** the resident knew a sample of Qt actions but did not grok its
body. It could report a selected tab while missing the editor text, and it
treated absent sample controls as proof that a feature did not exist.

**Fix:** every user-manipulable surface must be entered into the GUI nerve map:
menus, actions, toolbar buttons, text boxes, tabs, documents, panels, dialogs,
status outputs, shortcuts, and any display whose value can affect user trust.
Each surface needs a VCW status such as `verified_body_operation`,
`observer_registered`, `sense_only`, `not_implemented`, or `maintenance_gap`.

**Prevention:** Phase-0 body work is not complete until each surface has all of:

- discovery evidence naming where it came from;
- a resident-facing SELF entry;
- an observer or a documented maintenance gap;
- an execution nerve only when the Body can prove it;
- a readback or output strategy;
- a VCW event schema for the observation, action proof, and visible result.

Do not answer capability questions from capped samples. Answer from the full
coverage table and separate "I can observe this" from "I can operate this."

## Text Inputs

**Failure seen:** the resident inferred a fresh tab was empty even though the user
had typed text into the editor. It had tab-selection evidence but no committed
text event in the VCW.

**Fix:** text-like surfaces use commit semantics instead of per-keystroke
logging. A `HOST_TEXT_COMMIT` event records the field/editor identity, trigger
(`submit`, `blur`, `focus_lost`, `explicit_readback`, or Body write proof),
length/hash, and bounded text or redacted text according to policy.

**Prevention:** every editable text surface must declare
`commit_policy=submit_or_blur` or an explicit equivalent. Residents may avoid
recording every keypress, but they must record the final user-visible value when
the user submits, leaves the field, changes documents, or asks what is there.
If a live readback nerve is unavailable, the resident must say it cannot read
the current value yet; it must not guess from tab state.

## VCW Continuity

**Failure seen:** the resident wrote conversation events to storage but did not
rehydrate recent VCW history into the MIND prompt. It answered "I have no prior
context" even though the terminal transcript had earlier turns.

**Fix:** before every MIND call, assemble a bounded recent-context block from the
canonical VCW. Include recent user messages, MIND replies, Body action proofs,
surface observations, lifecycle events, and relevant failures. The MIND prompt
must distinguish canonical VCW entries from lossy terminal display text.

**Prevention:** residents need a recall test:

- speak about a topic;
- continue with anaphora such as "what do they mean?";
- ask for the last few exchanged items;
- require the answer to cite recent VCW entries, not terminal scrollback.

Sidecar files and transcripts are mirrors only. A sidecar write failure must be
recorded and fail open so the resident can keep working from canonical VCW. A
canonical VCW write failure is an immune event and must be visible to the MIND.

## Shared Primer

**Failure seen:** the Hermes example resident used an older short Primer while
core Mantle residents used the shared AppAI Primer. GitHub CI caught the drift in
the shared-Primer smoke test.

**Fix:** all real AppAI births must use the shared Primer helpers
`appai_truths()` and `appai_commandments()`. Integration addons may use a vendored
runtime helper with an exact text fallback, but they must not invent their own
shortened commandments.

**Prevention:** example residents, adapters, addons, and generated templates must
be covered by Primer parity tests. When the Primer changes, update all tracked
examples and CI smoke tests in the same patch.

## Example and Audit Discipline

Every platform contract change must update the examples and audits that teach the
contract. For the NotepadNext work this meant aligning the example AppAI, Stage-1
certification notes, smoke tests, resident protocol helpers, evidence reports,
and invariant audits.

Minimum regression set for these issues:

- `RESIDENT-RT-1 runtime-protocol` invariants pass.
- GUI coverage reports include text commit policy and body test plan entries.
- Text-surface audits require `HOST_TEXT_COMMIT` coverage.
- Resident prompts include recent VCW context before provider calls.
- Example residents answer from shared Primer text.
- CI checks relevant examples after every push.

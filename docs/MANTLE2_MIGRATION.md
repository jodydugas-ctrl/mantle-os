# MantleOS 2.0 local migration guide

This branch is a deliberately breaking `2.0.0rc1` candidate. It is local-only and
does not replace historical residents or lifecycle evidence.

## Resident protocol

Maintained residents declare `mantle-resident-v2`. Plain text is conversation input;
slash commands are Body maintenance. Canonical commands are `/key`, `/model` (with
`/mind` as an alias), `/offline`, `/status`, `/help`, `/provider-test`, `/evidence`,
and `/quit`. Host integrations may register extensions but cannot redefine these
commands. Every successful configuration mutation emits `BODY_CONFIGURATION_CHANGED`.

## Evidence and authority

Use `mantle.contracts` for claims and answers. Verified claims require an
`EvidenceRef`; user statements, model interpretations, and proposals retain their
own statuses. Historical certification is not current runtime authority. Spore
inspection is safe and inert by default:

```text
python -m mantle spore inspect <spore.png>
python -m mantle spore inspect <spore.png> --include-conversation
```

External hatch/graft activation must use a fresh target-bound
`LifecycleAuthorization`; SELF-vault reconstruction retains its Body-owned recovery
birthright. Genesis keys remain independently minted and are never derived from a
spore.

The CLI makes the approval explicit and one-shot:

```text
python -m mantle lifecycle authorize hatch seed.png new-nest --approve --out=hatch-auth.json
python -m mantle hatch seed.png --out=new-nest --auth=hatch-auth.json

python -m mantle lifecycle authorize graft patch.png workspace/host --approve --out=graft-auth.json
python -m mantle graft patch.png host --workspace=workspace --auth=graft-auth.json
```

Authorization binds the action, artifact SHA-256, normalized target, expiry, and
nonce. Mantle validates and consumes it before target creation, builds in a unique
same-parent staging directory, writes a phase journal, verifies Stage 1 and required
artifacts, then atomically promotes. Interrupted staging remains inspectable with
`mantle lifecycle status` and can be moved aside with `mantle lifecycle quarantine`.

The shared native scanner now covers conservative C/C++ declarations and bodies,
constructor initializer lists, balanced Qt connects and helper-wired actions, Qt UI
widgets/actions/connections, QRC resources, CMake targets/sources, and Rust fallback
structure. Every fallback emits `mantle-host-evidence-v3` coverage and parser gaps.

## Compatibility

Legacy germs/residents remain inspectable and must be explicitly migrated before a
Mantle 2 certification claim. The Spore-PNG carrier remains format v2; germ, host
evidence, GUI coverage, lifecycle authorization, and resident protocol schemas carry
their own versions.

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

## Compatibility

Legacy germs/residents remain inspectable and must be explicitly migrated before a
Mantle 2 certification claim. The Spore-PNG carrier remains format v2; germ, host
evidence, GUI coverage, lifecycle authorization, and resident protocol schemas carry
their own versions.


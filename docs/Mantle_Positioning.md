# Mantle OS Positioning

Non-normative on-ramp. The canonical doctrine lives in [`../documents/PRIMER.md`](../documents/PRIMER.md),
and the source-backed engineering map lives in
[`../documents/Mantle_for_Engineers.md`](../documents/Mantle_for_Engineers.md).

Mantle OS is a framework for installing an autonomic nervous system and brainstem into a
software or hardware container. That container becomes the Body of a virtual bio-robotic
agent: it can perceive inputs, react through deterministic reflexes, record experience,
protect its state, act through bounded outputs, and later accept a contained reasoning
layer.

The VCW cube is the durable nervous-memory substrate. It does not have to live in a
traditional app server. A smart-home Body can keep its VCW on a Raspberry Pi embedded in a
wall; a desktop app can keep it beside the executable; a cloud service can keep it in cloud
storage. The requirement is not a specific language or host. The requirement is a container
that can persist the VCW and expose clear input/output boundaries.

Mantle is built Body first, MIND second:

- **Body:** deterministic runtime. It runs without model calls, records state append-only,
  and must pass the audit gates before cognition is considered.
- **MIND:** optional LLM-backed cognition. It receives assembled context, writes only to its
  bounded cognition surface, and proposes actions. The Body still applies, verifies, and
  records effects.

This is why the organic language is intentional. It names engineering boundaries:

- **Senses** are the only inbound boundary.
- **Limbs** are the only outbound boundary.
- **Immune** is the failure and integrity boundary.
- **Heart** is the deterministic pulse.
- **Brain/MIND** is optional cognition, added only after the Body is proven.
- **VCW** is the append-only memory substrate.

For a plain-language introduction, read [`../documents/PRIMER.md`](../documents/PRIMER.md).
For engineers and AI agents, read
[`../documents/Mantle_for_Engineers.md`](../documents/Mantle_for_Engineers.md).

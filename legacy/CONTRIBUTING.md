# Contributing to Mantle OS

Thanks for your interest in Mantle OS. This project is published as an open demonstration of an
alternative coding structure, and contributions — from typo fixes to deep critiques of the
architecture — are welcome.

## Ways to contribute

- **Ask questions or discuss the ideas.** Open an issue. "Why is it built this way?" is a valid
  issue. The philosophy is meant to be examined.
- **Report problems.** If something in the `examples/vcw/` substrate doesn't run, or a document
  contradicts the code, open an issue describing what you expected and what happened.
- **Improve the docs.** Clarity fixes, examples, and diagrams are valuable.
- **Extend the substrate.** New organs, drivers, or examples that respect the framework's rules.

## Ground rules for code changes

Mantle has a small number of load-bearing principles. Changes should respect them:

1. **Body before brain.** Anything that *can* be a deterministic reflex *must* be a reflex, living
   in the Body. The MIND (LLM) is for judgment and voice — never for plumbing.
2. **The cube is the single source of truth.** Durable state lives in the VCW cube, addressed
   through bands. No hidden parallel stores or shared globals.
3. **Memory is append-only.** Never rewrite the past — append, tombstone (retire), or quarantine
   (isolate).
4. **Everything is provable.** Every organ carries audit obligations. If you add an organ or
   reflex, state how the Stage 1 / Stage 2 audit checks it.
5. **Fail open, never fail silent.** Instrumentation must not crash the host, but it must not hide
   a problem either.

## Before you open a pull request

- Run the substrate audit and invariants from the `examples/vcw/` directory:

  ```bash
  cd vcw
  python audit.py
  python test_invariants.py
  ```

- Make sure `python audit.py` still reports the **Stage 1 gate passed** (no open hard-fails).
- Keep Phase 1 brain-free: Phase-1 organs must not depend on an LLM to function.

## Style

- Match the existing code style in `examples/vcw/`.
- Keep documents in the established voice and reading order. If you add a document, link it from
  the README and the Primer's document set.

## License

By contributing, you agree that your contributions will be licensed under the project's
[MIT License](LICENSE).

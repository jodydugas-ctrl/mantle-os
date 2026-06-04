#!/usr/bin/env python3
"""
__main__.py  --  One command to see the whole organism (Mantle v2.3)

    python -m vcw demo        # the narrated Phase-1 tour (genesis -> sense -> reflex ->
                              #   learn -> rebirth -> persist), no network/LLM
    python -m vcw audit       # the Stage-1 Zombie Body audit (substrate + runnable Body)
    python -m vcw prove       # the security invariants (red/green)
    python -m vcw mind        # the narrated Phase-2 tour: fuse a bounded MIND (offline stub)
    python -m vcw audit-mind  # the Stage-2 audit: MIND containment + Phase-1 regression
    python -m vcw tour        # the base-cube lifecycle tour

The vcw modules use sibling imports (e.g. `from lineage import ...`), so this entry puts the
package directory on sys.path first -- which is exactly the import-compatibility idiom the
framework asks for: the Body runs whether launched as a module or a script.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_USAGE = "usage: python -m vcw [demo|audit|prove|mind|audit-mind|tour]"


def main(argv):
    cmd = argv[0] if argv else "demo"
    if cmd == "demo":
        import examples_boot
        examples_boot.main()
        return 0
    if cmd == "audit":
        import audit
        return audit.main(argv[1:])
    if cmd == "prove":
        import test_invariants
        return test_invariants.main()
    if cmd == "mind":
        import examples_mind
        examples_mind.main()
        return 0
    if cmd in ("audit-mind", "audit_mind"):
        import audit_mind
        return audit_mind.main(argv[1:])
    if cmd == "tour":
        import examples
        examples.main()
        return 0
    print(_USAGE)
    return 2 if cmd in ("-h", "--help", "help") else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]) or 0)

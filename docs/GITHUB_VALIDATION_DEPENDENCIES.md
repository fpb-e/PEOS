# Public release validation

Run `python3 -B tools/validate_rev0_314.py` on the public tree.
This entry validates only the public manifest, specification bindings and synthetic tests.
Original conversation/image corpus validation stays outside this public repository;
missing private sources are an intentional publication boundary, not a passing source test.
The original release archive remains immutable. No credentials or live private-ledger adapter is distributed.

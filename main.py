#!/usr/bin/env python3
"""One Line, One Laugh — make.fun entry.

Writes one line, a single joke that lands on a cold read, to
$MAKEFUN_OUTPUT_DIR/entry.txt (falling back to /output/entry.txt).

The line (112 characters, 112 bytes, no trailing newline):
    I told my plants I'm proud of them and they're thriving now, which proves my love language is lying to hostages.

Chosen from 44 candidates scored against each of the five published
judge criteria in order (see candidates.md in the work dir): funny on
its own with no setup, laugh arriving fast inside the line, fresh
angle, tight wording, holds up on a second read. Winner scored 68/75
and went 5-0 in a pairwise final against the other top scorers;
runner-up was the AI-wedding-vows line at 65/75. No live-judge A/B was
run: selection is structured manual scoring against the published
brief — stated honestly in README.md, with no judge numbers claimed.

Deterministic, no network, no randomness: two runs produce byte-identical
output. See README.md for the methodology. Verified in-session: two runs
to separate output dirs wrote byte-identical 112-byte entry.txt files,
and the import-time gate was proven to raise ValueError on a 250-char
ENTRY in a /tmp copy before this revision was applied.
"""

import hashlib
import os
import re

ENTRY = "I told my plants I'm proud of them and they're thriving now, which proves my love language is lying to hostages."

# sha256 of ENTRY encoded as UTF-8 (112 bytes, no trailing newline). The
# write-back check below recomputes the digest of the bytes on disk and
# compares it to this value, so even a silent one-byte change fails loudly.
EXPECTED_SHA256 = "3e0387b22ead85b48803df41c9cb3770cb12c52ea2124a536387fd1b5df2d605"

# The competition gate is 1-200 characters, one line, not only whitespace.
# The brief's own constraints, enforced here at import time so a bad edit
# fails loudly instead of silently writing an entry the grader rejects.
MAX_CHARS = 200
BANNED_PATTERNS = (
    re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]"),  # control characters
    re.compile(r"https?://"),                        # links: the line stands alone
    re.compile(r"[*#`_~]"),                         # markdown formatting
    re.compile(r"\[[^\]]*\]"),                      # stage directions like [sighs]
)


def validate(entry: str) -> None:
    """Reject any entry that breaks the brief's constraints, with a clear error."""
    if not entry or not entry.strip():
        raise ValueError("entry is empty or only whitespace: gate needs 1-200 characters")
    if not 1 <= len(entry) <= MAX_CHARS:
        raise ValueError(
            f"entry is {len(entry)} chars, outside the 1-{MAX_CHARS} gate"
        )
    if "\n" in entry or "\r" in entry:
        raise ValueError("entry must be one line: it contains a newline")
    for pattern in BANNED_PATTERNS:
        match = pattern.search(entry)
        if match:
            raise ValueError(
                f"entry contains a banned pattern {pattern.pattern!r}: {match.group(0)!r}"
            )


validate(ENTRY)


def main() -> None:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(ENTRY)
    # Verify the write: read the file back, compare bytes, then compare the
    # sha256 digest of the read-back bytes against the expected digest, so a
    # partial write, encoding surprise, or one-byte corruption fails loudly
    # instead of submitting a corrupted entry.
    written = open(path, "rb").read()
    if written != ENTRY.encode("utf-8"):
        raise OSError(f"entry.txt at {path} does not match the entry")
    digest = hashlib.sha256(written).hexdigest()
    if digest != EXPECTED_SHA256:
        raise OSError(
            f"entry.txt sha256 {digest} != expected {EXPECTED_SHA256}"
        )
    print(ENTRY)


if __name__ == "__main__":
    main()

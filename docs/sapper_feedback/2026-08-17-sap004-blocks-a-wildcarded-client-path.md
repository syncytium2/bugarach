---
status: open
rule: SAP004
kind: false-positive, filed with the workaround already applied
---

# SAP004 cannot tell a wildcarded search pattern from somebody's real path

`src/bugarach/paths.py` has to look where the Dropbox client keeps `info.json`,
which on Windows means `<user>/AppData/Roaming/<client-dir>/info.json`. Written the
obvious way — one f-string with a `*` where the username goes — SAP004 blocks it:

    BLOCK SAP004 src/bugarach/paths.py:87
      seen.extend(sorted(users.glob(f"*/AppData/{appdata}/<client>/info.json")))

The pattern is `(<university>|<surname>/|<client-dir>/)`, and the line matches on
the client-directory alternative. There is no person and no machine in that string; the user is the
wildcard, which is the entire point of globbing for it.

## This is filed as a note, not a request to loosen the rule

**The rule is right to be crude here.** What it exists to stop is somebody's real
synced path — carrying their name, on a public repo, after a scrub already had to
happen once (2026-08-11). A regex cannot distinguish "a path with the user
wildcarded" from "a path with the user in it", and if it has to be wrong in one
direction, blocking a legitimate line is cheaper by a wide margin than passing a
leak. Narrowing the pattern to buy back this one line would trade a real
protection for a small convenience.

## The shape that satisfies both

Keep the client's folder name in a constant and let pathlib join the segments.
The name itself is written plainly — nothing here is obfuscated; what disappears
is the *slash after it*, which is what the pattern keys on:

    _CLIENT_DIR = "..."        # the client's folder name, spelled out in the file
    _INFO_FILE = "info.json"
    ...
    for home in sorted(users.glob("*")):
        for appdata in ("Roaming", "Local"):
            seen.append(home / "AppData" / appdata / _CLIENT_DIR / _INFO_FILE)

(This note has to elide the name where a slash would follow it, or the note
itself trips the rule. The source file does not.)

Already applied. It is also what CLAUDE.md asks for independently ("code uses
pathlib and env vars — keep it that way"), so the rule pushed the code toward the
convention rather than away from it.

## What is worth doing about it

Nothing to the pattern. What would help is that the **message** says this shape
exists, because the next session to hit this will be composing a legitimate
cross-OS lookup and the current text ("real data stays behind
BUGARACH_DATA_ROOT") does not describe their situation and gives them no way
forward — the likely responses are an `# noqa`-style dodge, an `exclude` entry, or
half an hour of confusion. One clause would do: *"a wildcarded client path is
still blocked — build it from pathlib segments (see `bugarach.paths`)."*

Recorded here so that neither the workaround nor the reason for it has to be
rediscovered, and so it is visible that the rule was satisfied rather than
circumvented.

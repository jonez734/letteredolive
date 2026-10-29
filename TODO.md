# TODO — letteredolive (shell)

Live work only. Each item has a unique four-letter code.

---

## [QFKV] `empyre.buildargs` has an `args=None` default

### Problem

`empyre/src/empyre/lib.py` defines `buildargs(args=None, **kwargs)`. The
bbsengine6 loader requires `args` to have no default, so the signature check
fails and `empyre` is reported as "not available". The body already returns an
`ArgumentParser`.

### Fix (in the `empyre` repo)

Remove `=None` from `args`, and annotate `-> argparse.ArgumentParser | None`.

### Validation (run through the installed package, read-only)

- `empyre.buildargs`: FAIL, `args=None` default.
- `empyre.init`, `empyre.main`, `empyre.access`: PASS.
- `empyre.weather.buildargs`: FAIL, `args=None` default (and an extra
  `subparser=None` parameter, which `**kwargs` allows). Same fix as above.
- `empyre.weather.init`, `.main`, `.access`: PASS.

### Status

Deferred to the `empyre` repo; the author is fixing it soon. The shell
`weather` command is disabled in the meantime (see the registry).

---

## [KQKR] `murdermotel.buildargs` return annotation is `-> None`

### Problem

`murdermotel/src/murdermotel/__init__.py`: `buildargs(args, **kwargs) -> None`,
body `return None`. The loader's contract is `argparse.ArgumentParser | None`.
The return value is valid; only the annotation is wrong.

### Fix (in the `murdermotel` repo)

Annotate `-> argparse.ArgumentParser | None`.

### Status

Recorded only. `murdermotel` is out of scope for the shell work.

---

## [OVHO] `moneyday` `buildargs`: `args=None` default and no `None` in the annotation

### Problem

`moneyday/src/moneyday/main.py`: `buildargs(args: Namespace = None, **kwargs)
-> ArgumentParser`. The default on `args` violates the loader rule, and the
annotation omits `None`, which the contract allows.

### Fix (in the `moneyday` repo)

Remove the default from `args`, and annotate `-> argparse.ArgumentParser | None`.

### Status

Recorded only.

---

## [AXTA] `moneyday` `main`: `args=None` default

### Problem

`moneyday/src/moneyday/main.py`: `main(args: Namespace = None, **kw) -> bool`.
The default on `args` violates the loader rule.

### Fix (in the `moneyday` repo)

Remove the default from `args`.

### Status

Recorded only.

---

## [TPOH] Shell reports an installed-but-rejected module as "not installed"

### Problem

When a command's module is installed but fails the loader's signature check,
`shell/main.py` prints `'<name>' is not installed on this system.` That is
misleading: the module is present, and the real problem is its signature.

### Wanted

Distinguish the two cases. A missing module says "not installed". A module
that fails the loader check says it was rejected, and names the check that
failed (for example "buildargs signature invalid").

### Status

Open. Not yet implemented.

---

## [KHKP] `getch()` idle timer that blank input does not reset

Tracked in `bed/TODO.md` under the same code. Blank input at a prompt must not
reset the idle timer, so an idle client cannot hold a port open.

---

## Deferred

- Startup check that walks every command and confirms each module is installed
  and passes the loader check. Deferred by decision.

---

## [EMBED] Run letteredolive from another program (for example casino_client)

Question: can casino start an LO shell in its own process, alongside a member's
own LO shell? Current answer: not as it is. LO is written as a standalone program.

Blockers, found in `src/shell/__main__.py` and `src/shell/lib.py`:

- `main()` reads `sys.argv`, sets the kernel process name (`lib.set_proc_name`, a
  `prctl` call), and decides login-shell state from `argv[0]`. These are process-wide,
  so an embedded instance would rename the host process and misread its arguments.
- `init_screen` sets the terminal scroll region for the whole screen and never resets
  it, so a host prompt would inherit LO's margins.
- `shell_login` and `_check_database` run before the command loop. An embedded instance
  needs the caller to supply the login and the pool.
- Module state (`_screen_initialized`, `_PROC_NAME`) is per process. Two LO instances in
  one process share it, so they cannot be independent shells.

Options:

1. **Subprocess (recommended for casino).** casino_client launches LO as a child with
   its own terminal. No change to LO's state model. Smallest change.
2. **In-process `run(args, pool)`.** Split `main()` so the command loop takes its
   arguments and pool from the caller; keep argv, process-name and connect steps in
   `main()` only; make `init_screen` restore the margins on exit. A few hours. Does not
   allow two independent shells in one process.
3. **Instance state.** Move the shell's module globals into an instance object so several
   LO shells can run in one process. Larger refactor of `src/shell/`.

Decision needed: which option, and whether to do it in this project or leave it to the
casino side.

---

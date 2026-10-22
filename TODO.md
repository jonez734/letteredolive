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

### Status

Deferred to the `empyre` repo; the author is fixing it soon.

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

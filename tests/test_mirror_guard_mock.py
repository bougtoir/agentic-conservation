"""Local mock of the public-mirror push paths (no network).

A bare repository with receive.denyNonFastForwards emulates a force-push
restriction on the mirror's `main`. The legacy workflow path (parentless
commit + `git push --force`) must be rejected; the canonical path (overlay
commit whose parent is the current target head, plain push) must succeed and
delete nothing. The legacy loop's own guard (skip when the mapped source
branch does not exist) is checked as well.
"""

import subprocess
from pathlib import Path


def git(cwd, *args, check=True):
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=check,
        env={
            "GIT_AUTHOR_NAME": "t",
            "GIT_AUTHOR_EMAIL": "t@t",
            "GIT_COMMITTER_NAME": "t",
            "GIT_COMMITTER_EMAIL": "t@t",
            "HOME": str(cwd),
            "PATH": "/usr/bin:/bin",
        },
    )


def commit(work: Path, files: dict, parent: str | None) -> str:
    idx = work / ".idx"
    env_files = []
    for name, text in files.items():
        blob = subprocess.run(
            ["git", "hash-object", "-w", "--stdin"],
            cwd=work,
            input=text,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        env_files.append(f"100644 blob {blob}\t{name}")
    tree = subprocess.run(
        ["git", "mktree"],
        cwd=work,
        input="\n".join(env_files) + "\n",
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    args = ["commit-tree", tree, "-m", "c"] + (["-p", parent] if parent else [])
    idx.unlink(missing_ok=True)
    return git(work, *args).stdout.strip()


def test_force_restriction_blocks_legacy_and_allows_canonical(tmp_path):
    mirror = tmp_path / "mirror.git"
    work = tmp_path / "work"
    git(tmp_path, "init", "-q", "--bare", str(mirror))
    git(mirror, "config", "receive.denyNonFastForwards", "true")
    git(tmp_path, "init", "-q", str(work))
    current = commit(work, {"manuscript.txt": "v3.2", "frozen.txt": "keep"}, None)
    git(work, "push", "-q", str(mirror), f"{current}:refs/heads/main")

    legacy = commit(work, {"old.txt": "obsolete"}, None)  # parentless, drops files
    r = git(work, "push", "--force", str(mirror), f"{legacy}:refs/heads/main", check=False)
    assert r.returncode != 0
    assert git(mirror, "rev-parse", "main").stdout.strip() == current

    canonical = commit(work, {"manuscript.txt": "v3.3", "frozen.txt": "keep"}, current)
    git(work, "push", "-q", str(mirror), f"{canonical}:refs/heads/main")
    assert git(mirror, "rev-parse", "main").stdout.strip() == canonical
    names = git(mirror, "ls-tree", "--name-only", "main").stdout.split()
    assert names == ["frozen.txt", "manuscript.txt"]


def test_legacy_loop_skips_missing_source_branch():
    yml = Path(__file__).resolve().parents[2] / ".github/workflows/sync-to-repos.yml"
    legacy = subprocess.run(
        [
            "git",
            "show",
            "origin/devin/1790254872-functional-geometry-revision:"
            ".github/workflows/sync-to-repos.yml",
        ],
        cwd=yml.parents[2],
        capture_output=True,
        text=True,
    ).stdout
    if not legacy:
        return  # branch not available in this clone
    assert "SKIP: Branch '$BRANCH' not found in wip" in legacy
    assert "git push --force" in legacy

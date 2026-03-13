#!/usr/bin/env python3
"""Generate thesis context files: resume_context.txt (.memory/) + thesis_state.md (docs/)."""
from workflow_lib import (
    build_index,
    build_resume_text,
    build_thesis_state,
    write_index,
    write_resume_text,
    write_thesis_state,
)


def main() -> int:
    index = build_index()
    write_index(index)

    # Schicht 0: Kompakter Resume (Legacy, .memory/ — gitignored)
    text = build_resume_text(index)
    path = write_resume_text(text)
    print(text)
    print(f"\n(Resume gespeichert in: {path})")

    # Schicht 1: Thesis State SSOT (docs/ — git-tracked)
    state = build_thesis_state(index)
    state_path = write_thesis_state(state)
    print(f"\n(Thesis State gespeichert in: {state_path})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# XCL implementation status

Updated: 2026-11-23. Behavior reference:
[ivall/xcl@38b05b7](https://github.com/ivall/xcl/commit/38b05b7b6954cfa5bd21cec72f68823603ca2227),
observed 2026-11-23. The [XCL reference](xcl-reference.md) records the licence boundary and the
[capability matrix](xcl-capability-matrix.md) records the area-by-area gap.

This page is the dashboard for the transfer. It lists reviewable changes, their state and the next
action. Details and evidence belong in the change or its pull request, not here.

## Pull requests

| ID | Branch | Local commit | State | First failure | Next action |
| --- | --- | --- | --- | --- | --- |
| XCL-00 | `docs/xcl-reference` | `7168565` plus status | [PR #1027](https://github.com/R0Y00/Xbox2Windows/pull/1027) open | None | Review and merge. |
| XCL-01 | `tools/compat-report` | Pending | In progress; depends on XCL-00 | None yet | Add the deterministic import report and its synthetic PE test. |
| XCL-14 | None | None | Analysis complete; no branch | Depends on the XCL-01 report schema | Start after XCL-01 is merged. |

At most four pull requests stay open. A branch starts from `origin/main`; a dependent branch is
rebased after its prerequisite lands.

## Current limits

- The Windows jobs for `ee04692` are still running. The Linux Python and LLVM jobs completed
  successfully.
- XCL-00 changes documentation only. It does not establish a runtime measurement.
- XCL-01, XCL-02, XCL-03, XCL-04 to XCL-13, XCL-14 to XCL-23 and the later items remain open in
  the capability matrix.
- One pull request is open, below the limit of four.

## Next actions

1. Merge [XCL-00](https://github.com/R0Y00/Xbox2Windows/pull/1027) after review.
2. Rebase XCL-01 on the new `main`, run
   `out\pe-env\Scripts\python.exe -B tests\compat_report_check.py`, and open it.
3. After XCL-01 merges, start XCL-14 from the shared report schema in the analysis, then the
   import-routing work in XCL-02 and XCL-03.

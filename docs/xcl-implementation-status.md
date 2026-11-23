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
| XCL-01 | `tools/compat-report` | `4a2f0fa` | [PR #1036](https://github.com/R0Y00/Xbox2Windows/pull/1036) open; depends on XCL-00 documentation | None in the synthetic controls | Review; register the test in CTest and CI after merge. |
| XCL-14 | `shader/corpus-report` | `b7d24dd` | [PR #1039](https://github.com/R0Y00/Xbox2Windows/pull/1039) open; shares the XCL-01 report envelope | Native span follows the existing extractor; bounded FSSM and two-output cases stay visible | Review; wire the decoder and attachment path after XCL-01 lands. |

At most four pull requests stay open. A branch starts from `origin/main`; a dependent branch is
rebased after its prerequisite lands.

## Current limits

- The Windows jobs for `ee04692` are still running. The Linux Python and LLVM jobs completed
  successfully.
- XCL-00 changes documentation only. It does not establish a runtime measurement.
- XCL-01, XCL-02, XCL-03, XCL-04 to XCL-13, XCL-14 to XCL-23 and the later items remain open in
  the capability matrix.
- Three pull requests are open, below the limit of four.
- XCL-01 and XCL-14 exceed the 400-line guide because their tests build the PE32+ and shader
  framing fixtures from bytes. Each tool and its test remain one behavior; CI registration is a
  follow-up.
- The Linux Python and LLVM jobs pass on XCL-00 and XCL-01. The Windows jobs are still running.
  XCL-14 was pushed after those checks started.
- XCL-01 and XCL-14 can land in either order because they share only the JSON envelope. XCL-02
  and later work stay blocked until XCL-01 is merged. The author does not merge these PRs.

## Next actions

1. Merge [XCL-00](https://github.com/R0Y00/Xbox2Windows/pull/1027) after review.
2. Merge [XCL-01](https://github.com/R0Y00/Xbox2Windows/pull/1036) after review, then register
   `compat_report_check` in CTest and the platform-independent Python CI job.
3. Review [XCL-14](https://github.com/R0Y00/Xbox2Windows/pull/1039), then wire its decoder and
   attachment path to the merged XCL-01 report.
4. Rebase XCL-01 and XCL-14 after each merge, then start the import-routing work in XCL-02 and
   XCL-03.

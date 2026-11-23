# XCL reference for Xbox2Windows

XCL is a public compatibility layer for Xbox Series X|S software on PC. Xbox2Windows uses it as a behavioural reference, not as a code source. This note records why we read it, what may cross the boundary, how an observation is cited and where the static-recompilation project stops. The companion [capability matrix](xcl-capability-matrix.md) turns the comparison into backlog items.

## Pinned reference

| Field | Value |
| --- | --- |
| Repository | [ivall/xcl](https://github.com/ivall/xcl) |
| Commit | `38b05b7b6954cfa5bd21cec72f68823603ca2227` |
| Reference observed | 2026-11-23 |
| Licence | GPL-2.0-only |

XCL changes quickly. The commit above is the only revision this project cites until a documentation change moves the pin. Record the commit, date, environment and observed result with every observation. A link to a moving branch, an issue title or a release note does not replace the commit.

## Purpose

XCL is useful because it has already encountered questions that a static-recompilation project meets late: which runtime services a retail title imports, which console GPU objects it creates, which shader forms appear in a real pack and where a compatibility layer stops first. Its public reports give us a list of questions and a rough order of work.

XCL does not supply Xbox2Windows implementations, fixtures or measurements. We use it to decide what to investigate, then answer the question against public specifications and source-built inputs. The result must stand without XCL.

## Licence boundary

XCL is **GPL-2.0-only**. Xbox2Windows is **MIT**. The two licences do not permit a combined distributed work, and GPL-2.0-only code cannot be merged into the GPL-3.0 projects around this workspace either.

- Do not copy or translate XCL source, comments, identifiers, enum layouts, tables, tests or generated HLSL/DXIL.
- Do not link XCL into an Xbox2Windows binary or ship XCL code with an Xbox2Windows artifact.
- Do not paste XCL code or generated output into an issue, pull request, commit or fixture.
- Do not use an XCL-generated file as an input to an Xbox2Windows test.

If direct reuse ever becomes necessary, the clean choices are a separate GPL-2.0-only process or tool that exchanges data across a documented boundary, or a deliberate relicence of the affected Xbox2Windows component. Both are project decisions. Neither is a shortcut around review.

## What may be observed

- Public material: the README, HANDOFF, issues, pull requests, design notes and release notes.
- Local behaviour on synthetic input or the operator's own game copy: counts, slot numbers, return values, call order, first failure and timings.
- A compatibility report as a checklist of requested services, imports, stages or slots. Record the shape and counts; do not copy the report's tables.
- The diagnostic that ends a run: which API class, resource or shader form stopped first.

Keep raw output in `game-files/` or `out/`. Both are ignored by Git. A committed note may describe a count or a failure, but it may not contain title bytes, shader bytes, save data, screenshots of title content or a path that distributes the title.

## What may not be observed or reused

- XCL source code, comments, identifiers, tables, generated shaders or test data.
- Game files, dumps, title logs, shader bytes, screenshots, save data or report fragments containing title data.
- Distribution links, keys or instructions for obtaining a title.
- An XCL result presented as an Xbox2Windows measurement.

The last point is easy to blur. 'XCL reached the first menu on its development machine' describes XCL, its build, its hardware and its commit. It says nothing about whether an Xbox2Windows fixture passes, whether translated code runs or whether a frame is presented. An Xbox2Windows claim needs an Xbox2Windows commit, command, fixture and observed result.

## Provenance note

Every change that starts from an XCL observation carries this note in the pull request body. When the observation shapes a design, the note also appears in the affected document.

```text
Reference: ivall/xcl@<sha>, <issue or file URL>, observed <date>.
Public specification used: <GDK / D3D12 / AMD ISA / LLVM link>.
Independent implementation: <files>.
Tests: <positive fixture, negative control>.
```

Use the full 40-character commit. Replace every placeholder. The note records influence; it does not grant permission to copy. A reviewer should be able to open the observation, open the public specification and check that the implementation and its tests stand on their own.

## Public references

- [XCL README](https://github.com/ivall/xcl#readme)
- [XCL HANDOFF](https://github.com/ivall/xcl/blob/main/HANDOFF.md)
- [Early retail-title report, issue #159](https://github.com/ivall/xcl/issues/159)
- [NVIDIA report, issue #173](https://github.com/ivall/xcl/issues/173)
- [GPU results, issue #42](https://github.com/ivall/xcl/issues/42)
- [Shader count reconciliation, issue #36](https://github.com/ivall/xcl/issues/36)
- [XCL issue tracker](https://github.com/ivall/xcl/issues)

Issue numbers are stable, but titles and contents can change. Cite the pinned commit and the reading date as well as the issue.

## Scope limit: static recompilation

Xbox2Windows translates selected x64 functions from PE machine code through C++ and translates selected gfx1013 shader programs to desktop DXIL. It runs the results with Windows runtime shims. XCL is a runtime compatibility layer that boots a title. The two projects can share questions; they do not share an architecture.

Matching an XCL capability means making the equivalent behaviour available to translated code, with our own fixture and negative control. It does not mean adding a second emulator. Work that exists only to boot an unmodified title, or that bypasses the translation path, is outside the scope of this project.

An XCL observation creates a hypothesis. When accepted, it becomes a backlog item in the matrix. It does not close the item. A matrix row becomes measured only when an Xbox2Windows test names the commit, command, fixture and result.

## From observation to change

1. Pin the XCL commit. Record the date, environment and observation; keep raw output in `out/`.
2. Reduce the observation to one question, such as 'which descriptor-heap slot does this class request?'.
3. Read the public specification: GDK, D3D12, the AMD ISA or LLVM, depending on the question.
4. Implement against the specification with source-built or synthetic fixtures.
5. Add a positive test and a negative control, then add the provenance note.
6. Update the matrix row and its backlog ID, or record why the item stays open.

If a step cannot be completed without XCL code or title data, stop and record the limitation. A partial observation is useful; a copied implementation is not.

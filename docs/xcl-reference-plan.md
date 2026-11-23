# XCL reference plan for Xbox2Windows

Draft, 2026-11-23. XCL reference: [ivall/xcl](https://github.com/ivall/xcl), pinned at
`38b05b7` for this plan. XCL moves quickly; record the commit used for every observation.

## Purpose

XCL is the most complete public Xbox Series X|S compatibility layer we have examined. It boots
retail titles, translates the whole GTA VI shader pack and reaches the title's first menu on its
RDNA4 development machine. Xbox2Windows should use it as a behavioural reference and as a source
of priorities, not as a source of code.

## License boundary

XCL is **GPL-2.0-only**. Xbox2Windows is **MIT**. The two licences are not compatible for a
combined work, and GPL-2.0-only code cannot be merged into the GPL-3.0 projects around this
workspace either.

Allowed:

- Read XCL's public README, issues, pull requests, design notes and test descriptions.
- Run XCL locally on synthetic inputs or on the user's own game copy.
- Record observed behaviour: counts, slot numbers, return values, first failures, timings.
- Reimplement a behaviour from public Microsoft GDK/D3D12 documentation, AMD's ISA, LLVM and
  source-built fixtures.
- Use XCL's `report.json` as a checklist for what a title asks for.

Not allowed:

- Copy or translate XCL source, comments, identifiers, tables or generated HLSL/DXIL.
- Link XCL into an Xbox2Windows binary or ship XCL code with Xbox2Windows.
- Commit game files, dumps, XCL output containing game data, or distribution links.
- Present an XCL observation as an Xbox2Windows measurement.

Every change that starts from an XCL observation gets a short provenance note:

```text
Reference: ivall/xcl@<sha>, <issue or file URL>, observed <date>.
Public specification used: <GDK / D3D12 / AMD ISA / LLVM link>.
Independent implementation: <files>.
Tests: <positive fixture, negative control>.
```

If direct code reuse ever becomes necessary, the clean options are a separate GPL-2.0-only
process/tool or a deliberate relicence of the affected component. That is a project decision, not
an implementation shortcut.

## Capability map

Statuses describe the current Xbox2Windows tree on 2026-11-23.

| Area | XCL | Xbox2Windows | Gap | First action |
| --- | --- | --- | --- | --- |
| PE mapping and relocations | Full, data-driven import routing | `pe_map` covers mapping, relocations, TLS, SEH and load config | No unified routing report | `tools/compat_report.py` |
| Import routing | HLE / Windows / stub, name, ordinal, delay-load | Imports are mapped, but not classified per policy | Routing policy and diagnostics | Extend `pe_inventory.py` and `intake_exe.py` |
| Title memory and physical pages | UMA, physical pages, 4 GiB windows | `era_heap`, `era_physical`, `era_title_gpu`, `era_gpu_alias` | Large-memory and sparse-page coverage | Add title-memory fixtures |
| XGameRuntime | 396 GDK functions, XUser, XGameSave, PLS, XPackage, XSystem | No dedicated shim in the tree | Large | Add a thunk table and shim skeleton |
| D3D12.X device | Full console device and slots | Root-signature/device shim only | Large | Inventory slots, then device creation |
| D3D12.X command lists | Compute and graphics, heaps, PresentX | Not implemented | Large | Compute path first |
| Shader translator | Whole GTA VI pack: 26,503 records | Selected gfx1013 forms; PR #1002 merged | Instruction and stage coverage | Corpus coverage report |
| Pipelines | VS/PS, CS, MS/PS, VS/GS/PS, background creation | `pso_readiness.py` inventory | Creation path and fallbacks | Add PSO fixtures |
| Textures | Byte-exact GFX10 tiling and mips | Strong asset tooling, no full runtime tiling | Runtime tiling and format translation | Synthetic tiling tests |
| Audio | XAudio2, Opus, XMA1/2 | Metadata and probes | Runtime audio | Defer until boot |
| Media | Bink, FSR4, BVH, DirectStorage | Bink/FSR/BVH experiments | End-to-end paths | Defer until boot |
| Tools | `inspect`, `run`, `disasm`, `shaders`, `rpf`, `report.json` | Many focused scripts | No single report or run command | `compat_report` + `inspect` |
| Tests | 370+ unit/integration/GPU | Extensive CPU/GPU fixtures | Cross-project oracle reports | Add synthetic oracle tests |

## Execution plan

The schedule assumes one full-time developer. Phases 2 and 4 can run in parallel with a second
person.

### Phase 0 - Reference and measurement (2-3 days)

1. Add `docs/xcl-reference.md`: licence boundary, pinned commit, feature summary, links.
2. Add this capability matrix to the docs tree and keep it current.
3. Add `tools/compat_report.py`:
   - classify every PE import as HLE, Windows, stub or unsupported;
   - list ordinal and delay-load imports;
   - report TLS, SEH and load-config features found by `pe_map`;
   - optionally census a user-supplied shader pack (record count, stages, top unsupported forms);
   - write deterministic JSON and Markdown.
4. Add `tests/compat_report_check.py` with a synthetic PE containing named, ordinal and delay
   imports, plus an unknown-DLL negative control.
5. Add a README entry for the report.

Exit criteria: the synthetic fixture reports the expected route for every import, an unknown DLL
fails with its name, and the report is byte-deterministic.

### Phase 1 - Import routing and boot diagnostics (1 week)

1. Add a route table in `tools/pe_inventory.py` or a new `tools/import_routing.py`.
2. Extend `tools/intake_exe.py` and `tools/pe_run_package.py` to print the route for each import
   and refuse an unbound import with the DLL, symbol and caller.
3. Add delay-load coverage to `pe_map` tests if the current fixtures do not already exercise it.
4. Add a synthetic test title with one import from each route, including a missing stub.
5. Run the report on the local GTA VI EXE (read-only) and compare its counts with the XCL issue
   reports. Keep the output under `out/` and do not commit it.

Exit criteria: every import in the local EXE has a route; no route is silently guessed; the
negative control names the missing binding.

### Phase 2 - XGameRuntime and kernelx surface (2 weeks)

1. Add `src/xgameruntime_shim.cpp` and `.def` with a data-driven table generated from public GDK
   headers and documentation.
2. Start with the thunk protocol and the classes the title requests: XUser, XGameSave, persistent
   local storage, XPackage, XGame, XSystem, XAsync and XTaskQueue.
3. Reuse the existing `era_*` memory and page bookkeeping for title memory and PLS.
4. Add a synthetic test title that calls one representative function from each class; add a
   negative control for an unimplemented class.
5. Use an XCL `report.json` only to enumerate requested classes and slots. Do not copy its table.

Exit criteria: the synthetic title reaches its checks with no called stub; every exported thunk
has a test; unimplemented classes report their class and slot.

### Phase 3 - D3D12.X compute, then graphics (3-4 weeks)

Split this into reviewable PRs:

1. Device and adapter slots, including the console IID map and resource creation.
2. Descriptor heaps: CBV/SRV/UAV and sampler slots, CPU/GPU handles, table records.
3. Compute command lists: tables, barriers, clears, copies, dispatches and readback.
4. Buffers at console addresses and the UMA window via `era_gpu_alias`.
5. Graphics command lists: RTV/DSV, root arguments, draws, indirect draws, rect lists and
   `PresentX`.
6. Resource states, aliasing and sparse pages.

Add `tests/d3d12x_compute_check.cpp` and `tests/d3d12x_graphics_check.cpp` with source-built
shaders and CPU references. Use XCL's public slot inventory as a checklist, and Microsoft's
desktop D3D12 documentation for each method shape.

Exit criteria: a compute dispatch round-trips a known buffer; a triangle renders to a known
target; `PresentX` reaches a frame boundary; the test title's D3D12.X checks pass.

### Phase 4 - Shader coverage to the whole pack (2-3 weeks, parallel with Phase 3)

1. Add a corpus harness that runs the existing extractor and translator over a user-supplied
   shader pack and records: records, stages, decoded dwords, translated modules, validation
   failures and the top unsupported forms.
2. Use XCL's public counts (26,503 records) and issue #36 to reconcile denominators. Do not copy
   its translator or output.
3. Prioritise forms by frequency in the user's own pack; implement one instruction family per PR.
4. For each family, add a source-built fixture, a passing GPU comparison and a negative control.
5. Extend the existing compute/pixel/mesh test pages; PR #1002 is the template for a qword family.

Exit criteria: the report distinguishes records, programs and streams; every implemented form has
a fixture; the pack translation rate is measured, not inferred.

### Phase 5 - Pipelines and textures (2 weeks)

1. Build PSOs from translated shaders: root signatures, static samplers, VS/PS, CS, MS/PS and
   VS/GS/PS. Add a non-blocking path for large pipelines.
2. Add GFX10 tiling and mip-layout tests: 2D, 3D, BC1-BC7 and the console's packed formats.
3. Compare synthetic tiling results with public XCL measurements; do not copy its tables.
4. Add negative controls for a wrong tile size, a wrong mip tail and a wrong format family.

Exit criteria: the test pipeline draws; synthetic textures round-trip byte-exactly; unsupported
formats fail with the format and the resource shape.

### Phase 6 - End-to-end bring-up and media (1-2 weeks)

1. Run `compat_report` and the static-recompilation path on the local GTA VI package.
2. Capture the first stop with the commit, command, report and logs; compare it with XCL's
   published first-stop reports.
3. Add audio/media only after the first frame: XAudio2 voices, XMA/Opus, Bink, FSR4 and BVH.
4. Keep game data local; publish only synthetic fixtures and measurements.

Exit criteria: a reproducible first stop, a report another contributor can reproduce, and no game
data in the repository.

## First ten working days

| Day | Deliverable |
| --- | --- |
| 1-2 | `docs/xcl-reference.md`, capability matrix, `tools/compat_report.py` skeleton |
| 3-4 | `compat_report` classification and synthetic PE test |
| 5 | Import-routing table and `intake_exe` diagnostics |
| 6-7 | XGameRuntime import inventory and thunk-table skeleton |
| 8 | First XUser/XGameSave synthetic call |
| 9 | D3D12.X slot inventory and device-creation fixture |
| 10 | Shader corpus report and first priority list |

## Timeline

| Week | Milestone |
| --- | --- |
| 1 | Reference docs, capability matrix, `compat_report` |
| 2 | Import routing complete; XGameRuntime skeleton |
| 3-4 | XGameRuntime classes; shader corpus report |
| 5-6 | D3D12.X compute path |
| 7-8 | D3D12.X graphics and PSO creation |
| 9 | Texture tiling and format tests |
| 10 | End-to-end first-stop report |

## Metrics

- Import report: 100% of imports classified, 0 unknown.
- XGameRuntime: 0 called stubs for the classes the title requests.
- D3D12.X: compute readback, triangle draw and one presented frame.
- Shaders: records/programs/streams separated; every implemented form has a passing fixture.
- Pipelines: PSO creation for the test shaders, including one mesh and one geometry pipeline.
- Textures: byte-exact synthetic tiling for the supported formats.
- End-to-end: a reproducible first stop with a committed synthetic fixture and a local-only report.

## Risks

- **Licence contamination.** The largest risk. Keep XCL at arm's length and record provenance.
- **Scope creep.** XCL is a runtime; Xbox2Windows is a static-recompilation research project.
  Add runtime shims to support translated code, not a second emulator.
- **XCL is a moving target.** Pin one commit per observation and do not chase every change.
- **GPU coverage.** Wave64 and mesh shaders differ on NVIDIA, Intel and AMD. Report the adapter,
  driver and debug-layer state.
- **Game data.** Never commit files, dumps, logs, shader bytes or report fragments that contain
  title data. Keep them in `game-files/` or `out/`.

## References

- [XCL README](https://github.com/ivall/xcl#readme)
- [XCL HANDOFF](https://github.com/ivall/xcl/blob/main/HANDOFF.md)
- [XCL first GTA VI report](https://github.com/ivall/xcl/issues/159)
- [XCL NVIDIA GTA VI report](https://github.com/ivall/xcl/issues/173)
- [XCL GPU results](https://github.com/ivall/xcl/issues/42)
- [Shader count reconciliation](https://github.com/ivall/xcl/issues/36)

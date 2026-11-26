# All-or-none gate for the BVH builder's compute stages

The console ray-tracing structure builder is a set of compute programs from `XboxBvhBuilder.dll`.
Its stages feed each other through title memory; a stage that runs on data a missing stage never
wrote computes store offsets from garbage. In the observed failure, 14 of 35 translated stages ran
and the title died within a second on pointers that had become bounding-box bit patterns.

`X2W_COMPUTE_BUILDER_GATE=1` makes the set run all or none. It is off by default and changes no
existing path when unset.

## Identification

At device slot 62, the gate resolves the caller module of the return address with
`GetModuleHandleExW(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS)` and compares the basename with
`XboxBvhBuilder.dll`, case-insensitively. A compute pipeline is tracked only when that resolution
succeeds; an unresolved caller is left untracked rather than guessed. The header's pure classifier
and state machine are tested without a device or a title module.

## Decision

A builder Dispatch is allowed when every tracked builder pipeline has a real desktop PSO. On the
first builder Dispatch the gate makes the missing pipelines on the spot. If one cannot be made, the
builder is turned off for the rest of the run and the Dispatch is refused with a named reason. A
non-builder Dispatch is unchanged. A placeholder pipeline without a translated compute request key
keeps its normal request path: the gate applies only once a translation exists. The gate is counted
in the compute totals line as `builder gate refused N`.

## Scope and limits

This is a safety gate, not a translation. The slot 62 programs are console GPU code; the gate's
on-the-spot creation first requires a structurally valid desktop compute container and a desktop
root signature. A console DXIL program fails by name and latches the builder off, which is the
intended conservative result until the translation path publishes real compute PSOs.

The module-resolution path is exercised by the existing slot 62 call flow only when the gate is on;
the device-free test covers the classifier and the all-or-none state machine, not a loaded title
module. A real-title run with the gate on must report either `all have a desktop PSO` or one named
reason, and must never leave a partially tracked builder running.

```powershell
ctest --preset dev --no-tests=error -R '^startup_compute_builder_gate$' -V
```

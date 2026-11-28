# Startup indirect DispatchL2

The title creates a command signature with Xbox argument type `0x69` (105) and a 12-byte
stride. The GDK reference identifies 105 as `D3D12XBOX_INDIRECT_ARGUMENT_TYPE_DISPATCH_L2`:
the argument record is the ordinary three-DWORD Dispatch record, and the Xbox flags are a
direct member of the signature's argument descriptor. The previous stand-in recognized
`0x69` as an unsupported console type and returned a placeholder signature, so every such
`ExecuteIndirect` was dropped before the pipeline check.

Device slot 41 now recognizes exactly one argument of type 105 with stride
`sizeof(D3D12_DISPATCH_ARGUMENTS)`. It copies the signature description, changes that
argument's type to desktop `D3D12_INDIRECT_ARGUMENT_TYPE_DISPATCH`, creates the desktop
signature, and records the wrapper as a Dispatch signature with a 12-byte stride. Other
unknown console types keep the placeholder behavior.

The scope is deliberately narrow: the Xbox DispatchL2 flags are not forwarded because the
desktop signature has no equivalent, only a single rootless or ordinarily rooted argument
is accepted, root-view and other console signature arguments are unchanged, and the title's
compute pipeline must still have a translated desktop PSO. The change removes a lost
signature; it does not translate the shader.

`tests/startup_indirect_dispatch.cpp` creates a type-105 signature, runs the same GPU-written
Dispatch record through it, and compares the fenced result with the CPU reference. Its
placeholder control now uses type `0x6a`, which remains unsupported. On WARP and the AMD
Radeon RX 9060 XT, `startup_indirect_dispatch_warp` and
`startup_indirect_dispatch_hardware` pass 2/2.

In a 300-second title run, the indirect totals changed from the known placeholder bucket to
`placeholder-signature: 0`; the same signatures now reach the `compute-pipeline` refusal
bucket. The run still produced no 3D because the corresponding compute/mesh pipelines were
not translated. This experiment establishes the signature mapping, not a rendering
milestone.

```powershell
cmake --build --preset release --target startup_indirect_dispatch
ctest --preset release --no-tests=error -R '^startup_indirect_dispatch_(warp|hardware)$' -V
```

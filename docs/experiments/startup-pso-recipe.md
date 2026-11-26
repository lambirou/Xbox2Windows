# Translated PSO recipes

The shader cache stores the translated vertex and pixel bytecode, the root signature and the
sampler descriptions. It does not store the draw state that produced a desktop graphics pipeline
state object: the blend state, depth-stencil state, rasterizer state, target formats and DSV format.
A run therefore creates each translated PSO on its first draw.

`X2W_PSO_RECIPE_DIR=<dir>` records that state after a successful
`CreateGraphicsPipelineState` and replays matching records before creating a new PSO on a later
run. It is off by default.

## Format

One text file per translation key: `<dir>/pso_<translation-key>.txt`. The file holds up to 64
records and 64 KiB. Each record starts with `x2w-pso-recipe 1` and ends with `end`. It carries the
translation key, the target/depth/raster state key, the target count and formats, the DSV format,
the `indexed_rect` flag, the effective blend state after export write masks, the depth-stencil
state, the rasterizer state, the sample mask and count, and the topology type. No pointers or
process addresses are written.

The parser recomputes the state key from the recorded fields. A record whose recomputed key does
not match the key it names, whose target formats or DSV do not match the current pass, or whose
version is unknown is ignored and the unchanged creation path runs. A malformed or oversized file
is counted and ignored.

## Scope and limits

This is state reconstruction, not a D3D12 pipeline library. A replayed record still calls
`CreateGraphicsPipelineState`; the driver may compile or find the PSO in its own cache. The change
moves the state reconstruction and the first-use creation earlier, and makes the exact draw state
available without a title run. It does not claim to eliminate driver compilation.

The device-free test `startup_pso_recipe` covers the serializer/parser round trip, two appended
records, a corrupt state key, an unknown version, an oversized file, and target-format and DSV
mismatches. The parser and state-key matching are verified. A two-process translated-draw replay
with the same recipe directory is not yet part of the suite; the existing `startup_stream_*`
fixtures can supply the translated draw when that case is added.

```powershell
ctest --preset dev --no-tests=error -R '^startup_pso_recipe$' -V
```

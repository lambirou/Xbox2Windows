# First `image_bvh_intersect_ray` slice: FP32 box nodes

`tools/startup/gfx2hlsl.py` now lowers the 32-bit `image_bvh_intersect_ray` (RDNA 2 MIMG opcode 230) for
one node form: the 128-byte FP32 box node, kind 5. The result is four child pointers, with `0xffffffff` for a
disabled child or a missed box. The helper performs the four slab tests, clips against `ray_extent`, and sorts
hits by entry distance only when bit 31 of the BVH T# is set. With sorting disabled it compacts hits in child
order, which is the order a traversal consumes the four results.

The node layout is the one in Mesa 25.1.0 `src/amd/vulkan/bvh/bvh.h` (MIT): `children[4]` at bytes 0..15,
`coords[4][2][3]` at 16..111, and four reserved words at 112..127. The slab test follows Mesa
`radv_nir_rt_common.c` (MIT): inverse direction clamped to finite extremes, `tmin`/`tmax` from the three axes,
an inactive box whose `min.x` is NaN, `tmax >= max(0, tmin)`, `tmin < ray_extent`, and the five compare-exchange
stages that sort the four children. A child word of `0xffffffff` is a miss even when its stored box would hit.
The BVH T# fields are RDNA 2 ISA Table 49: base 39:0 (256-byte aligned), reserved 54:40, box growing 62:55,
box sorting 63, size 105:64, triangle return mode 120, big page 123 and type 8 at 127:124.

## Accepted slice

- compute stage only;
- `image_bvh_intersect_ray v[4], v[11], s[4]` with the packed address form (the disassembler prints `v[16:31]`
  for the eleven consumed dwords);
- a constant inline T# built by four SGPR constants, type 8, base nonzero and 256-byte aligned, box growing zero,
  size at least one 64-byte unit and below 4 GiB, and the node inside that size;
- a constant node pointer whose low three bits are 5, 128-byte aligned and inside the same 4 GiB address window;
- either value of the sort bit.

The manifest names the node allocation with `srv <i> bvh base 0x<base> size 0x<size>`. The host must bind a raw
`ByteAddressBuffer` at the base covering `(size + 1) * 64` bytes. That host binding is not part of this change.

## Refused by name

Triangle nodes (kind 0), 16-bit box nodes (kind 4), every other node kind, `image_bvh64_intersect_ray`, A16,
non-sequential addresses, a pixel or vertex stage, a node pointer that is not a straight-line constant, a T#
loaded at run time, a type other than 8, nonzero box growing, a misaligned base, an absolute base, a size that
does not cover the node, size bits above 4 GiB, and every reserved T# field. The checks assert that a refusal
emits no helper call and no destination VGPR assignment.

## Evidence

```text
python -B tests/startup_gfx2hlsl_bvh_check.py
```

The check compares the CPU box reference with the fixture in `tests/gfx1030_bvh_box/check.py` for five rays,
compares the emitted sort network with the same reference, checks the sort-bit negative control (word 0 changes
from `0x1d` to `0x25`), translates a synthetic constant-T# program and checks the four child results and the
manifest, and checks every refusal above. It also compiles the translated compute shader with DXC when one is
available; without DXC it prints `dxc compile: skip` and does not count that as a pass.

This is a translator slice. It does not execute the native gfx1030 probe, does not bind the node buffer on a
D3D12 device, and does not establish any title behavior.

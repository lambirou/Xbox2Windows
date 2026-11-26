# All-or-none gate for the console BVH builder's compute pipeline set
# (src/startup_stubs/compute_builder_gate.h), without a device or a title module.
add_executable(startup_compute_builder_gate_check tests/startup_compute_builder_gate_check.cpp)
target_include_directories(startup_compute_builder_gate_check PRIVATE src)
target_compile_features(startup_compute_builder_gate_check PRIVATE cxx_std_17)
add_test(NAME startup_compute_builder_gate COMMAND startup_compute_builder_gate_check)

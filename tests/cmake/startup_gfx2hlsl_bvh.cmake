# gfx2hlsl image_bvh_intersect_ray FP32 box-node slice: translator controls and a DXC compile
# when one is available (the check prints a capability skip otherwise).
if(EXISTS "${INTAKE_PYTHON}")
    add_test(NAME startup_gfx2hlsl_bvh COMMAND "${INTAKE_PYTHON}" -B
        "${CMAKE_CURRENT_SOURCE_DIR}/tests/startup_gfx2hlsl_bvh_check.py")
endif()

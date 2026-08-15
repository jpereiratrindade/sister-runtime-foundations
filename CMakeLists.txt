cmake_minimum_required(VERSION 3.20)

project(
  SisTerRuntimeFoundations
  VERSION 0.1.0
  DESCRIPTION "From Bare Metal to Governed Containers"
  LANGUAGES CXX
)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(srf-runtime-probe src/runtime_probe.cpp)

if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
  target_compile_options(
    srf-runtime-probe
    PRIVATE
      -Wall
      -Wextra
      -Wpedantic
      -Werror
      -Wconversion
      -Wsign-conversion
  )
endif()

include(CTest)
if(BUILD_TESTING)
  find_package(Python3 REQUIRED COMPONENTS Interpreter)
  add_test(
    NAME runtime-probe-integration
    COMMAND
      "${Python3_EXECUTABLE}"
      "${CMAKE_CURRENT_SOURCE_DIR}/tests/runtime_probe_integration.py"
      "$<TARGET_FILE:srf-runtime-probe>"
  )
  set_tests_properties(runtime-probe-integration PROPERTIES TIMEOUT 15)
  add_test(
    NAME epistemic-model
    COMMAND
      "${Python3_EXECUTABLE}"
      "${CMAKE_CURRENT_SOURCE_DIR}/tests/epistemic_model_test.py"
  )
  set_tests_properties(epistemic-model PROPERTIES TIMEOUT 5)
endif()

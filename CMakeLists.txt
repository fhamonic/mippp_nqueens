cmake_minimum_required(VERSION 3.20)

project(
  nqueens
  VERSION 1.0
  LANGUAGES CXX)

# ################### Packages ####################
find_package(mippp REQUIRED)
find_package(ortools REQUIRED)

# ################### Modules ####################
set(CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/cmake" ${CMAKE_MODULE_PATH})
include(CompilerWarnings)
include(CompilerOptimizations)

# ################### Targets #####################
function(set_mippp_options _target)
  target_include_directories(${_target} PUBLIC include)
  target_link_libraries(${_target} mippp::mippp)
  # target_compile_options(${_target} PUBLIC -ftime-report)
  set_project_optimizations(${_target})
  set_project_warnings(${_target})
endfunction()

add_executable(mippp src/mippp.cpp)
set_mippp_options(mippp)

add_executable(mippp_bulk src/mippp_bulk.cpp)
set_mippp_options(mippp_bulk)


set(GUROBI_DIR "/home/plaiseek/Softwares/solvers/gurobi1201/linux64"
    CACHE PATH "Gurobi SDK root, needed by the gurobi_c and gurobi_c_bulk benchmarks")
set(GUROBI_LIB "gurobi120"
    CACHE STRING "Gurobi library name, matches the SDK version")

if(EXISTS "${GUROBI_DIR}/include/gurobi_c.h")
  function(set_c_options _target)
    target_include_directories(${_target} PUBLIC include)
    target_include_directories(${_target} PUBLIC "${GUROBI_DIR}/include")
    target_link_directories(${_target} PUBLIC "${GUROBI_DIR}/lib")
    target_link_libraries(${_target} ${GUROBI_LIB})
    # target_compile_options(${_target} PUBLIC -ftime-report)
    set_project_optimizations(${_target})
    set_project_warnings(${_target})
  endfunction()

  add_executable(gurobi_c src/gurobi_c.cpp)
  set_c_options(gurobi_c)

  add_executable(gurobi_c_bulk src/gurobi_c_bulk.cpp)
  set_c_options(gurobi_c_bulk)
else()
  message(STATUS
    "Gurobi SDK not found (GUROBI_DIR=${GUROBI_DIR}), skipping the gurobi_c and gurobi_c_bulk benchmarks")
endif()



add_executable(or_tools src/or_tools.cpp)
target_include_directories(or_tools PUBLIC include)
# the or-tools::or-tools umbrella target wraps libortools.a in WHOLE_ARCHIVE,
# which keeps the MPSolver interface registrars from being dropped by the linker
target_link_libraries(or_tools or-tools::or-tools)
set_project_optimizations(or_tools)
set_project_warnings(or_tools)
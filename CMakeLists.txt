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
  target_link_libraries(${_target} mippp::mippp)
  # target_compile_options(${_target} PUBLIC -ftime-report)
  set_project_optimizations(${_target})
  set_project_warnings(${_target})
endfunction()

add_executable(mippp src/mippp.cpp)
set_mippp_options(mippp)

add_executable(mippp_distinct src/mippp_distinct.cpp)
set_mippp_options(mippp_distinct)

add_executable(mippp_bulk src/mippp_bulk.cpp)
set_mippp_options(mippp_bulk)

add_executable(mippp_bulk_distinct src/mippp_bulk_distinct.cpp)
set_mippp_options(mippp_bulk_distinct)


if(EXISTS "$ENV{GUROBI_HOME}/include/gurobi_c.h")
  function(set_c_options _target)
    target_include_directories(${_target} PUBLIC "$ENV{GUROBI_HOME}/include")
    target_link_directories(${_target} PUBLIC "$ENV{GUROBI_HOME}/lib")
    target_link_libraries(${_target} "gurobi120")
    set_project_optimizations(${_target})
    set_project_warnings(${_target})
  endfunction()

  add_executable(gurobi_c src/gurobi_c.cpp)
  set_c_options(gurobi_c)

  add_executable(gurobi_c_bulk src/gurobi_c_bulk.cpp)
  set_c_options(gurobi_c_bulk)
else()
  message(STATUS
    "Gurobi SDK not found, export GUROBI_HOME=\".../gurobi1201/linux64\"")
endif()


add_executable(or_tools src/or_tools.cpp)
target_include_directories(or_tools PUBLIC include)
target_link_libraries(or_tools or-tools::or-tools)
set_project_optimizations(or_tools)
set_project_warnings(or_tools)
cmake_minimum_required(VERSION 3.20)

project(
  nqueens
  VERSION 1.0
  LANGUAGES CXX)

# ################### Packages ####################
find_package(mippp REQUIRED)

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


function(set_c_options _target)
  target_include_directories(${_target} PUBLIC include)
  target_link_directories(${_target} PUBLIC "/home/plaiseek/Softwares/solvers/gurobi1201/linux64/lib")
  target_link_libraries(${_target} gurobi120)
  # target_compile_options(${_target} PUBLIC -ftime-report)
  set_project_optimizations(${_target})
  set_project_warnings(${_target})
endfunction()

add_executable(c src/c.cpp)
set_c_options(c)

add_executable(c_bulk src/c_bulk.cpp)
set_c_options(c_bulk)



# include(FetchContent)
# FetchContent_Declare(
#   or-tools
#   GIT_REPOSITORY https://github.com/google/or-tools.git
#   GIT_TAG        main
# )
# FetchContent_MakeAvailable(or-tools)

# add_executable(or_tools src/or_tools.cpp)
# target_include_directories(or_tools PUBLIC include)
# target_link_libraries(or_tools ortools::ortools)
# set_project_optimizations(or_tools)
# set_project_warnings(or_tools)
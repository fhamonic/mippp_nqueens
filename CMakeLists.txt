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
add_executable(nqueens src/main.cpp)
target_include_directories(nqueens PUBLIC include)
target_link_libraries(nqueens mippp::mippp)

set_project_optimizations(nqueens)
set_project_warnings(nqueens)
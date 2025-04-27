cmake_minimum_required(VERSION 3.20)

project(
  nqueens
  VERSION 1.0
  LANGUAGES CXX)

# ################### Packages ####################
find_package(mippp REQUIRED)

# ################### LIB target ####################
add_executable(nqueens src/main.cpp)
target_link_libraries(nqueens mippp::mippp)

target_include_directories(nqueens PUBLIC include)
target_include_directories(nqueens PUBLIC $ENV{GUROBI_HOME}/include)


target_compile_options(nqueens PUBLIC -Wall -Wextra -Wshadow)
from conan import ConanFile
from conan.tools.cmake import CMake


class NQueensBenchmark(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain", "CMakeDeps"
    build_policy = "missing"

    def requirements(self):
        self.requires("mippp/0.2")

    def generate(self):
        print("Include directories:")
        for lib, dep in self.dependencies.items():
            if not lib.headers:
                continue
            for inc in dep.cpp_info.includedirs:
                print("\t" + inc)

    def build(self):
        cmake = CMake(self)
        cmake.configure(
            variables={
                "BUILD_DEPS": "ON",
                # "USE_CLP": "OFF",
                # "USE_CBC": "ON",
                # "USE_GLPK": "ON",
                # "USE_SCIP": "ON",
                # "USE_CPLEX": "ON",
                # "CPLEX_ROOT": "/home/plaiseek/Softwares/solvers/cplex-community/cplex",
            }
        )
        cmake.build()

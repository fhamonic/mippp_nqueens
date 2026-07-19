BUILD_DIR = build
BUILD_TYPE = gcc15_c++26
# BUILD_TYPE = debug

.PHONY: all test clean $(BUILD_DIR)

all: test

$(BUILD_DIR):
	conan build . -of=${BUILD_DIR} -b=missing -pr=${BUILD_TYPE}

test: $(BUILD_DIR)
	@cd $(BUILD_DIR) && \
	ctest --output-on-failure

clean:
	@rm -rf CMakeUserPresets.json
	@rm -rf $(BUILD_DIR)

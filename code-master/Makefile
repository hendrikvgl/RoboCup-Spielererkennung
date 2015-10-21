BUILD_DIR=/home/darwin/git/.build_clang_i386-pc-linux-gnu-arm-cross_T_Release 
CPUS=4

# This Makefile will be modified by the build script, don't change it!
# The build script sets the correct number of CPUS and the current build type.
# Afterwards when executing make, this file "redirects" the execution into the real build directory.
# This Makefile supports a general make with the implicit all target and a general target forwarding.

.PHONY: install clean all

all:
	cd $(BUILD_DIR) ; make -j $(CPUS) all | grep --color=always -v -e 'Leaving directory' -e 'Entering directory'

install:
	make all && cd $(BUILD_DIR) ; make -j $(CPUS) | grep --color=always -vi -e  'up-to-date' -e 'Leaving directory' -e 'Entering directory'

%:
	cd $(BUILD_DIR) ; make -j $(CPUS) $@ | grep --color=always -v -e 'Leaving directory' -e 'Entering directory'

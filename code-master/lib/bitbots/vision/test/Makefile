# This Makefile is in some kind a link to the Makefile in the project root.
# When invoked with no target is performs a make vision with the root Makefile
# Otherwise it's a target forward.

T=$(wildcard *.cpp)
S=$(T:.cpp=.x)

.PHONY: local clean all install

local:
	make $(S)

all:
	cd ../.. ; make all

clean:
	cd ../.. ; make clean

install:
	cd ../.. ; make install

%.x: %.cpp
	cd ../.. ; make $@

%:
	cd ../.. ; make $@

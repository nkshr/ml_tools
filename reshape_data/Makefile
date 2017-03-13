SRCS = reshape_data.cpp
OBJS = $(addsuffix .o, $(basename $(SRCS)))
CXX = g++
CXX_FLAGS = -std=c++11
all: $(OBJS)
	$(CXX) $(CXX_FLAGS) $(OBJS) -o reshape_data

%.o: %.cpp
	$(CXX) $(CXX_FLAGS) -o $@ -c $^
.PHONY: clean

clean:
	rm -f .o
	rm -f ./reshape_data

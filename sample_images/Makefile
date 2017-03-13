SRCS = sample_images.cpp
OBJS = $(addsuffix .o, $(basename $(SRCS)))
CXX = g++
CXX_FLAGS = -std=c++11

all: $(OBJS)
	$(CXX) $(CXX_FLAGS) $(OBJS) -o sample_images

%.o: %.cpp
	$(CXX) $(CXX_FLAGS) -o $@ -c $^

.PHONY: clean
clean:
	rm -f *.o
	rm -f ./sample_images

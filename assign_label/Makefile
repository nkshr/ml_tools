DEBUG_AL = y
AL_SRCS = assign_label.cpp subsynset_checker.cpp
SD_SRCS = subsynsets_debugger.cpp

CXX_FLAGS = -std=c++11
AL_OBJS = $(addsuffix .o, $(basename $(AL_SRCS)))
SD_OBJS = $(addsuffix .o, $(basename $(SD_SRCS)))

ifeq ($(DEBUG_AL),y)
	CXX_FLAGS += -DDEBUG_AL
endif

all: assign_label subsynsets_debugger

assign_label: $(AL_OBJS)
	g++ $(AL_OBJS) -o assign_label $(CXX_FLAGS)

subsynsets_debugger: $(SD_OBJS)
	g++ $(SD_SRCS) -o subsynsets_debugger $(CXX_FLAGS)

%.o: %.cpp
	g++ $(CXX_FLAGS) -o $@ -c $^

.PHONY: clean
clean:
	rm -f *.o
	rm -f assign_label
	rm -f subsynsets_debugger

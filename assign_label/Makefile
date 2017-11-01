DEBUG_ASSIGN_LABEL = y
ASSIGN_LABEL_SRCS = assign_label.cpp subsynset_checker.cpp
SUBSYNSET_DEBUGGER_SRCS = subsynset_debugger.cpp

CXX_FLAGS = -std=c++11
ASSIGN_LABEL_OBJS = $(addsuffix .o, $(basename $(ASSIGN_LABEL_SRCS)))
SUBSYNSET_DEBUGGER_OBJS = $(addsuffix .o, $(basename $(SUBSYNSET_DEBUGGER_SRCS)))

ifeq ($(DEBUG_ASSIGN_LABEL),y)
	CXX_FLAGS += -DDEBUG_ASSIGN_LABEL
endif

all: assign_label subsynsets_debugger

assign_label: $(ASSIGN_LABEL_OBJS)
	g++ $(ASSIGN_LABEL_OBJS) -o assign_label $(CXX_FLAGS)

subsynset_debugger: $(SUBSYNSET_DEBUGGER_OBJS)
	g++ $(SUBSYNSET_DEBUGGER_SRCS) -o subsynset_debugger $(CXX_FLAGS)

%.o: %.cpp
	g++ $(CXX_FLAGS) -o $@ -c $^

.PHONY: clean
clean:
	rm -f *.o
	rm -f assign_label
	rm -f subsynset_debugger

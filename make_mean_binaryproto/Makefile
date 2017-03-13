#!/bin/sh

DEBUG_SS = n
TIME_SS = y

SRCS = make_mean_binaryproto.cpp
OBJS = $(addsuffix .o, $(basename $(SRCS)))

CAFFE_INC_DIR = -I/home/mg6/caffe/build/install/include
CAFFE_LIB_DIR = -L/home/mg6/caffe/build/lib
CAFFE_LIB = -lcaffe

OPENCV_INC_DIR = `pkg-config --cflags-only-I opencv`
OPENCV_LIB_DIR = `pkg-config --libs-only-L opencv`
OPENCV_LIBS = `pkg-config --libs-only-l opencv`

GLFW_INC_DIR = -I./GLFW/include
GLFW_LIB_DIR = -L./GLFW/lib
GLFW_LIB = -lglfw3

GFLAGS_INC_DIR = -I./gflags/include
GFLAGS_LIB_DIR = -L./gflags/lib 
GLFAGS_LIB = -lgflags

GLOG_INC_DIR = -I./glog/include
GLOG_LIB_DIR = -L./glog/lib 
GLOG_LIB = -lglog

CUBLAS_INC_DIR = -I/usr/local/cuda-8.0/targets/x86_64-linux/include

CXX = /usr/bin/c++

CXX_FLAGS =  -fPIC -Wall -Wno-sign-compare -Wno-uninitialized -O3 -DNDEBUG  

CXX_INC_DIR = $(OPENCV_INC_DIR) $(GLFW_INC_DIR) $(CAFFE_INC_DIR) $(GFLAGS_INC_DIR) $(GLOG_INC_DIR) $(CUBLAS_INC_DIR)

LDLIBS = -lcaffe -lproto -lboost_system -lboost_thread -lboost_filesystem -lboost_chrono -lboost_date_time -lboost_atomic -lpthread -lpthread -lprotobuf $(OPENCV_LIBS) $(GLFW_LIBS)

LDFLAGS = $(CAFFE_LIB_DIR) $(OPENCV_LIB_DIR) $(GLFW_LIB_DIR) $(GFLAGS_LIB_DIR) $(GLOG_LIB_DIR) 

all: $(OBJS)
	$(CXX) $(CXX_DEFINES) $(CXX_INC_DIR) $(CXX_FLAGS) $(OBJS) $(LDFLAGS) $(LDLIBS) -o make_mean_binaryproto

%.o: %.cpp
	$(CXX) $(CXX_DEFINES) $(CXX_INC_DIR) $(CXX_FLAGS) -o $@ -c $^

.PHONY: clean
clean:
	rm -f *.o
	rm -f ./make_mean_binaryproto

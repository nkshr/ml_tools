
all:
	g++ resize_images_for_imagenet.cpp -o resize_images_for_imagenet -std=c++11 `pkg-config --libs opencv` `pkg-config --cflags opencv` -lpthread

.PHONY: clean

clean:
	rm -f resize_images_for_imagenet

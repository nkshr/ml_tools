all:
	g++ blur_image.cpp -o blur_image `pkg-config --cflags --libs opencv`

install:
	cp ./blur_image /usr/local/bin
	cp ./blur_images.py /usr/local/bin
clean:
	rm ./blur_image

.PHONY: clean

#!/bin/bash

fname=$(basename $1)
ext="${fname##*.}"
fname="${fname%.*}"

case $ext in
    "train")
	cp $1 ./.caffe.train
	gnuplot ./train_loss_iter.gnuplot
	pngname=${1}_loss_iter.png
	rm -f ./.caffe.train
	mv  ./.train_loss_iter.png $pngname;;
    "test")
	cp $1 ./.caffe.test
	gnuplot -p ./test_acc_iter.gnuplot
	pngname=${1}_acc_iter.png
	echo $pngname
	mv ./.test_acc_iter.png $pngname;
	
	gnuplot -p ./test_loss_iter.gnuplot
	pngname=${1}_loss_iter.png
	echo $pngname
	rm -f ./.caffe.test
	mv ./.test_loss_iter.png $pngname;;
    *) echo Invalid arguments.;; 
esac

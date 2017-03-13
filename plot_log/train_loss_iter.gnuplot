reset
set terminal png
set output ".train_loss_iter.png"
set style data lines
set key right

set title "Training loss vs. training iterations"
set xlabel "Training iterations"
set ylabel "Training loss"
plot ".caffe.train" using 1:3 title "train"
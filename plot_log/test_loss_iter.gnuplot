reset
set terminal png
set output ".test_loss_iter.png"
set style data lines
set key right

set title "Test loss vs. test iterations"
set xlabel "Test iterations"
set ylabel "Test loss"
plot ".caffe.test" using 1:4 title "test"
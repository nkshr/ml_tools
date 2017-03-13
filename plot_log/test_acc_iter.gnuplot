reset
set terminal png
set output ".test_acc_iter.png"
set style data lines
set key right

set title "Test accuracy vs. test iterations"
set xlabel "Test iterations"
set ylabel "Test accuracy"
plot ".caffe.test" using 1:3 title "test"
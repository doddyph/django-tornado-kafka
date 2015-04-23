## output as jpeg image
#set terminal jpeg size 500,500
# output as png image
set terminal jpeg

# aspect ratio of the graph
#set size 1, 1
set size 1, 0.8

# the file write to
set output "result.jpg"
#set output "result.png"

# the graph title
set title "Benchmark Result"

# the legend key place
set key left top

# draw gridlines oriented on the y axis
set grid y

# the x-axis label
set xlabel "Requests"

# the y-axis label
set ylabel "Time (ms)"

# use tabs as the delimiter instead of spaces (default)
set datafile separator '\t'

# plot the data
#plot "result.txt" every ::2 using 5 title 'response time' with lines
plot "result.txt" using 3 smooth sbezier with lines title 'ctime', \
    "result.txt" using 4 smooth sbezier with lines title 'dtime', \
    "result.txt" using 5 smooth sbezier with lines title 'ttime', \
    "result.txt" using 6 smooth sbezier with lines title 'wait'
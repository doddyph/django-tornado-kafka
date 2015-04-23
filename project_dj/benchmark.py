#!/usr/bin/env python
#
# A simple benchmark of tornado's HTTP stack.
# Requires 'ab' to be installed.
#
# Running without profiling:
# demos/benchmark/benchmark.py
# demos/benchmark/benchmark.py --quiet --num_runs=5|grep "Requests per second"
#
# Running with profiling:
#
# python -m cProfile -o /tmp/prof demos/benchmark/benchmark.py
# python -m pstats /tmp/prof
# % sort time
# % stats 20

from tornado.options import define, options, parse_command_line
import subprocess

define('wshost', type=str, default="localhost")
define('wsport', type=int, default=8080)

# Increasing --n without --keepalive will eventually run into problems
# due to TIME_WAIT sockets
define("n", type=int, default=100)
define("c", type=int, default=100)
define("keepalive", type=bool, default=False)
define("quiet", type=bool, default=False)

# Repeat the entire benchmark this many times (on different ports)
# This gives JITs time to warm up, etc.  Pypy needs 3-5 runs at
# --n=15000 for its JIT to reach full effectiveness
define("num_runs", type=int, default=1)


def main():
    parse_command_line()
    for i in xrange(options.num_runs):
        run()


def run():
    args = ["ab"]
    args.extend(["-n", str(options.n)])
    args.extend(["-c", str(options.c)])
    if options.keepalive:
        args.append("-k")
    if options.quiet:
        # just stops the progress messages printed to stderr
        args.append("-q")
    args.extend(["-e", "results.csv"])
    args.extend(["-g", "results.txt"])
    args.append("http://%s:%d/demo/" % (options.wshost, options.wsport))
    subprocess.Popen(args)


if __name__ == '__main__':
    main()
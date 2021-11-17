#!/bin/sh
yosys -q -s ../synth_74.ys -p "tee -o serv.stat stat -liberty ../74ac.lib" ~/yosys/serv/rtl/*.v && cat serv.stat

.PHONY: all clean sim_counter

all: boneless.net

%.json: ../benchmarks/%.v ../74ac.lib ../74_models.v ../74_adder.v ../74_dffe.v ../74_mux.v ../synth_74.ys
	yosys -q -s ../synth_74.ys -p "write_json $@" $<

serv.json serv.eblif: ~/yosys/serv/rtl/*.v ../74ac.lib ../74_models.v ../74_adder.v ../74_dffe.v ../74_mux.v ../synth_74.ys
	# We omit -cname and -iname because the output nets actually have more useful names.
	yosys -q -s ../synth_74.ys -p "write_json $@; write_blif -conn serv.eblif" ~/yosys/serv/rtl/*.v

%.net: %.json generate_netlist.py parts.py
	python3 generate_netlist.py $<

clean:
	rm -f *.net *.json *.erc *.log serv.eblif place.png *.rpt *.place

VTR_PATH=~/yosys/vtr-verilog-to-routing
serv.place: serv.eblif 74xx_fpga.xml
	$(VTR_PATH)/vpr/vpr 74xx_fpga.xml $< --pack --place \
		--sweep_dangling_primary_ios off --const_gen_inference comb --sweep_dangling_blocks off --netlist_verbosity 2 --alpha_clustering 0.1 --beta_clustering 0.0 \
		--graphics_commands "set_draw_block_internals 1; set_nets 2; save_graphics place.png" \
		--timing_analysis off

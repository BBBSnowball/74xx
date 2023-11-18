.PHONY: all clean sim_counter

all: serv.net

%.json: ../benchmarks/%.v ../74ac.lib ../74_models.v ../74_adder.v ../74_dffe.v ../74_mux.v ../synth_74.ys
	yosys -q -s ../synth_74.ys -p "write_json $@" $<

serv.json serv.eblif: ../../serv/rtl/*.v ../74ac.lib ../74_models.v ../74_adder.v ../74_dffe.v ../74_mux.v ../synth_74.ys
	# We omit -cname and -iname because the output nets actually have more useful names.
	yosys -q -s ../synth_74.ys -p "write_json $@; write_blif -conn serv.eblif" ../../serv/rtl/*.v

%.net: %.json generate_netlist.py parts.py
	python3 generate_netlist.py $<

clean:
	rm -f *.net *.json *.erc *.log serv.eblif place.png *.rpt *.place

VTR_PATH=../../vtr-verilog-to-routing
serv.place: serv.eblif 74xx_fpga.xml
	sed -E <serv.eblif >serv2.eblif 's/ \S+=[$$](false|true|undef)//g'
	$(VTR_PATH)/vpr/vpr 74xx_fpga.xml serv2.eblif \
		--netlist_verbosity 2 --alpha_clustering 0.0 --beta_clustering 0.0 --allow_unrelated_clustering on \
		--clustering_pin_feasibility_filter off --balance_block_type_utilization off \
		--graphics_commands "set_draw_block_internals 1; set_nets 2; set_macros 1; save_graphics place{i}.png" \
		--timing_analysis off
	mv serv2.place serv.place

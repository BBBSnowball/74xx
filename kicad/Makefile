.PHONY: all clean sim_counter

all: boneless.net

%.json: ../benchmarks/%.v ../74ac.lib ../74_models.v ../74_adder.v ../74_dffe.v ../74_mux.v ../synth_74.ys
	yosys -q -s ../synth_74.ys -p "write_json $@" $<

serv.json serv.eblif: ~/yosys/serv/rtl/*.v ../74ac.lib ../74_models.v ../74_adder.v ../74_dffe.v ../74_mux.v ../synth_74.ys
	yosys -q -s ../synth_74.ys -p "write_json $@; write_blif -cname -iname -conn serv.eblif" ~/yosys/serv/rtl/*.v

%.net: %.json generate_netlist.py parts.py
	python3 generate_netlist.py $<

clean:
	rm -f *.net *.json *.erc *.log serv.eblif place.png *.rpt *.place

VTR_PATH=~/yosys/vtr-verilog-to-routing
serv.place: serv.eblif
	# VTR doesn't support .search and it doesn't accept if add models with .names lines anyway
	# so we rewrite the .subckt to .names.
	#NOTE We are also using .names for the DFF because we don't want it to pack logic and registers into the same cell.
	#     That's why we disable timing analysis to avoid it complaining about all the loops.
	sed -E <serv.eblif >serv2.eblif \
		-e 's/^\.subckt \\74AC04_6x1NOT A=(\S+) Y=(\S+)$$/.names \1 \2\n1 0/' \
		-e 's/^\.subckt \\74AC32_4x1OR2 A=(\S+) B=(\S+) Y=(\S+)$$/.names \1 \2 \3\n1 - 1\n- 1 1/' \
		-e 's/^\.subckt \\74AC08_4x1AND2 A=(\S+) B=(\S+) Y=(\S+)$$/.names \1 \2 \3\n1 1 1/' \
		-e 's/^\.subckt \\74AC00_4x1NAND2 A=(\S+) B=(\S+) Y=(\S+)$$/.names \1 \2 \3\n0 0 0\n- - 1/' \
		-e 's/^\.subckt \\74AC10_3x1NAND3 A=(\S+) B=(\S+) C=(\S+) Y=(\S+)$$/.names \1 \2 \3 \4\n0 0 0 0\n- - - 1/' \
		-e 's/^\.subckt \\74AC86_4x1XOR2 A=(\S+) B=(\S+) Y=(\S+)$$/.names \1 \2 \3\n10 1\n01 1/' \
		-e 's/^\.subckt \\74AC74_2x1DFFSR C=(\S+) CLK=(\S+) D=(\S+) P=(\S+) Q=(\S+)$$/.names \1 \2 \3 \4 \5\n1111 1/'

	$(VTR_PATH)/vpr/vpr $(VTR_PATH)/vtr_flow/arch/custom_grid/custom_sbloc.xml serv2.eblif --pack --place \
		--absorb_buffer_luts off --sweep_dangling_primary_ios off --const_gen_inference comb --sweep_dangling_blocks off --netlist_verbosity 2 --alpha_clustering 0.1 --beta_clustering 0.0 \
		--graphics_commands "set_draw_block_internals 1; set_nets 2; save_graphics place.png" \
		--timing_analysis off
	mv serv2.place serv.place

.PHONY: all clean sim_counter

SERV_SRC ?= ../../serv
LIBS_74 ?= ../74ac.lib ../74_models.v ../74_adder.v ../74_dffe.v ../74_mux.v ../synth_74.ys
#VPR = ../../vtr-verilog-to-routing/vpr/vpr
VPR ?= vpr

all: serv.net serv.place serv_vpr_generated.kicad_pcb

%.json: ../benchmarks/%.v $(LIBS_74)
	yosys -q -s ../synth_74.ys -p "write_json $@" $<

serv.json serv.eblif: $(SERV_SRC)/rtl/*.v $(LIBS_74)
	# We omit -cname and -iname because the output nets actually have more useful names.
	yosys -q -s ../synth_74.ys -p "write_json $@; write_blif -conn serv.eblif" $(SERV_SRC)/rtl/*.v

%.net: %.json generate_netlist.py parts.py
	python3 generate_netlist.py $<

clean:
	rm -f *.net *.json *.erc *.log serv.eblif place.png *.rpt *.place

serv.place: serv.eblif 74xx_fpga.xml
	sed -E <serv.eblif >serv2.eblif 's/( \S+=|^[.]conn +)[$$](false|true|undef)/\1unconn/g'
	rm -f serv2.place serv.place
	$(VPR) 74xx_fpga.xml serv2.eblif \
		--netlist_verbosity 2 --alpha_clustering 0.0 --beta_clustering 0.0 --allow_unrelated_clustering on \
		--clustering_pin_feasibility_filter off --balance_block_type_utilization off \
		--graphics_commands "set_draw_block_internals 1; set_nets 2; set_macros 1; save_graphics place{i}.png" \
		--timing_analysis off \
		|| true   ;# ignore errors, for now
	mv serv2.place serv.place

serv_vpr_generated.kicad_net serv_vpr_generated.kicad_pcb: serv.json serv.place serv2.net generate_netlist2.py generate_netlist.py parts.py
	python3 generate_netlist2.py serv_vpr_generated serv.json serv2.net serv.place

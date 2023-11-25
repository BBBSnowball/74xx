import skidl
import json
import sys
import os.path
import pprint
import pdb
import xml.etree.ElementTree as ET
import re
import kinet2pcb
import pcbnew
import logging

#from parts import *
from generate_netlist import *

def xy_mm(x, y):
    return pcbnew.VECTOR2I(round(x*pcbnew.PCB_IU_PER_MM), round(y*pcbnew.PCB_IU_PER_MM))

if __name__ == '__main__':
    # arguments:
    # 1. output prefix
    # 2. serv.json: logic primitives and nets, generated by Yosys
    # 3. serv2.net: XML netlist, generated by VPR -> which primitives are part of the same chip
    # 4. serv.place: table of chip positions

    verbose = bool(int(os.environ.get("VERBOSE", "0")))

    _, output_prefix, json_file, xml_netlist_file, placement_file, input_board_file, grid_size = sys.argv

    with open(json_file) as f:
        data = json.load(f)

    xml_netlist = ET.parse(xml_netlist_file)
    netlist_rootblock = xml_netlist.getroot()

    clb_placement = []
    with open(placement_file) as f:
        #placement_text = f.read()
        line_no = 0
        for line in f:
            line_no += 1
            cells = line.split("\t")
            if len(cells) >= 7 and cells[1] == "":
                cells = cells[0:1] + cells[2:]
            if len(cells) >= 6 and cells[5][0] == "#":
                clbnum = int(cells[5][1:].strip())
                while len(clb_placement) < clbnum+1:
                    clb_placement.append(None)
                clb_placement[clbnum] = {
                    "one_of_the_names": cells[0],
                    "x": int(cells[1]),
                    "y": int(cells[2]),
                    "subblk": int(cells[3]),
                    "layer": int(cells[4]),
                }
            elif line_no > 5:
                print("WARN: Couldn't parse line in placement file: %r -> %r" % (line, cells))

    top = get_toplevel(data)
    nets = create_nets(top)
    cells = top['cells']

    bitval_to_netname = {}
    for k,v in top['netnames'].items():
        if len(v["bits"]) == 1:
            bitval = v["bits"][0]
            if bitval not in ["0", "1", "z", "x"]:
                if bitval not in bitval_to_netname:
                    bitval_to_netname[bitval] = []
                if k not in bitval_to_netname[bitval]:
                    bitval_to_netname[bitval].append(k)
        # What is the correct order? Does it start with MSB or LSB?
        # -> o_dbus_adr has its first two bits as "0" and we only have DFFs for bits 2 to 31 so first is probably LSB
        for i, bitval in enumerate(v["bits"]):
            if bitval not in ["0", "1", "z", "x"]:
                if bitval not in bitval_to_netname:
                    bitval_to_netname[bitval] = []
                name = "%s[%d]" % (k, i)
                if name not in bitval_to_netname[bitval]:
                    bitval_to_netname[bitval].append(name)
    if verbose:
        for bitval,v in bitval_to_netname.items():
            print("bit %d is net %s" % (bitval,v))

    cells_by_output_name = {}
    for cellname,v in cells.items():
        for port,direction in v["port_directions"].items():
            if direction == "output":
                for c in v["connections"][port]:
                    for netname in bitval_to_netname[c]:
                        cells_by_output_name[netname] = cellname
    if verbose:
        for k,v in cells_by_output_name.items():
            print("net %s is output of cell %s" % (k,v))

    chips = []
    for clb in netlist_rootblock:
        if clb.tag != "block":
            continue

        clb_instance = clb.attrib["instance"]
        mode = clb.attrib["mode"]

        if re.match("\A(io|io_in|io_out)\[\d+\]\Z", clb_instance):
            # let's ignore IOs, for now
            continue
        m = re.match("\Aclb\[(\d+)\]\Z", clb_instance)
        if not m:
            print("WARN: CLB instance name is not as expected!")
            clbnum = 0
            clbinfo = None
        else:
            clbnum = int(m[1])
            if clbnum < len(clb_placement) and clb_placement[clbnum]:
                clbinfo = clb_placement[clbnum]
            else:
                print("WARN: CLB number doesn't exist in placement file! (%s > %s)" % (clbnum, len(clb_placement)-1))
                clbinfo = None
        if not clbinfo:
            clbinfo = { "x": 0, "y": 0 }

        if verbose:
            print("CLB: %s (%s), %r" % (clb_instance, mode, clbinfo))

        parts = []
        for part in clb:
            if part.tag != "block":
                continue
            name = part.attrib["name"]
            if verbose:
                print("  part %s: %s" % (part.attrib["instance"], name))
            if name == "open" or mode in ["inpad", "outpad"]:
                pass
            elif name not in cells_by_output_name:
                print("ERROR: Part not found in JSON netlist: clb=%r, part=%r" % (clb_instance, name))
            else:
                parts.append({"name": name, "name_in_json": cells_by_output_name[name], "info": top['cells'][cells_by_output_name[name]] })

        if len(parts) > 0:
            chips.append({
                "clbnum": clbnum,
                "type": "\\" + mode,
                "x": clbinfo["x"],
                "y": clbinfo["y"],
                "parts": parts,
            })

    for chip in chips:
        create_chips({chip["type"]: [part["info"] for part in chip["parts"]]}, nets)

    #skidl.ERC()
    skidl.generate_netlist(file_=output_prefix+".kicad_net")
    # direct use of kinet2pcb because generate_pcb() is only available in newer skidl (newer than newest release)
    input_board = pcbnew.LoadBoard(input_board_file) if input_board_file != "" else None
    brd_filename = output_prefix + ".kicad_pcb"
    kinet2pcb.kinet2pcb(default_circuit, brd_filename, None, input_board=input_board)

    skidl_netname_to_netname = {}
    for bitval,net in nets.items():
        if type(bitval) == int and bitval in bitval_to_netname:
            skidl_netname_to_netname[net.name] = bitval_to_netname[bitval]

    #mm_per_chip_x, mm_per_chip_y = 20, -30
    #mm_per_chip_x, mm_per_chip_y = 15, -25
    mm_per_chip_x, mm_per_chip_y = 13, -25
    if len(chips) != len(all_chips):
        print("ERROR: We expected to create %d chips but there are actually %d chips! Positions will not be updated!" % (len(chips), len(all_chips)))
    else:
        brd = pcbnew.LoadBoard(brd_filename)

        caps = [c for c in default_circuit.parts if c.name == "C"]
        for i in range(len(chips)):
            chip = chips[i]
            skidl_chip = all_chips[i]
            fp = brd.FindFootprintByReference(skidl_chip.ref)
            if fp:
                # coordinate 0,0 seems to be bottom-left in place2.png
                # (place3.png is newer than serv.place because vpr has crashed)
                xy = xy_mm(mm_per_chip_x*chip["x"], mm_per_chip_y*chip["y"])
                fp.SetPosition(xy)
            else:
                print("WARN: Couldn't find footprint with ref=%r" % (skidl_chip.ref))
                xy = xy_mm(0, 0)

            # see https://www.atomic14.com/2022/10/24/kicad-python-scripting-cheat-sheet-copy.html
            pcb_txt = pcbnew.PCB_TEXT(brd)
            #pcb_txt.SetText(("clb[%d]\n%s" % (chip["clbnum"], chip["type"][1:])) + "".join("\n" + part["name"] for part in chip["parts"]))
            pcb_txt.SetText("clb[%d]\n%s" % (chip["clbnum"], chip["type"][1:]))
            pcb_txt.SetPosition(xy + xy_mm(7.6/2, -1.6))
            if fp:
                pcb_txt.SetPosition(fp.Reference().GetPosition() + xy_mm(0, -1.0))
            pcb_txt.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
            pcb_txt.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_BOTTOM)
            #pcb_txt.Rotate(xy_mm(x, y), text["angle"])
            pcb_txt.SetTextSize(xy_mm(1, 1))
            pcb_txt.SetTextThickness(round(0.15 * pcbnew.PCB_IU_PER_MM))
            #pcb_txt.SetLayer(pcbnew.F_SilkS)
            pcb_txt.SetLayer(pcbnew.User_9)
            brd.Add(pcb_txt)

            if fp:
                pcb_txt = pcbnew.PCB_TEXT(brd)
                pcb_txt.SetText(chip["type"][1:])
                pcb_txt.SetPosition(fp.Value().GetPosition())
                pcb_txt.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
                pcb_txt.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
                pcb_txt.SetTextSize(xy_mm(1, 1))
                pcb_txt.SetTextThickness(round(0.15 * pcbnew.PCB_IU_PER_MM))
                pcb_txt.SetLayer(pcbnew.F_SilkS)
                brd.Add(pcb_txt)
                fp.Value().SetVisible(False)

                for pad in fp.Pads():
                    if pad.GetNetname() == "__NOCONNECT":
                        # shouldn't be connected but all of them are connected to each other -> let's fix that
                        # https://github.com/devbisme/WireIt/blob/master/WireIt.py#L610
                        cnct = brd.GetConnectivity()
                        cnct.Remove(pad)
                        no_connect = 0  # PCBNEW ID for the no-connect net.
                        pad.SetNetCode(no_connect)

                for pad in skidl_chip:
                    if pad.func == skidl.Pin.OUTPUT and pad.net and pad.net.name[0] != "$" and pad.net.name in skidl_netname_to_netname:
                        netnames = skidl_netname_to_netname[pad.net.name]
                        netname = sorted(netnames, key = lambda x: len(x))[0]
                        kicad_pad = fp.FindPadByNumber(int(pad.num))
                        pcb_txt = pcbnew.PCB_TEXT(brd)
                        pcb_txt.SetText(netname)
                        pcb_txt.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
                        pcb_txt.SetTextSize(xy_mm(0.7, 0.7))
                        pcb_txt.SetTextThickness(round(0.1 * pcbnew.PCB_IU_PER_MM))
                        pcb_txt.SetLayer(pcbnew.F_SilkS)
                        if int(kicad_pad.GetNumber()) <= 7:
                            if False:
                                pcb_txt.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_RIGHT)
                                pcb_txt.SetPosition(kicad_pad.GetPosition() + xy_mm(-1, 0))
                            else:
                                # test in Kicad with: pcb_txt = [d for d in brd.GetDrawings() if d.IsSelected()][0]
                                pcb_txt.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
                                #pcb_txt.SetPosition(kicad_pad.GetPosition() + xy_mm(-2, 0))
                                #pcb_txt.Rotate(pcb_txt.GetPosition(), pcbnew.EDA_ANGLE(270, pcbnew.DEGREES_T))
                                pcb_txt.SetPosition(kicad_pad.GetPosition() + xy_mm(-2, -2))
                                pcb_txt.Rotate(pcb_txt.GetPosition(), pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T))

                                line = pcbnew.PCB_SHAPE(brd)
                                line.SetShape(pcbnew.SHAPE_T_SEGMENT)
                                line.SetFilled(False)
                                line.SetStart(kicad_pad.GetPosition() + xy_mm(-1, -1))
                                line.SetEnd(pcb_txt.GetPosition() + xy_mm(+0.3, 0))
                                line.SetLayer(pcbnew.F_SilkS)
                                line.SetWidth(int(0.1 * pcbnew.PCB_IU_PER_MM))
                                brd.Add(line)
                        else:
                            if False:
                                pcb_txt.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
                                pcb_txt.SetPosition(kicad_pad.GetPosition() + xy_mm(+1, 0))
                            else:
                                pcb_txt.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
                                #pcb_txt.SetPosition(kicad_pad.GetPosition() + xy_mm(+2, 0))
                                pcb_txt.SetPosition(kicad_pad.GetPosition() + xy_mm(+2, -2))
                                pcb_txt.Rotate(pcb_txt.GetPosition(), pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T))

                                line = pcbnew.PCB_SHAPE(brd)
                                line.SetShape(pcbnew.SHAPE_T_SEGMENT)
                                line.SetFilled(False)
                                line.SetStart(kicad_pad.GetPosition() + xy_mm(+1, -1))
                                line.SetEnd(pcb_txt.GetPosition() + xy_mm(-0.3, 0))
                                line.SetLayer(pcbnew.F_SilkS)
                                line.SetWidth(int(0.1 * pcbnew.PCB_IU_PER_MM))
                                brd.Add(line)
                        brd.Add(pcb_txt)

                if i < len(caps):
                    cap = caps[i]
                    fp_cap = brd.FindFootprintByReference(cap.ref)
                    if fp_cap:
                        fp_cap.SetPosition(fp.GetPosition() + xy_mm(3.8-2.5, -4.9))

        if grid_size != "":
            width, height = map(int, grid_size.split("x"))
            x_min = 0
            y_min = 0
            x_max = width-1
            y_max = height-1
        else:
            x_min = min(chip["x"] for chip in chips)
            x_max = max(chip["x"] for chip in chips)
            y_min = min(chip["y"] for chip in chips)
            y_max = max(chip["y"] for chip in chips)
        x_min = x_min * mm_per_chip_x - 10
        x_max = x_max * mm_per_chip_x + 17.5
        y_min = y_min * mm_per_chip_y + 25
        y_max = y_max * mm_per_chip_y - 10
        edge_points = [xy_mm(x_min, y_min), xy_mm(x_min, y_max), xy_mm(x_max, y_max), xy_mm(x_max, y_min), xy_mm(x_min, y_min)]
        for i in range(4):
            a = edge_points[i]
            b = edge_points[i+1]
            line = pcbnew.PCB_SHAPE(brd)
            line.SetShape(pcbnew.SHAPE_T_SEGMENT)
            line.SetFilled(False)
            line.SetStart(a)
            line.SetEnd(b)
            line.SetLayer(pcbnew.Edge_Cuts)
            line.SetWidth(int(0.1 * pcbnew.PCB_IU_PER_MM))
            brd.Add(line)

        pcbnew.Refresh()
        pcbnew.ExportSpecctraDSN(brd, output_prefix + ".dsn")
        pcbnew.SaveBoard(brd_filename, brd)

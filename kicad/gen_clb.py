print("    <pb_type name=\"clb\">")
print("      <input name=\"I\" num_pins=\"14\" equivalent=\"full\"/>")
print("      <output name=\"O\" num_pins=\"14\" equivalent=\"full\"/>")
print("      <clock name=\"clk\" num_pins=\"2\"/>")

def print_mode(subckt_name, short_name, inputs, outputs, num_pb):
    outer_pb_name = "%s_x%d" % (short_name, num_pb)
    print("      <mode name=\"%s\">" % subckt_name)
    print("        <pb_type name=\"%s\" num_pb=\"1\">" % (outer_pb_name))
    for port in inputs:
        print("          <input name=\"%s\" num_pins=\"%d\"/>" % (port, num_pb))
    for port in outputs:
        print("          <output name=\"%s\" num_pins=\"%d\"/>" % (port, num_pb))
    print("          <pb_type name=\"%s\" blif_model=\".subckt \%s\" num_pb=\"%d\">" % (short_name, subckt_name, num_pb))
    for port in inputs:
        print("            <input name=\"%s\" num_pins=\"1\"/>" % (port))
    for port in outputs:
        print("            <output name=\"%s\" num_pins=\"1\"/>" % (port))
    print("            <delay_constant max=\"174e-12\" min=\"261e-12\" in_port=\"%s\" out_port=\"%s\"/>" % (
      " ".join(short_name + "." + port for port in inputs),
      " ".join(short_name + "." + port for port in outputs)
    ))
    print("          </pb_type>")
    print("          <interconnect>")
    i = 1
    for port in inputs:
        print("            <complete name=\"conn%d\" input=\"%s.%s\" output=\"%s.%s\"/>" % (i, outer_pb_name, port, short_name, port))
        i += 1
    for port in outputs:
        print("            <complete name=\"conn%d\" input=\"%s.%s\" output=\"%s.%s\"/>" % (i, short_name, port, outer_pb_name, port))
        i += 1
    print("          </interconnect>")
    print("        </pb_type>")
    print("        <interconnect>")
    i = 1
    for port in inputs:
        print("          <complete name=\"conn%d\" input=\"clb.I\" output=\"%s.%s\"/>" % (i, outer_pb_name, port))
        i += 1
    for port in outputs:
        print("          <complete name=\"conn%d\" input=\"%s.%s\" output=\"clb.O\"/>" % (i, outer_pb_name, port))
        i += 1
    print("        </interconnect>")
    print("      </mode>")

print_mode("74AC04_6x1NOT", "inv", ["A"], ["Y"], 6)
print_mode("74AC32_4x1OR2", "or2", ["A", "B"], ["Y"], 4)
print_mode("74AC08_4x1AND2", "and2", ["A", "B"], ["Y"], 4)
print_mode("74AC00_4x1NAND2", "nand2", ["A", "B"], ["Y"], 4)
print_mode("74AC10_3x1NAND3", "nand3", ["A", "B", "C"], ["Y"], 3)
print_mode("74AC86_4x1XOR2", "xor2_x4", ["A", "B"], ["Y"], 4)

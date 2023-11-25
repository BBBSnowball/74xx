
module serv_rf_top_no_ext
  #(
    parameter PRE_REGISTER = 1,
    /* Amount of reset applied to design
       "NONE" : No reset at all. Relies on a POR to set correct initialization
                 values and that core isn't reset during runtime
       "MINI" : Standard setting. Resets the minimal amount of FFs needed to
                 restart execution from the instruction at RESET_PC
     */
    parameter RESET_STRATEGY = "MINI",
    parameter WITH_CSR = 1,
    parameter RF_WIDTH = 2,
	parameter RF_L2D   = $clog2((32+(WITH_CSR*4))*32/RF_WIDTH))
  (
   input wire 	      clk,
   input wire 	      i_rst,
   input wire 	      i_timer_irq,
   output wire [31:0] o_ibus_adr,
   output wire 	      o_ibus_cyc,
   input wire [31:0]  i_ibus_rdt,
   input wire 	      i_ibus_ack,
   output wire [31:0] o_dbus_adr,
   output wire [31:0] o_dbus_dat,
   output wire [3:0]  o_dbus_sel,
   output wire 	      o_dbus_we ,
   output wire 	      o_dbus_cyc,
   input wire [31:0]  i_dbus_rdt,
   input wire 	      i_dbus_ack
  );

  serv_rf_top #(
    .PRE_REGISTER(PRE_REGISTER),
    .RESET_STRATEGY(RESET_STRATEGY),
    .WITH_CSR(WITH_CSR),
    .RF_WIDTH(RF_WIDTH)
  ) cpu (
    .i_ext_rd(0),
    .i_ext_ready(0),
    .clk(clk),
    .i_rst(i_rst),
    .i_timer_irq(i_timer_irq),
    .o_ibus_adr(o_ibus_adr),
    .o_ibus_cyc(o_ibus_cyc),
    .i_ibus_rdt(i_ibus_rdt),
    .i_ibus_ack(i_ibus_ack),
    .o_dbus_adr(o_dbus_adr),
    .o_dbus_dat(o_dbus_dat),
    .o_dbus_sel(o_dbus_sel),
    .o_dbus_we(o_dbus_we),
    .o_dbus_cyc(o_dbus_cyc),
    .i_dbus_rdt(i_dbus_rdt),
    .i_dbus_ack(i_dbus_ack),
  );

endmodule

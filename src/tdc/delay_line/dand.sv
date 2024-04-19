/*
   Filename: dand.v
    Version: 1.0
   Standard: Verilog
Description: Guaranteed to be an and chain independent of inputs
     Author: Phillip Marlowe (@phillipmmarlowe)
*/
`define AND_CELL sky130_fd_sc_hd__and2_1  
`timescale 1ns/1ps


module const_ones #(parameter N=64) (
    output [N-1:0] ones
);
    genvar i;
    generate
        for(i=0; i<N; i=i+1) begin : const_ones_genblk
            sky130_fd_sc_hd__conb_1 const_one(
                .HI(ones[i])
                `ifdef USE_POWER_PINS
                    , .VGND(VGND)
                    , .VPWR(VPWR)
                    , .VPB(VPWR)
                    , .VNB(VGND)
                `endif  // USE_POWER_PINS 
            );
        end
    endgenerate
endmodule


module dand #(parameter WIDTH_p=32) ( 
	input 			    pulse_i,
	output [WIDTH_p-1:0]	meas_o
);
    
	(* keep *) wire [WIDTH_p:0] ffout_w;
	(* keep *) wire [WIDTH_p-1:0]
	
	const_ones #(.N(WIDTH)) ones(
        .ones(a_int)
    );
	
	assign ffout_w[0] = pulse_i;
    assign ffout_o = ffout_w[WIDTH_p:1];
	
	generate 
		genvar i;
		for(i=0; i<WIDTH_p; i=i+1) begin : dand_genblk
		    `AND_CELL DA ( 
                .X(ffout_w[i+1]), 
                .A(a_int), 
                .B(ffout_w[i])
                `ifdef USE_POWER_PINS
                    , .VGND(VGND)
                    , .VPWR(VPWR)
                    , .VPB(VPB)
                    , .VNB(VNB)
                `endif  // USE_POWER_PINS
            );
        end
   	endgenerate

endmodule

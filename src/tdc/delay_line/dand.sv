/*
   Filename: dand.v
    Version: 1.0
   Standard: Verilog
Description: Guaranteed to be an and chain independent of inputs
     Author: Phillip Marlowe (@phillipmmarlowe)
*/
`define AND_CELL sky130_fd_sc_hd__and2_1  
`timescale 1ns/1ps

/*
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
*/

module dand #(parameter WIDTH=32) ( 
	input 			    pulse_i,
	output [WIDTH-1:0]	meas_o
);
    
	(* keep *) wire [WIDTH:0] ffout_w;
	(* keep *) wire [WIDTH-1:0] a_int;
	
	const_ones #(.N(WIDTH)) ones(
        .ones(a_int)
    );
	
	assign ffout_w[0] = pulse_i;
    assign meas_o = ffout_w[WIDTH:1];
	
	generate 
		genvar i;
		for(i=0; i<WIDTH; i=i+1) begin : dand_genblk
		    `AND_CELL DA ( 
                .X(ffout_w[i+1]), 
                .A(a_int[i]), 
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

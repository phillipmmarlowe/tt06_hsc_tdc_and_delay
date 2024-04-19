/*
   Filename: rca.v
    Version: 1.0
   Standard: Verilog
Description: Guaranteed to be an adder independent of inputs
     Author: Tyler Sheaves (@tsheaves)
*/
`define FA_CELL sky130_fd_sc_hd__fa_2 
// `timescale 1ns/1ps
/*
(* techmap_celltype = "$fa" *)
module fa_fixed(A, B, C, X, Y);
	parameter WIDTH = 1;

	(* force_downto *)
	input [WIDTH-1:0] A, B, C;
	(* force_downto *)
	output [WIDTH-1:0] X, Y;

	(* force_downto *)
	wire [WIDTH-1:0] t1, t2, t3;

    wire _TECHMAP_FAIL_ = WIDTH > 1;

    `FA_CELL FA ( 
        .COUT(X), 
        .CIN(C), 
        .A(A), 
        .B(B), 
        .SUM(Y)
        `ifdef USE_POWER_PINS
            , .VGND(VGND)
            , .VPWR(VPWR)
            , .VPB(VPWR)
            , .VNB(VGND)
        `endif  // USE_POWER_PINS 
    );

endmodule
*/
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

module const_zeros #(parameter N=64) (
    output [N-1:0] zeros
);

    genvar i;

    generate
        for(i=0; i<N; i=i+1) begin : const_zeros_genblk
            sky130_fd_sc_hd__conb_1 const_zero(
                .LO(zeros[i])
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


module rca_dl #(parameter WIDTH=32) ( 
	input 			    pulse,
	output  [WIDTH-1:0] meas
);

    (* keep *)	wire [WIDTH:0] 
        c;
    
    (* keep *)	wire [WIDTH-1:0]
        a_int, b_int;

    (* keep *) wire
        co;

	assign c[0] = pulse;
	assign co = c[WIDTH];
    
    const_ones #(.N(WIDTH)) ones(
        .ones(a_int)
    );
    
    const_zeros #(.N(WIDTH)) zeros(
        .zeros(b_int)
    );

	generate 
		genvar i;
		for(i=0; i<WIDTH; i=i+1) begin : rca_genblk
            (* keep *)
			fa_fixed FA( 
                .X(c[i+1]), 
                .C(c[i]), 
                .A(a_int[i]), 
                .B(b_int[i]), 
                .Y(meas[i]) 
            );
        end
   	endgenerate

endmodule

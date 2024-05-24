/*
   Filename: tdc_delay_line.sv
    Version: 1.0
   Standard: SystemVerilog 2012
Description: Create a delay line using vmacros
     Author: Tyler Sheaves (@tsheaves)
     Editted by Phillip Marlowe (@phillipmmarlowe)
*/
`timescale 1ns/1ps
module delay_line #(
    parameter N=64,
    parameter DL_TYPE="RCA"
    ) ( 
	input in,
	output [N-1:0] dl_out
);
	
    generate
	    case(DL_TYPE)
		    "DAND": begin : dl_genblk
                            dand #(.WIDTH(N)) dl (
			          .pulse_i(in),
                                  .meas_o(dl_out)
			     );
                 end
	    endcase
    endgenerate

endmodule

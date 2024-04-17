import cocotb
import cocotb.utils as utils
import csv
from cocotb.clock import Clock, Timer
from cocotb.triggers import ClockCycles, Timer, RisingEdge, FallingEdge
from cocotb.decorators import coroutine

# TODO: move elsewhere
class TDCCtrl:
    
    def __init__(self, clk_period, dut, n_sync_stages, is_inverted=False):
        
        self.clk_period=clk_period
        self.dut=dut
        self.n_sync_stages=n_sync_stages
        self.clock_launch_coru=None
        self.clock_capt_coru=None
        self.theta_ps=0
        self.n_samples=0

        self.src_ctrl = {
            "PG_IN"  : 0,
            "PG_TOG" : 1 
        }
        self.reg_bypass = {
            "BYPASS" : 1,
            "REG"    : 0
        }

        if(is_inverted):
            self.pulse_phases = [
                "FALL", 
                "SAT_FALL", 
                "RISE",
                "SAT_RISE"
            ]
        else:
            self.pulse_phases = [
                "SAT_RISE",
                "RISE",
                "SAT_FALL",
                "FALL"               
            ]

    @cocotb.coroutine
    def set_theta_ps(self, theta_ps):
        self.theta_ps=theta_ps
        yield cocotb.start_soon(self.__restart_clks__())
    
    @cocotb.coroutine
    def reset_design(self):
        yield cocotb.start_soon(self.__reset_design__())

    @cocotb.coroutine
    def pg_cfg(self, pg_src="PG_IN", pg_byp="PG_REG"):
        match (pg_src, pg_byp):
            case ("PG_IN", "PG_BYPASS"):
                yield cocotb.start_soon(self.__pg_in_byp_reg__())
            case ("PG_IN", "PG_REG"):
                yield cocotb.start_soon(self.__pg_in_reg__())
            case ("PG_TOG", "PG_BYPASS"):
                yield cocotb.start_soon(self.__pg_tog_byp_reg__())
            case ("PG_TOG", "PG_REG"):
                yield cocotb.start_soon(self.__pg_tog_reg__())
    
    @cocotb.coroutine
    def get_sample(self):
        yield cocotb.start_soon(self.__get_sample__()) 
    
    @cocotb.coroutine
    def start_clocks(self):
        yield cocotb.start_soon(self.__restart_clks__())

    async def __start_clks__(self):    
        # Start launch clk
        self.dut.ena.value = 0
        self.clock_launch_coru = cocotb.start_soon(
            Clock(self.dut.clk_launch, period=self.clk_period, units="ns").start()
        )
        await RisingEdge(self.dut.clk_launch)
        # Phase delay capture clk start
        if(self.theta_ps > 0):
            await Timer(self.theta_ps, units='ps')
        # Start capture clk
        self.clock_capt_coru   = cocotb.start_soon(
            Clock(self.dut.clk_capture, period=self.clk_period, units="ns").start()
        )
        await RisingEdge(self.dut.clk_capture)
        await RisingEdge(self.dut.clk_launch)
    
    async def __restart_clks__(self):
        enable_init = self.dut.ena.value
        self.dut.ena.value = 0
        if(self.clock_launch_coru != None):
            await RisingEdge(self.dut.clk_launch)
            self.clock_launch_coru.kill()
        if(self.clock_capt_coru != None):
            await RisingEdge(self.dut.clk_capture)
            self.clock_capt_coru.kill()
        self.clock_launch_coru = None
        self.clock_capt_coru = None
        start_clocks_thread = cocotb.start_soon(self.__start_clks__())
        await start_clocks_thread
        # Restore enable after clocks restart
        self.dut.ena.value = enable_init

    async def __reset_design__(self):
        enable_init = self.dut.ena.value
        self.dut.ena.value = 1
        self.dut.val_in.value = 0
        self.dut.pg_in.value = 0
        self.dut.rst_n.value = 0
        await RisingEdge(self.dut.clk_launch)
        self.dut.rst_n.value = 1
        self.dut.ena.value = enable_init
    
    async def __pg_in_byp_reg__(self):
        self.dut.pg_src.value = self.src_ctrl["PG_IN"]
        self.dut.pg_bypass.value = self.reg_bypass["BYPASS"]
    
    async def __pg_in_reg__(self):
        self.dut.pg_src.value = self.src_ctrl["PG_IN"]
        self.dut.pg_bypass.value = self.reg_bypass["REG"]

    async def __pg_tog_byp_reg__(self):
        self.dut.pg_src.value = self.src_ctrl["PG_TOG"]
        self.dut.pg_bypass.value = self.reg_bypass["BYPASS"]

    async def __pg_tog_reg__(self):
        self.dut.pg_src.value = self.src_ctrl["PG_TOG"]
        self.dut.pg_bypass.value = self.reg_bypass["REG"]

    async def __drive_valid__(self, n):
        self.dut.val_in.value = 1
        await ClockCycles(self.dut.clk_launch, n)
        self.dut.val_in.value = 0

    async def __stress_delay_line__(self, stress_val):
        self.dut.val_in.value = 1
        await ClockCycles(self.dut.clk_launch, n)
        self.dut.val_in.value = 0

    async def __get_sample__(self):
        '''
        If the pg is toggling and the clocks are active, samples can be collected
        '''
        assert self.dut.pg_src.value == self.src_ctrl["PG_TOG"]
        assert self.clock_launch_coru != None and self.clock_capt_coru != None
        enable_init = self.dut.ena.value
        self.dut.ena.value = 1              
        await RisingEdge(self.dut.pg_tog)                
        cocotb.start_soon(self.__drive_valid__(4))
        await RisingEdge(self.dut.val_out)                
        
        for phase in self.pulse_phases:
            await RisingEdge(self.dut.clk_capture)
            match(phase):
                case("FALL"):
                    assert self.dut.hw.value == 0
                case("SAT_FALL"):
                    assert self.dut.hw.value == 0
                case("RISE"):
                    assert self.dut.hw.value == 64
                case("SAT_RISE"):
                    assert self.dut.hw.value == 64

        self.dut.val_in.value = 0
        self.dut.ena.value = enable_init
        await RisingEdge(self.dut.clk_launch)

@cocotb.test()
async def test_git(dut):
    dut._log.info("Start")
    f_clk_ns = 54
    output_sync_stages = 1
    tdc_ctrl = TDCCtrl(
        clk_period=f_clk_ns, 
        dut=dut, 
        n_sync_stages=output_sync_stages
    )
    
    dut._log.info("Starting clocks.")
    clock_strt_thread = cocotb.start_soon(tdc_ctrl.start_clocks())
    await clock_strt_thread

    dut._log.info("Resetting design.")
    reset_thread = cocotb.start_soon(tdc_ctrl.reset_design())
    await reset_thread

    dut._log.info("Configuring the pulsegenerator to toggle w/ register bypass.")    
    pg_cfg_thread = cocotb.start_soon(tdc_ctrl.pg_cfg("PG_TOG", "PG_BYPASS"))
    await pg_cfg_thread
    
    dut._log.info("Capturing samples.")
    for theta_ps in range(1, 1001, 10):
        set_theta_thread = cocotb.start_soon(tdc_ctrl.set_theta_ps(theta_ps))
        await set_theta_thread
        get_samples_thread = cocotb.start_soon(tdc_ctrl.get_sample())
        await get_samples_thread

    dut._log.info("Configuring the pulsegenerator to toggle w/o register bypass.")    
    pg_cfg_thread = cocotb.start_soon(tdc_ctrl.pg_cfg("PG_TOG", "PG_REG"))
    await pg_cfg_thread
    
    dut._log.info("Capturing samples.")
    for theta_ps in range(1, 1001, 10):
        set_theta_thread = cocotb.start_soon(tdc_ctrl.set_theta_ps(theta_ps))
        await set_theta_thread
        get_samples_thread = cocotb.start_soon(tdc_ctrl.get_sample())
        await get_samples_thread        
    

from hwt.hdl.types.struct import HStruct
from hwt.hwIOs.std import HwIOSignal
from hwt.hwParam import HwParam
from hwt.hwModule import HwModule
from hwtLib.types.ctypes import uint32_t


class ExampleCls0(HwModule):
    """
    Some text before

    .. hwt-params::

    Some text after
    """

    def _config(self):
        self.PARAM0 = HwParam(
            HStruct((uint32_t, "a"),
                    (uint32_t, "b"))
        )
        self.PARAM1 = HwParam(HStruct((uint32_t, "c"),
                                    (uint32_t, "d")))

    def _declr(self):
        self.din = HwIOSignal()
        self.dout = HwIOSignal()._m()

    def _impl(self):
        self.dout(self.din)

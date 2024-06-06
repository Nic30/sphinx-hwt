from hwt.hdl.types.struct import HStruct
from hwt.hwIOs.std import HwIOSignal
from hwt.hwModule import HwModule
from hwt.hwParam import HwParam
from hwt.pyUtils.typingFuture import override
from hwtLib.types.ctypes import uint32_t


class ExampleCls0(HwModule):
    """
    Some text before

    .. hwt-params::

    Some text after
    """

    @override
    def hwConfig(self):
        self.PARAM0 = HwParam(
            HStruct((uint32_t, "a"),
                    (uint32_t, "b"))
        )
        self.PARAM1 = HwParam(HStruct((uint32_t, "c"),
                                    (uint32_t, "d")))

    @override
    def hwDeclr(self):
        self.din = HwIOSignal()
        self.dout = HwIOSignal()._m()

    @override
    def hwImpl(self):
        self.dout(self.din)

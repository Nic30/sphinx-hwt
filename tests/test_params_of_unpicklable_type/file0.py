from hwt.hdl.types.struct import HStruct
from hwt.interfaces.std import Signal
from hwt.synthesizer.param import Param
from hwt.synthesizer.unit import Unit
from hwtLib.types.ctypes import uint32_t


class ExampleCls0(Unit):
    """
    Some text before

    .. hwt-params::

    Some text after
    """

    def _config(self):
        self.PARAM0 = Param(
            HStruct((uint32_t, "a"),
                    (uint32_t, "b"))
        )
        self.PARAM1 = Param(HStruct((uint32_t, "c"),
                                    (uint32_t, "d")))

    def _declr(self):
        self.din = Signal()
        self.dout = Signal()._m()

    def _impl(self):
        self.dout(self.din)

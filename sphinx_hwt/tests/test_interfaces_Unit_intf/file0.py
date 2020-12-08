from hwt.synthesizer.unit import Unit
from hwt.interfaces.std import Signal


class ExampleCls0(Unit):
    """
    .. hwt-schematic::
    .. hwt-interfaces::
    """

    def _declr(self):
        self.din = Signal()
        self.dout = Signal()._m()

    def _impl(self):
        self.dout(self.din)

from hwt.interfaces.std import Signal
from hwt.synthesizer.unit import Unit


class ExampleCls0(Unit):
    """
    Some text before

    .. hwt-schematic::

    Some text after
    """
    def _declr(self):
        self.din = Signal()
        self.dout = Signal()._m()

    def _impl(self):
        self.dout(self.din)

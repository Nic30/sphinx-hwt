from hwt.hwIOs.std import HwIOSignal
from hwt.hwModule import HwModule


class ExampleCls0(HwModule):
    """
    Some text before

    .. hwt-schematic::

    Some text after
    """
    def _declr(self):
        self.din = HwIOSignal()
        self.dout = HwIOSignal()._m()

    def _impl(self):
        self.dout(self.din)

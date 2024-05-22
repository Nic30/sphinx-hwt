from hwt.hwModule import HwModule
from hwt.hwIOs.std import HwIOSignal


class ExampleCls0(HwModule):
    """
    Some text before

    .. hwt-params::

    Some text after
    """

    def _declr(self):
        self.din = HwIOSignal()
        self.dout = HwIOSignal()._m()

    def _impl(self):
        self.dout(self.din)

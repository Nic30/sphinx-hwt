from hwt.hwModule import HwModule
from hwt.hwIOs.std import HwIOSignal
from hwt.pyUtils.typingFuture import override


class ExampleCls0(HwModule):
    """
    Some text before

    .. hwt-params::

    Some text after
    """

    @override
    def hwDeclr(self):
        self.din = HwIOSignal()
        self.dout = HwIOSignal()._m()

    @override
    def hwImpl(self):
        self.dout(self.din)

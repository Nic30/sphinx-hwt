from hwt.hwIOs.std import HwIOSignal
from hwt.hwModule import HwModule
from hwt.pyUtils.typingFuture import override


class CustomSignal(HwIOSignal):
    "Doc for a CustomSignal class itself"


class ExampleCls0(HwModule):
    """
    .. hwt-io::
    """

    @override
    def hwDeclr(self):
        self.din = CustomSignal()
        self.dout = CustomSignal()._m()

    @override
    def hwImpl(self):
        self.dout(self.din)

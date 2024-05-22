from hwt.hwModule import HwModule
from hwt.hwIOs.std import HwIOSignal


class CustomSignal(HwIOSignal):
    "Doc for a CustomSignal class itself"


class ExampleCls0(HwModule):
    """
    .. hwt-io::
    """

    def _declr(self):
        self.din = CustomSignal()
        self.dout = CustomSignal()._m()

    def _impl(self):
        self.dout(self.din)

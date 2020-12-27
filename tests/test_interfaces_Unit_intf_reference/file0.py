from hwt.synthesizer.unit import Unit
from hwt.interfaces.std import Signal


class CustomSignal(Signal):
    "Doc for a CustomSignal class itself"


class ExampleCls0(Unit):
    """
    .. hwt-interfaces::
    """

    def _declr(self):
        self.din = CustomSignal()
        self.dout = CustomSignal()._m()

    def _impl(self):
        self.dout(self.din)

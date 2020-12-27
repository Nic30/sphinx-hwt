from hwt.synthesizer.unit import Unit
from hwt.interfaces.std import Signal
from hwt.synthesizer.param import Param


class ExampleCls0(Unit):
    """
    Some text before

    .. hwt-params::

    Some text after
    """

    def _config(self) -> None:
        self.PARAM0 = Param(0)
        self.PARAM1 = Param(1)

    def _declr(self):
        self.din = Signal()
        self.dout = Signal()._m()

    def _impl(self):
        self.dout(self.din)

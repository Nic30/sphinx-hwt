from hwt.hwModule import HwModule
from hwt.hwIOs.std import HwIOSignal
from hwt.hwParam import HwParam


class ExampleCls0(HwModule):
    """
    Some text before

    .. hwt-params::

    :ivar PARAM1: An extra doc of PARAM1
    :ivar PARAM0: An extra doc of PARAM0

    Some text after
    """

    def _config(self) -> None:
        self.PARAM0 = HwParam(0)
        self.PARAM1 = HwParam(1)

    def _declr(self):
        self.din = HwIOSignal()
        self.dout = HwIOSignal()._m()

    def _impl(self):
        self.dout(self.din)

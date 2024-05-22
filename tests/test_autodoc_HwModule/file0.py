from hwt.hwModule import HwModule
from hwt.hwIOs.std import HwIOSignal
from hwt.hwParam import HwParam


class ExampleCls0(HwModule):
    """
    SOMETHING

    Some text before

    .. hwt-autodoc::

    :ivar din: An extra doc of din
    :ivar dout: An extra doc of dout

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

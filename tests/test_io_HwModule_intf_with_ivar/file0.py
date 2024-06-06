from hwt.hwIOs.std import HwIOSignal
from hwt.hwModule import HwModule
from hwt.hwParam import HwParam
from hwt.pyUtils.typingFuture import override


class ExampleCls0(HwModule):
    """
    Some text before

    .. hwt-io::

    :ivar din: An extra doc of din
    :ivar dout: An extra doc of dout

    Some text after
    """

    def hwConfig(self) -> None:
        self.PARAM0 = HwParam(0)
        self.PARAM1 = HwParam(1)

    @override
    def hwDeclr(self):
        self.din = HwIOSignal()
        self.dout = HwIOSignal()._m()

    @override
    def hwImpl(self):
        self.dout(self.din)

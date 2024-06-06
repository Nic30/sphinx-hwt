from hwt.hwIOs.std import HwIOVectSignal
from hwt.hwModule import HwModule
from hwt.hwParam import HwParam
from hwt.pyUtils.typingFuture import override


def example_constructor():
    u = ExampleCls0()
    u.WIDTH = 32
    return u


class ExampleCls0(HwModule):
    """
    .. hwt-schematic:: example_constructor

    """

    @override
    def hwConfig(self)->None:
        self.WIDTH = HwParam(1)

    @override
    def hwDeclr(self):
        self.din0 = HwIOVectSignal(self.WIDTH)
        self.dout0 = HwIOVectSignal(self.WIDTH)._m()

        if self.WIDTH >= 3:
            self.din1 = HwIOVectSignal(self.WIDTH)
            self.dout1 = HwIOVectSignal(self.WIDTH)._m()

    @override
    def hwImpl(self):
        self.dout0(self.din0)

        if self.WIDTH >= 3:
            self.dout1(self.din1)

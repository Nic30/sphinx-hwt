from hwt.hwIOs.std import HwIOSignal
from hwt.hwModule import HwModule
from hwt.pyUtils.typingFuture import override


class ExampleCls0(HwModule):
    """
    .. hwt-components::
    """

    @override
    def hwDeclr(self):
        self.din = HwIOSignal()
        self.dout = HwIOSignal()._m()

    @override
    def hwImpl(self):
        self.dout(self.din)


class ExampleCls1(HwModule):
    """
    .. hwt-components::
    """

    @override
    def hwDeclr(self):
        self.din = HwIOSignal()
        self.dout = HwIOSignal()._m()

    @override
    def hwImpl(self):
        c0 = self.c0 = ExampleCls0()
        c0.din(self.din)
        self.dout(c0.dout)


class ExampleCls1x2(HwModule):
    """
    .. hwt-components::
    """

    @override
    def hwDeclr(self):
        self.din = HwIOSignal()
        self.dout = HwIOSignal()._m()

    @override
    def hwImpl(self):
        c0 = self.c0 = ExampleCls0()
        c1 = self.c1 = ExampleCls0()
        c0.din(self.din)
        c1.din(c0.din)
        self.dout(c1.dout)


class ExampleCls2(HwModule):
    """
    .. hwt-components::
    """

    @override
    def hwDeclr(self):
        self.din = HwIOSignal()
        self.dout = HwIOSignal()._m()

    @override
    def hwImpl(self):
        c0 = self.c0 = ExampleCls1()
        c0.din(self.din)
        self.dout(c0.dout)

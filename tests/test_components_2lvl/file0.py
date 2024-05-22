from hwt.hwModule import HwModule
from hwt.hwIOs.std import HwIOSignal


class ExampleCls0(HwModule):
    """
    .. hwt-components::
    """

    def _declr(self):
        self.din = HwIOSignal()
        self.dout = HwIOSignal()._m()

    def _impl(self):
        self.dout(self.din)


class ExampleCls1(HwModule):
    """
    .. hwt-components::
    """

    def _declr(self):
        self.din = HwIOSignal()
        self.dout = HwIOSignal()._m()

    def _impl(self):
        c0 = self.c0 = ExampleCls0()
        c0.din(self.din)
        self.dout(c0.dout)


class ExampleCls1x2(HwModule):
    """
    .. hwt-components::
    """

    def _declr(self):
        self.din = HwIOSignal()
        self.dout = HwIOSignal()._m()

    def _impl(self):
        c0 = self.c0 = ExampleCls0()
        c1 = self.c1 = ExampleCls0()
        c0.din(self.din)
        c1.din(c0.din)
        self.dout(c1.dout)


class ExampleCls2(HwModule):
    """
    .. hwt-components::
    """

    def _declr(self):
        self.din = HwIOSignal()
        self.dout = HwIOSignal()._m()

    def _impl(self):
        c0 = self.c0 = ExampleCls1()
        c0.din(self.din)
        self.dout(c0.dout)

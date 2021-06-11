from hwt.synthesizer.unit import Unit
from hwt.interfaces.std import Signal


class ExampleCls0(Unit):
    """
    .. hwt-components::
    """

    def _declr(self):
        self.din = Signal()
        self.dout = Signal()._m()

    def _impl(self):
        self.dout(self.din)


class ExampleCls1(Unit):
    """
    .. hwt-components::
    """

    def _declr(self):
        self.din = Signal()
        self.dout = Signal()._m()

    def _impl(self):
        c0 = self.c0 = ExampleCls0()
        c0.din(self.din)
        self.dout(c0.dout)


class ExampleCls1x2(Unit):
    """
    .. hwt-components::
    """

    def _declr(self):
        self.din = Signal()
        self.dout = Signal()._m()

    def _impl(self):
        c0 = self.c0 = ExampleCls0()
        c1 = self.c1 = ExampleCls0()
        c0.din(self.din)
        c1.din(c0.din)
        self.dout(c1.dout)


class ExampleCls2(Unit):
    """
    .. hwt-components::
    """

    def _declr(self):
        self.din = Signal()
        self.dout = Signal()._m()

    def _impl(self):
        c0 = self.c0 = ExampleCls1()
        c0.din(self.din)
        self.dout(c0.dout)

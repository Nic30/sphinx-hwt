from hwt.hwIOs.std import HwIOSignal
from hwt.hwIO import HwIO
from hwt.hwParam import HwParam
from ipCorePackager.constants import DIRECTION


class Intf1(HwIO):
    """

    .. hwt-params::
    .. hwt-io::

    """

    def _config(self):
        self.WIDTH = HwParam(16)

    def _declr(self):
        self.din0 = Intf0(masterDir=DIRECTION.IN)
        self.dout0 = Intf0()


class Intf0(HwIO):
    """
    Text before

    .. hwt-params::
    .. hwt-io::

    Text after
    """

    def _config(self):
        self.DATA_WIDTH = HwParam(8)

    def _declr(self):
        self.din = HwIOSignal(masterDir=DIRECTION.IN)
        self.dout = HwIOSignal()

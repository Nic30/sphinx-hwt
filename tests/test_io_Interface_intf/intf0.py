from hwt.hwIOs.std import HwIOSignal
from hwt.hwIO import HwIO
from hwt.hwParam import HwParam
from ipCorePackager.constants import DIRECTION


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

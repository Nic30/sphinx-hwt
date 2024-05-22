from hwt.hwIO import HwIO
from hwt.hwIOs.std import HwIOSignal
from hwt.hwParam import HwParam
from hwt.pyUtils.typingFuture import override
from ipCorePackager.constants import DIRECTION


class Intf0(HwIO):
    """
    Text before

    .. hwt-params::
    .. hwt-io::

    Text after
    """

    @override
    def hwConfig(self):
        self.DATA_WIDTH = HwParam(8)

    @override
    def hwDeclr(self):
        self.din = HwIOSignal(masterDir=DIRECTION.IN)
        self.dout = HwIOSignal()

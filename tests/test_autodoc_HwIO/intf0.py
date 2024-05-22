from hwt.hwIOs.std import HwIOSignal
from hwt.hwIO import HwIO
from hwt.hwParam import HwParam
from ipCorePackager.constants import DIRECTION


class Intf0(HwIO):
    """
    Text before

    .. hwt-autodoc::

    :ivar din: An extra doc for din
    :ivar dout: An extra doc for dout
    :ivar x: doc for x

    Text after
    """

    def _config(self):
        self.DATA_WIDTH = HwParam(8)

    def _declr(self):
        self.din = HwIOSignal(masterDir=DIRECTION.IN)
        self.dout = HwIOSignal()
        self.x = 123

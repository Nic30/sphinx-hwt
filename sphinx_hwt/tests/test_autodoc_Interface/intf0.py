from hwt.interfaces.std import Signal
from hwt.synthesizer.interface import Interface
from hwt.synthesizer.param import Param
from ipCorePackager.constants import DIRECTION


class Intf0(Interface):
    """
    Text before

    .. hwt-autodoc::

    :ivar din: An extra doc for din
    :ivar dout: An extra doc for dout
    :ivar x: doc for x

    Text after
    """

    def _config(self):
        self.DATA_WIDTH = Param(8)

    def _declr(self):
        self.din = Signal(masterDir=DIRECTION.IN)
        self.dout = Signal()
        self.x = 123

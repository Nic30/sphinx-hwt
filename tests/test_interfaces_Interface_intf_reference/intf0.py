from hwt.interfaces.std import Signal
from hwt.synthesizer.interface import Interface
from hwt.synthesizer.param import Param
from ipCorePackager.constants import DIRECTION


class Intf1(Interface):
    """

    .. hwt-params::
    .. hwt-interfaces::

    """

    def _config(self):
        self.WIDTH = Param(16)

    def _declr(self):
        self.din0 = Intf0(masterDir=DIRECTION.IN)
        self.dout0 = Intf0()


class Intf0(Interface):
    """
    Text before

    .. hwt-params::
    .. hwt-interfaces::

    Text after
    """

    def _config(self):
        self.DATA_WIDTH = Param(8)

    def _declr(self):
        self.din = Signal(masterDir=DIRECTION.IN)
        self.dout = Signal()

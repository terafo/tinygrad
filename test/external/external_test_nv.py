import unittest
from tinygrad import Device, dtypes, Tensor
from tinygrad.engine.schedule import create_schedule
from tinygrad.runtime.ops_nv import NVDevice
from tinygrad.features.search import Opt, OptOps
from test.test_linearizer_failures import helper_test_lin

from tinygrad.codegen.linearizer import Linearizer
from tinygrad.ops import LazyOp, BinaryOps, UnaryOps, ReduceOps, BufferOps, MemBuffer
from tinygrad.shape.shapetracker import ShapeTracker
from tinygrad.shape.view import View

class TestNV(unittest.TestCase):
  @classmethod
  def setUpClass(self):
    TestNV.d0: NVDevice = Device["NV"]
    TestNV.a = Tensor([0.,1.], device="NV").realize()
    TestNV.b = self.a + 1
    si = create_schedule([self.b.lazydata])[-1]
    TestNV.d0_runner = TestNV.d0.get_runner(*si.ast)
    TestNV.b.lazydata.buffer.allocate()

  def test_oor_kernels(self):
    ast = LazyOp(op=BufferOps.STORE, src=(LazyOp(op=UnaryOps.CAST, src=(LazyOp(op=ReduceOps.SUM, src=(LazyOp(op=UnaryOps.CAST, src=(LazyOp(op=BinaryOps.MUL, src=(LazyOp(op=BufferOps.LOAD, src=(), arg=MemBuffer(idx=1, dtype=dtypes.half, st=ShapeTracker(views=(View(shape=(1, 256, 1, 512, 4, 16, 4, 16), strides=(0, 100352, 0, 196, 0, 14, 0, 1), offset=-15, mask=((0, 1), (0, 256), (0, 1), (0, 512), (0, 4), (1, 15), (0, 4), (1, 15)), contiguous=False), View(shape=(256, 1, 512, 7, 7, 512, 3, 3), strides=(2097152, 0, 0, 128, 2, 4096, 1088, 17), offset=0, mask=None, contiguous=False))))), LazyOp(op=BufferOps.LOAD, src=(), arg=MemBuffer(idx=2, dtype=dtypes.half, st=ShapeTracker(views=(View(shape=(256, 1, 512, 7, 7, 512, 3, 3), strides=(25088, 0, 49, 7, 1, 0, 0, 0), offset=0, mask=None, contiguous=False),))))), arg=None),), arg=(dtypes.float, False)),), arg=((0, 3, 4), dtypes.float)),), arg=(dtypes.half, False)),), arg=MemBuffer(idx=0, dtype=dtypes.half, st=ShapeTracker(views=(View(shape=(1, 1, 512, 1, 1, 512, 3, 3), strides=(0, 0, 4608, 0, 0, 9, 3, 1), offset=0, mask=None, contiguous=True),)))) # noqa: E501
    opts = [Opt(op=OptOps.TC, axis=6, amt=2), Opt(op=OptOps.UPCAST, axis=0, amt=4), Opt(op=OptOps.UPCAST, axis=3, amt=0), Opt(op=OptOps.LOCAL, axis=1, amt=4), Opt(op=OptOps.LOCAL, axis=2, amt=3), Opt(op=OptOps.UPCAST, axis=1, amt=2)] # noqa: E501
    helper_test_lin(Linearizer(ast), opts=opts, failed_platforms=["NV"])

if __name__ == "__main__":
  unittest.main()


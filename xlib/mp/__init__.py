import multiprocessing

if multiprocessing.get_start_method() != "spawn":
    multiprocessing.set_start_method("spawn", force=True)

from .MPAtomicInt32 import MPAtomicInt32
from .MPSPSCMRRingData import MPSPSCMRRingData
from .MPWeakHeap import MPWeakHeap
from .MPWorker import MPWorker
from .PMPI import PMPI

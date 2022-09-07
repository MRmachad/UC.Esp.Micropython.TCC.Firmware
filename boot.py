import gc

gc.collect()
gc.threshold(gc.mem_free() // (4 + gc.mem_alloc()))

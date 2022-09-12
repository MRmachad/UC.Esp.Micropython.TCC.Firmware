import gc

gc.collect()
gc.threshold(gc.mem_free() // (4 + gc.mem_alloc()))
print("\n=> Limite de alocação {} : {}".format( gc.threshold(), gc.isenabled()))

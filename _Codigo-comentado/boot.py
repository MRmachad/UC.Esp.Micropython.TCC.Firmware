
"""
Devido a uma fragemtação da memoria ram e deconrencia de um mal gerenciamento do mesmo pelo GC, coonfiguramos um valor limite para o gatilho do gc 
toda vez que o esp acorda e passa pelo boot. Isso no ajuda a previnir que o esp entre em falaha por erro de alocação de memoria
"""

import gc

gc.collect()
gc.threshold(gc.mem_free() // (4 + gc.mem_alloc()))
print("\n=> Limite de alocação {} : {}".format( gc.threshold(), gc.isenabled()))

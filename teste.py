import network

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
  
    VecTupRedes =  wlan.scan()
    rssi = 0
    for tup in VecTupRedes:
        if tup[0].decode() == "LUCAS E LEO":
            rssi = tup[3]
    
    

def myfunc():
    g = 0
    g0 = g
    if g0==0:
            g1 = g
            print g1
            g2 = g
            g3 = g2 -1
            g = g3
            myfunc()
    else:
            return

myfunc()

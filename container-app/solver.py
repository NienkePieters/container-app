
import pandas as pd
import numpy as np
from rectpack import newPacker
import rectpack.packer as packer
import matplotlib.pyplot as plt


# Function Solver
def solver(n_812, n_1012, bins):

    # Pallets Count
    #-- 80 x 120 cm
    bx = 0
    by = 0
    pal_812 = [80 + bx, 120 + by]

    #-- 100 x 120 cm
    bx = 0
    by = 0
    pal_1012 = [100 + bx, 120 + by]

    # Pallets to load
    rectangles = [pal_812 for i in range(n_812)] + [pal_1012 for i in range(n_1012)]

    # Build the Packer
    pack = newPacker(mode = packer.PackingMode.Offline, bin_algo = packer.PackingBin.Global,
                     rotation=True)

    # Add the rectangles to packing queue
    for r in rectangles:
        pack.add_rect(*r)

    # Add the bins where the rectangles will be placed
    for b in bins:
        pack.add_bin(*b)

    # Start packing
    pack.pack()

    # Full rectangle list
    all_rects = pack.rect_list()

    # Pallets with dimensions
    all_pals = [sorted([p[3], p[4]]) for p in all_rects]

    # Count number of 80 x 120
    p_812, p_1012 = all_pals.count(pal_812), all_pals.count(pal_1012)
    print("{:,}/{:,} Pallets 80 x 120 (cm) | {:,}/{:,} Pallets 100 x 120 (cm)".format(p_812, n_812, p_1012, n_1012))

    return all_rects, all_pals

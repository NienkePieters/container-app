
import pandas as pd
import numpy as np
from rectpack import newPacker
import rectpack.packer as packer
import matplotlib.pyplot as plt


# Function Solver
def solver(pallets_dict, bins):
    ''' For optimizing how pallets should be placed in the container. The inputs are the number of 80x120cm pallets, 100x120cm pallets and container size.'''

    # Set Pallet Buffer
    bx = 5 # buffer x
    by = 5 # buffer y

    #Create list of Rectangles
    rectangles = []
    for pallet in pallets_dict:
        for i in range(pallet.pallet_quantity):
            rectangles.append([(pallet.pallet_width + bx), (pallet.pallet_length + by)])
    
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

    return all_rects, all_pals

 
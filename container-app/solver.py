
import pandas as pd
import numpy as np
from rectpack import newPacker
import rectpack.packer as packer
import matplotlib.pyplot as plt


# Function Solver
def solver(n_128, n_68, n_64, n_1210, n_610, n_65, bins):
    ''' For optimizing how pallets should be placed in the container. The inputs are the quantities of each pallet type and the container size.'''

    # Set Pallet Buffer
    bx = 5 # buffer x
    by = 5 # buffer y
    pal_128 = [120 + bx, 80 + by]
    pal_68 = [60 + bx, 80 + by]
    pal_64 = [60 + bx, 40 + by]
    pal_1210 = [120 + bx, 100 + by]
    pal_610 = [60 + bx, 100 + by]
    pal_65 = [60 + bx, 50 + by]
    
    # Create Rectangles / Pallets to load
    rectangles =[pal_128 for i in range(n_128)] + [pal_68 for i in range(n_68)] + [pal_64 for i in range(n_64)] +\
                [pal_1210 for i in range(n_1210)] + [pal_610 for i in range(n_610)] + [pal_65 for i in range(n_65)]        

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

 

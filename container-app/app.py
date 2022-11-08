from viktor.core import ViktorController
from viktor.parametrization import ViktorParametrization, Text, IntegerField, OptionField, DynamicArray
from viktor.views import SVGView, SVGResult
from io import StringIO

from solver import solver
import pandas as pd
import numpy as np
from rectpack import newPacker
import rectpack.packer as packer
import matplotlib.pyplot as plt

class Parametrization(ViktorParametrization):
    title = Text('# Container Loading Optimization')

    #dynamic array with pallet inputs
    array = DynamicArray('Input pallets')
    array.pallet_length = IntegerField('Pallet length (cm)')
    array.pallet_width = IntegerField('Pallet width (cm)')
    array.pallet_quantity = IntegerField('Quantity')

    bin_type = OptionField('What type of container to fill?', options=["20'", "40'"], default="20'", flex=90)

class Controller(ViktorController):
    label = 'My Entity Type'
    parametrization = Parametrization(width=25)

    @SVGView("container", duration_guess=1)
    def create_svg_result(self, params, **kwargs):
        '''This function creates the output view plotting the pallets and container.'''

        #initialize figure
        fig = plt.figure(figsize = (4,12))

        # Pallet Dimensions
        bx = 5 # buffer x
        by = 5 # buffer y
        #pal_812 = [80 + bx, 120 + by]
        #pal_1012 = [100 + bx, 120 + by]

        # Containers size
        bins20 = [(235, 590)] # 20' container
        bins40 = [(235, 1203)] # 40' container
        # https://www.dsv.com/fr-fr/nos-solutions/modes-de-transport/fret-maritime/dimensions-de-conteneurs-maritimes/dry-container
        # https://www.icontainers.com/help/how-many-pallets-fit-in-a-container/

        if params.bin_type == "20'":
            bin_type = bins20
            plt.plot([0,235,235,0,0],[0,0,590,590,0], linewidth = 2.5 )
        else:
            bin_type = bins40
            plt.plot([0,235,235,0,0],[0,0,1203,1203,0], linewidth = 2.5)

        #all_rects, all_pals = solver(params.n_812, params.n_1012, bin_type)
        all_rects, all_pals = solver(params.array, bin_type)

        # Loop all rect
        for rect in all_rects:
            b, x, y, w, h, rid = rect
            x1, x2, x3, x4, x5 = x, x+w, x+w, x, x
            y1, y2, y3, y4, y5 = y, y, y+h, y+h,y

            # Pallet type colours. If included also add color in plot below.
            #if [w, h] == pal_812 or [h, w] == pal_812:
            #    color = '--k'
            #else:
            #    color = '--r'

            plt.plot([x1,x2,x3,x4,x5],[y1,y2,y3,y4,y5], linewidth = 2)
        
        plt.ylim([-50,1250])
        plt.xlim([-50,285])
        #plt.axis('equal')
        fig.tight_layout()

        #save figure
        svg_data = StringIO()
        fig.savefig(svg_data, format='svg')
        plt.close()

        return SVGResult(svg_data)

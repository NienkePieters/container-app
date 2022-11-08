from viktor.core import ViktorController
from viktor.parametrization import ViktorParametrization, Text, IntegerField, OptionField, DynamicArray
from viktor.views import SVGView, SVGResult
from io import StringIO
from matplotlib.patches import Rectangle

from solver import solver
import pandas as pd
import numpy as np
from rectpack import newPacker
import rectpack.packer as packer
import matplotlib.pyplot as plt

class Parametrization(ViktorParametrization):
    title = Text('# Container Loading Optimization')

    bin_type = OptionField('What type of container to fill?', options=["20'", "40'"], default="20'", flex=90)

    #dynamic array with pallet inputs
    array = DynamicArray('Select pallet types and quantities')
    array.pallet_dim = OptionField('Pallet Type', options =['120 x 80 cm: Standard Euro Pallet', '60 x 80 cm: Half Euro Pallet', '60 x 40 cm: Display Pallet', '120 x 100 cm: Standard Block Pallet', '60 x 100 cm: Half Block Pallet', '60 x 50 cm: HST mini-pallet'], flex=70, default='120 x 80 cm: Standard Euro Pallet')
    array.pallet_quantity = IntegerField('Quantity', default = 1, flex = 25)


class Controller(ViktorController):
    label = 'My Entity Type'
    parametrization = Parametrization(width=35)

    @SVGView("container", duration_guess=1)
    def create_svg_result(self, params, **kwargs):
        '''This function creates the output view plotting the pallets and container.'''

        #initialize figure
        fig = plt.figure(figsize = (4,12))

        # Set Containers size
        bins20 = [(235, 590)] # 20' container
        bins40 = [(235, 1203)] # 40' container
        # https://www.dsv.com/fr-fr/nos-solutions/modes-de-transport/fret-maritime/dimensions-de-conteneurs-maritimes/dry-container
        # https://www.icontainers.com/help/how-many-pallets-fit-in-a-container/

        # Set Pallet Dimensions
        bx = 5 # buffer x
        by = 5 # buffer y

        pal_128 = [120 + bx, 80 + by]
        pal_68 = [60 + bx, 80 + by]
        pal_64 = [60 + bx, 40 + by]
        pal_1210 = [120 + bx, 100 + by]
        pal_610 = [60 + bx, 100 + by]
        pal_65 = [60 + bx, 50 + by]
        
        # How many of each pallet type is selected
        n_128, n_68, n_64, n_1210, n_610, n_65 = 0, 0, 0, 0, 0, 0

        for pallet in params.array:
            if pallet.pallet_dim == '120 x 80 cm: Standard Euro Pallet':
                n_128 += pallet.pallet_quantity
            if pallet.pallet_dim == '60 x 80 cm: Half Euro Pallet':
                n_68 += pallet.pallet_quantity
            if pallet.pallet_dim == '60 x 40 cm: Display Pallet':
                n_64 += pallet.pallet_quantity
            if pallet.pallet_dim == '120 x 100 cm: Standard Block Pallet':
                n_1210 += pallet.pallet_quantity
            if pallet.pallet_dim == '60 x 100 cm: Half Block Pallet':
                n_610 += pallet.pallet_quantity
            if pallet.pallet_dim == '60 x 50 cm: HST mini-pallet':
                n_65 += pallet.pallet_quantity

        # Plot Container
        if params.bin_type == "20'":
            bin_type = bins20
            plt.plot([0,235,235,0,0],[0,0,590,590,0], linewidth = 2.5, color = "k" )
        else:
            bin_type = bins40
            plt.plot([0,235,235,0,0],[0,0,1203,1203,0], linewidth = 2.5, color = "k")

        #all_rects, all_pals = solver(params.n_812, params.n_1012, bin_type)
        all_rects, all_pals = solver(n_128, n_68, n_64, n_1210, n_610, n_65, bin_type)

        # Loop all rect
        for rect in all_rects:
            b, x, y, w, h, rid = rect
            #x1, x2, x3, x4, x5 = x, x+w, x+w, x, x
            #y1, y2, y3, y4, y5 = y, y, y+h, y+h,y
            # Pallet type colours. If included also add color in plot below.
            if [w, h] == pal_128 or [h, w] == pal_128:
                color = 'pink'
            if [w, h] == pal_68 or [h, w] == pal_68:
                color = 'brown'
            if [w, h] == pal_64 or [h, w] == pal_64:
                color = 'olive'
            if [w, h] == pal_1210 or [h, w] == pal_1210:
                color = 'orange'
            if [w, h] == pal_610 or [h, w] == pal_610:
                color = 'blue'
            if [w, h] == pal_65 or [h, w] == pal_65:
                color = 'purple'
            plt.gca().add_patch(Rectangle((x,y),w,h, facecolor = color, edgecolor='k', fill=True, lw=2))
            #plt.plot([x1,x2,x3,x4,x5],[y1,y2,y3,y4,y5], color, linewidth = 2)
        
        #plt.ylim([-50,1250])
        #plt.xlim([-50,285])
        plt.axis('equal')
        plt.axis('off')
        fig.tight_layout()

        #save figure
        svg_data = StringIO()
        fig.savefig(svg_data, format='svg')
        plt.close()

        return SVGResult(svg_data)

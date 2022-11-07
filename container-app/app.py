from viktor.core import ViktorController
from viktor.parametrization import ViktorParametrization, Text, IntegerField, OptionField
from viktor.views import SVGView, SVGResult
from io import StringIO

from solver import solver
import pandas as pd
import numpy as np
from rectpack import newPacker
import rectpack.packer as packer
import matplotlib.pyplot as plt

class Parametrization(ViktorParametrization):
    title = Text('# Container loading optimization model')

    n_812 = IntegerField('How many 80 x 120 cm pallets?')

    n_1012 = IntegerField('How many 100 x 120 cm pallets?')

    bin_type = OptionField('What type of container?', options=["20'", "40'"], default="20'")

class Controller(ViktorController):
    label = 'My Entity Type'
    parametrization = Parametrization

    @SVGView("container", duration_guess=1)
    def create_svg_result(self, params, **kwargs):
        #initialize figure
        fig = plt.figure(figsize = (10,10))

        # Pallet Dimensions
        bx = 5 # buffer x
        by = 5 # buffer y
        pal_812 = [80 + bx, 120 + by]
        pal_1012 = [100 + bx, 120 + by]

        # Containers size
        bins20 = [(235, 590)] # 20' container
        bins40 = [(235, 1203)] # 40' container
        # https://www.dsv.com/fr-fr/nos-solutions/modes-de-transport/fret-maritime/dimensions-de-conteneurs-maritimes/dry-container
        # https://www.icontainers.com/help/how-many-pallets-fit-in-a-container/

        if params.bin_type == "20'":
            bin_type = bins20
            plt.plot([0,235,235,0,0],[0,0,590,590,0])
        else:
            bin_type = bins40
            plt.plot([0,235,235,0,0],[0,0,1203,1203,0])

        all_rects, all_pals = solver(params.n_812, params.n_1012, bin_type)
        # Loop all rect
        for rect in all_rects:
            b, x, y, w, h, rid = rect
            x1, x2, x3, x4, x5 = x, x+w, x+w, x, x
            y1, y2, y3, y4, y5 = y, y, y+h, y+h,y

            # Pallet type
            if [w, h] == pal_812:
                color = '--k'
            else:
                color = '--r'

            plt.plot([x1,x2,x3,x4,x5],[y1,y2,y3,y4,y5], color)
        


        plt.axis('equal')


        svg_data = StringIO()
        fig.savefig(svg_data, format='svg')
        plt.close()

        return SVGResult(svg_data)

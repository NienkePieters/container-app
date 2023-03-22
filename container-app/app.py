from viktor.core import ViktorController
from viktor.geometry import SquareBeam, Group, Material
from viktor.parametrization import ViktorParametrization, Text, IntegerField, OptionField, DynamicArray
from viktor.views import SVGView, SVGResult, GeometryResult, GeometryView
from viktor import Color
from io import StringIO
from matplotlib.patches import Rectangle

from solver import solver
import pandas as pd
import numpy as np
from rectpack import newPacker
import rectpack.packer as packer
import matplotlib.pyplot as plt
import random


class Parametrization(ViktorParametrization):
    title = Text('# Container Loading Optimization')

    bin_type = OptionField('What type of container to fill?', options=["20'", "40'"], default="20'", flex=90)

    # dynamic array with pallet inputs
    array = DynamicArray('Select pallet types and quantities',
                         default=[{'pallet_dim': '120 x 80 cm: Standard Euro Pallet', 'pallet_quantity': 1}])
    array.pallet_dim = OptionField('Pallet Type',
                                   options=['120 x 80 cm: Standard Euro Pallet', '60 x 80 cm: Half Euro Pallet',
                                            '60 x 40 cm: Display Pallet', '120 x 100 cm: Standard Block Pallet',
                                            '60 x 100 cm: Half Block Pallet', '60 x 50 cm: HST mini-pallet'], flex=70,
                                   default='120 x 80 cm: Standard Euro Pallet')
    array.pallet_quantity = IntegerField('Quantity', default=1, flex=25)


class Controller(ViktorController):
    label = 'My Container'
    parametrization = Parametrization(width=35)

    @SVGView("container", duration_guess=1)
    def create_svg_result(self, params, **kwargs):
        '''This function creates the output view plotting the pallets and container.'''

        # initialize figure
        fig = plt.figure(figsize=(4, 12))

        # Set Containers size
        bins20 = [(235, 590)]  # 20' container
        bins40 = [(235, 1203)]  # 40' container
        # https://www.dsv.com/fr-fr/nos-solutions/modes-de-transport/fret-maritime/dimensions-de-conteneurs-maritimes/dry-container
        # https://www.icontainers.com/help/how-many-pallets-fit-in-a-container/

        # Set Pallet Dimensions
        bx = 5  # buffer x
        by = 5  # buffer y

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
            plt.plot([0, 235, 235, 0, 0], [0, 0, 590, 590, 0], linewidth=2.5, color="k")
        else:
            bin_type = bins40
            plt.plot([0, 235, 235, 0, 0], [0, 0, 1203, 1203, 0], linewidth=2.5, color="k")

        # all_rects, all_pals = solver(params.n_812, params.n_1012, bin_type)
        all_rects, all_pals = solver(n_128, n_68, n_64, n_1210, n_610, n_65, bin_type)

        # Loop all rect
        for rect in all_rects:
            b, x, y, w, h, rid = rect
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
            plt.gca().add_patch(Rectangle((x, y), w, h, facecolor=color, edgecolor='k', fill=True, lw=2))

        plt.axis('equal')
        plt.axis('off')
        fig.tight_layout()

        # save figure
        svg_data = StringIO()
        fig.savefig(svg_data, format='svg')
        plt.close()

        return SVGResult(svg_data)

    @GeometryView("3D container", duration_guess=1)
    def visualize_container(self, params, **kwargs):

        # generate container
        length_x = 2.35
        length_z = 2.6
        if params.bin_type == "20'":
            length_y = 5.90
            bin_type = [(235, 590)]
        else:
            length_y = 12.03
            bin_type = [(235, 1203)]
        container = SquareBeam(length_x, length_y, length_z)
        container.material = Material('iron', threejs_opacity=0.5)
        container.translate([(length_x / 2), (length_y / 2), (length_z / 2)])

        # Set Pallet Dimensions
        bx = 5  # buffer x
        by = 5  # buffer y

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

        # all_rects, all_pals = solver(params.n_812, params.n_1012, bin_type)
        all_rects, all_pals = solver(n_128, n_68, n_64, n_1210, n_610, n_65, bin_type)

        pallets = []
        for i, pallet in enumerate(all_rects):
            b, x, y, w, h, rid = pallet
            length_x = w / 100
            length_y = h / 100
            length_z = random.uniform(1, 2)  # random pallet heights

            # create pallet
            pallet_box = SquareBeam(length_x=length_x - 0.1, length_y=length_y - 0.1,
                                    length_z=length_z)  # add 0.1 loose space between pallets

            # move pallet to right location (defining the center of the pallet)
            pallet_box.translate([(x / 100 + 0.5 * length_x), (y / 100 + 0.5 * length_y), (0.5 * length_z)])

            # set Material
            if [w, h] == pal_128 or [h, w] == pal_128:
                color = Color(227, 119, 194)  # pink
            elif [w, h] == pal_68 or [h, w] == pal_68:
                color = Color(140, 86, 75)  # brown
            elif [w, h] == pal_64 or [h, w] == pal_64:
                color = Color(188, 189, 34)  # olive
            elif [w, h] == pal_1210 or [h, w] == pal_1210:
                color = Color(255, 127, 14)  # orange
            elif [w, h] == pal_610 or [h, w] == pal_610:
                color = Color(31, 119, 180)  # blue
            elif [w, h] == pal_65 or [h, w] == pal_65:
                color = Color(148, 103, 189)  # purple
            pallet_box.material = Material('plastic', color=color)

            # add to pallet list
            pallets.append(pallet_box)
        pallets = Group(pallets)

        container_system = Group([container, pallets])

        return GeometryResult(container_system)

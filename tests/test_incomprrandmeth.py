# -*- coding: utf-8 -*-
"""
This is the unittest of the RandMeth class.
"""
from __future__ import division, absolute_import, print_function

import copy
import unittest
import numpy as np
from gstools import Gaussian
from gstools.field.generator import IncomprRandMeth
import emcee as mc


MC_VER = int(mc.__version__.split(".")[0])


class TestIncomprRandMeth(unittest.TestCase):
    def setUp(self):
        self.cov_model_2d = Gaussian(
            dim=2, var=1.5, len_scale=2.5, mode_no=100
        )
        self.cov_model_3d = copy.deepcopy(self.cov_model_2d)
        self.cov_model_3d.dim = 3
        self.seed = 19031977
        self.x_grid = np.linspace(0.0, 10.0, 9)
        self.y_grid = np.linspace(-5.0, 5.0, 16)
        self.z_grid = np.linspace(-6.0, 7.0, 8)
        self.x_tuple = np.linspace(0.0, 10.0, 10)
        self.y_tuple = np.linspace(-5.0, 5.0, 10)
        self.z_tuple = np.linspace(-6.0, 8.0, 10)

        self.rm_2d = IncomprRandMeth(
            self.cov_model_2d, mode_no=100, seed=self.seed
        )
        self.rm_3d = IncomprRandMeth(
            self.cov_model_3d, mode_no=100, seed=self.seed
        )

    def test_unstruct_2d(self):
        modes = self.rm_2d(2, self.x_tuple, self.y_tuple)
        self.assertAlmostEqual(modes[0, 0], 1.99100618)
        self.assertAlmostEqual(modes[0, 1], 2.02471175)
        self.assertAlmostEqual(modes[1, 1], -0.28979649)

    def test_unstruct_3d(self):
        modes = self.rm_3d(3, self.x_tuple, self.y_tuple, self.z_tuple)
        if MC_VER < 3:
            self.assertAlmostEqual(modes[0, 1], 0.99476583)
            self.assertAlmostEqual(modes[1, 0], 0.17039711)
            self.assertAlmostEqual(modes[1, 1], -0.25210944)
        else:
            self.assertAlmostEqual(modes[0, 0], 2.41526352)
            self.assertAlmostEqual(modes[0, 1], 3.29398652)
            self.assertAlmostEqual(modes[1, 0], -0.33790866)

    def test_struct_2d(self):
        modes = self.rm_2d(2, self.x_grid, self.y_grid, mesh_type='structured')
        self.assertAlmostEqual(modes[0, 0, 0], 0.50751115)
        self.assertAlmostEqual(modes[0, 1, 0], 0.69751927)
        self.assertAlmostEqual(modes[1, 1, 1], -0.19747468)

    def test_struct_3d(self):
        modes = self.rm_3d(3, self.x_grid, self.y_grid, self.z_grid, mesh_type='structured')
        if MC_VER < 3:
            self.assertAlmostEqual(modes[0, 1, 0, 0], 1.69569140)
            self.assertAlmostEqual(modes[0, 0, 1, 0], 1.04667503)
            self.assertAlmostEqual(modes[0, 0, 0, 1], 1.19464729)
            self.assertAlmostEqual(modes[1, 1, 1, 0], -0.36103764)
        else:
            self.assertAlmostEqual(modes[0, 0, 0, 0], 1.49469700)
            self.assertAlmostEqual(modes[1, 0, 1, 1], 0.12813365)
            self.assertAlmostEqual(modes[1, 1, 0, 1], 0.01443056)
            self.assertAlmostEqual(modes[1, 1, 1, 1], -0.12304040)

    def test_assertions(self):
        cov_model_1d = Gaussian(dim=1, var=1.5, len_scale=2.5, mode_no=100)
        self.assertRaises(ValueError, IncomprRandMeth, cov_model_1d)


if __name__ == "__main__":
    unittest.main()

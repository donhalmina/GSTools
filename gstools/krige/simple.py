# -*- coding: utf-8 -*-
"""
GStools subpackage providing a class for simple kriging.

.. currentmodule:: gstools.krige.simple

The following classes are provided

.. autosummary::
   Simple
"""
# pylint: disable=C0103
from __future__ import division, absolute_import, print_function

from functools import partial

import numpy as np
from scipy.linalg import inv
from scipy.spatial.distance import cdist

from gstools.covmodel.base import CovModel
from gstools.field.tools import (
    check_mesh,
    make_isotropic,
    unrotate_mesh,
    reshape_axis_from_struct_to_unstruct,
    reshape_field_from_unstruct_to_struct,
)
from gstools.field.base import Field
from gstools.tools.geometric import pos2xyz, xyz2pos
from gstools.tools.export import vtk_export as vtk_ex
from gstools.krige.krigesum import krigesum

__all__ = ["Simple"]


class Simple(Field):
    """
    A class for simple kriging.

    Parameters
    ----------
    model : :any:`CovModel`
        Covariance Model used for kriging.
    mean : :class:`float`, optional
        mean value of the kriging field
    cond_pos : :class:`list`
        tuple, containing the given condition positions (x, [y, z])
    cond_val : :class:`numpy.ndarray`
        the values of the conditions
    """

    def __init__(self, model, mean, cond_pos, cond_val):
        super(Simple, self).__init__(model, mean)
        self.krige_var = None
        # initialize private attributes
        self._cond_pos = None
        self._cond_val = None
        self.set_condition(cond_pos, cond_val)

        # initialize attributes

    def __call__(self, pos, mesh_type="unstructured"):
        """
        Generate the simple kriging field.

        The field is saved as `self.field` and is also returned.

        Parameters
        ----------
        pos : :class:`list`
            the position tuple, containing main direction and transversal
            directions (x, [y, z])
        mesh_type : :class:`str`
            'structured' / 'unstructured'

        Returns
        -------
        field : :class:`numpy.ndarray`
            the kriged field
        krige_var : :class:`numpy.ndarray`
            the kriging error variance
        """
        # internal conversation
        x, y, z = pos2xyz(pos, dtype=np.double)
        c_x, c_y, c_z = pos2xyz(self.cond_pos, dtype=np.double)
        self.pos = xyz2pos(x, y, z)
        self.mesh_type = mesh_type
        # format the positional arguments of the mesh
        check_mesh(self.model.dim, x, y, z, mesh_type)
        mesh_type_changed = False
        if mesh_type == "structured":
            mesh_type_changed = True
            mesh_type_old = mesh_type
            mesh_type = "unstructured"
            x, y, z, axis_lens = reshape_axis_from_struct_to_unstruct(
                self.model.dim, x, y, z
            )
        if self.model.do_rotation:
            x, y, z = unrotate_mesh(self.model.dim, self.model.angles, x, y, z)
            c_x, c_y, c_z = unrotate_mesh(
                self.model.dim, self.model.angles, c_x, c_y, c_z
            )
        y, z = make_isotropic(self.model.dim, self.model.anis, y, z)
        c_y, c_z = make_isotropic(self.model.dim, self.model.anis, c_y, c_z)

        # set condtions to zero mean
        cond = self.cond_val - self.mean
        krig_mat = inv(self._get_cov_mat((c_x, c_y, c_z), (c_x, c_y, c_z)))
        krig_vecs = self._get_cov_mat((c_x, c_y, c_z), (x, y, z))
        # generate the kriged field
        field, krige_var = krigesum(krig_mat, krig_vecs, cond)

        # reshape field if we got an unstructured mesh
        if mesh_type_changed:
            mesh_type = mesh_type_old
            field = reshape_field_from_unstruct_to_struct(
                self.model.dim, field, axis_lens
            )
            krige_var = reshape_field_from_unstruct_to_struct(
                self.model.dim, krige_var, axis_lens
            )
        # calculate the kriging error
        self.krige_var = self.model.sill - krige_var
        # add the given mean
        self.field = field + self.mean
        return self.field, self.krige_var

    def _get_cov_mat(self, pos1, pos2):
        return self.model.cov_nugget(
            cdist(
                np.column_stack(pos1[: self.model.dim]),
                np.column_stack(pos2[: self.model.dim]),
            )
        )

    def set_condition(self, cond_pos, cond_val):
        """Set the conditions for kriging.

        Parameters
        ----------
        cond_pos : :class:`list`
            the position tuple of the conditions (x, [y, z])
        cond_val : :class:`numpy.ndarray`
            the values of the conditions
        """
        self._cond_pos = cond_pos
        self._cond_val = np.array(cond_val, dtype=np.double)

    @property
    def cond_pos(self):
        """:class:`list`: The position tuple of the conditions."""
        return self._cond_pos

    @property
    def cond_val(self):
        """:class:`list`: The values of the conditions."""
        return self._cond_val

    def __repr__(self):
        """Return String representation."""
        return "Simple(model={0}, mean={1}, cond_pos={2}, cond_val={3}".format(
            self.model, self.mean, self.cond_pos, self.cond_val
        )


if __name__ == "__main__":  # pragma: no cover
    import doctest

    doctest.testmod()

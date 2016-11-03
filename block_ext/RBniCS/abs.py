# Copyright (C) 2015-2016 by the RBniCS authors
# Copyright (C) 2016 by the block_ext authors
#
# This file is part of the RBniCS interface to block_ext.
#
# RBniCS and block_ext are free software: you can redistribute them and/or modify
# them under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RBniCS and block_ext are distributed in the hope that they will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with RBniCS and block_ext. If not, see <http://www.gnu.org/licenses/>.
#

from math import fabs
from dolfin import as_backend_type, Point, vertices
from block_ext.RBniCS.matrix import Matrix
from block_ext.RBniCS.vector import Vector
from block_ext.RBniCS.function import Function
from RBniCS.utils.decorators import backend_for
from RBniCS.utils.mpi import parallel_max

# abs function to compute maximum absolute value of an expression, matrix or vector (for EIM). To be used in combination with max
# even though here we actually carry out both the max and the abs!
@backend_for("block_ext", inputs=((Matrix.Type(), Vector.Type(), Function.Type()), ))
def abs(expression):
    assert isinstance(expression, (Matrix.Type(), Vector.Type(), Function.Type()))
    pass # TODO
    
# Auxiliary class to signal to the max() function that it is dealing with an output of the abs() method
class AbsOutput(object):
    def __init__(self, max_abs_return_value, max_abs_return_location):
        self.max_abs_return_value = max_abs_return_value
        self.max_abs_return_location = max_abs_return_location
        

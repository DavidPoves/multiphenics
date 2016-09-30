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

from block_ext import BlockFunctionSpace
from RBniCS.backends.basic import TensorsList as BasicTensorsList
import block_ext.RBniCS.backends.block_ext
import block_ext.RBniCS.backends.block_ext.wrapping
import RBniCS.backends.numpy
from RBniCS.utils.decorators import BackendFor, Extends, override

@Extends(BasicTensorsList)
@BackendFor("block_ext", online_backend="NumPy", inputs=(BlockFunctionSpace, ))
class TensorsList(BasicTensorsList):
    @override
    def __init__(self, V_or_Z):
        BasicTensorsList.__init__(self, V_or_Z, block_ext.RBniCS.backends.block_ext, block_ext.RBniCS.backends.block_ext.wrapping, RBniCS.backends.numpy)
        

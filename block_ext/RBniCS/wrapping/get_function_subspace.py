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

from block_ext.block_function_space import BlockFunctionSpace

def get_function_subspace(block_function_space, block_components):
    assert isinstance(block_components, (int, list))
    assert not isinstance(block_components, tuple), "block_ext does not handle yet the case of sub components"
    if isinstance(block_components, int):
        return BlockFunctionSpace([block_function_space[block_components]])
    else:
        extracted_block_function_spaces = list()
        for block_component in block_components:
            assert isinstance(block_component, int)
            assert not isinstance(block_component, tuple), "block_ext does not handle yet the case of sub components"
            extracted_block_function_spaces.append(block_function_space[block_component])
        return BlockFunctionSpace(extracted_block_function_spaces)


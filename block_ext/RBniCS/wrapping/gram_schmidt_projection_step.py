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

def gram_schmidt_projection_step(new_basis, X, old_basis, transpose):
    angle = - (transpose(new_basis)*X*old_basis)
    for (block_index, (block_new_basis, block_old_basis)) in enumerate(zip(new_basis, old_basis)):
        block_new_basis.vector().add_local( angle * block_old_basis.vector().array() )
        block_new_basis.vector().apply("add")
    return new_basis


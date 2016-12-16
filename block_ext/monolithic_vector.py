# Copyright (C) 2016 by the block_ext authors
#
# This file is part of block_ext.
#
# block_ext is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# block_ext is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with block_ext. If not, see <http://www.gnu.org/licenses/>.
#

from dolfin import PETScVector, as_backend_type
from petsc4py import PETSc
from block_ext.block_outer import BlockOuterVector

class MonolithicVector(PETScVector):
    # The values of block_vector are not really used, just the
    # block sparsity pattern. vec object has been already allocated
    # by the MonolithicMatrix::create_monolithic_vectors method
    def __init__(self, block_vector, vec, block_discard_dofs=None):
        import numpy as np
        # Outer dimensions
        N = block_vector.blocks.shape[0]
        
        # Inner dimensions
        n = []
        for I in range(N):
            if not isinstance(block_vector[I], BlockOuterVector):
                block = as_backend_type(block_vector[I]).vec()
            else:
                block = as_backend_type(block_vector[I].vec).vec()
            current_n = block.getSize()
            if block_discard_dofs is not None and block_discard_dofs.need_to_discard_dofs[I]:
                current_n -= len(block_discard_dofs.dofs_to_be_discarded[I])
            n.append(current_n)
        
        # Store dimensions
        self.N, self.n = N, n
        
        # Auxiliary block ranges
        self.block_range_start = np.array([sum(n[: I   ]) for I in range(N)], dtype='i')
        self.block_range_end   = np.array([sum(n[:(I+1)]) for I in range(N)], dtype='i')
        
        # Init PETScVector
        PETScVector.__init__(self, vec)
        
        # Store dofs to be discarded while adding
        self.block_discard_dofs = block_discard_dofs
        
    def block_add(self, block_vector):
        N, n = self.N, self.n
        assert N == block_vector.blocks.shape[0]
        block_discard_dofs = self.block_discard_dofs
        
        for I in range(N):
            if block_discard_dofs is not None and block_discard_dofs.need_to_discard_dofs[I]:
                row_reposition_dofs = block_discard_dofs.subspace_dofs_extended[I]
            else:
                row_reposition_dofs = None
            if not isinstance(block_vector[I], BlockOuterVector):
                self._block_add(block_vector[I], I, n, row_reposition_dofs)
            else:
                self._block_add(block_vector[I].vec, I, n, row_reposition_dofs)
        self.vec().assemble()
        
    def copy_values_to(self, block_vector):
        import numpy as np
        N, n = self.N, self.n
        assert N == block_vector.blocks.shape[0]
        block_range_start, block_range_end = self.block_range_start, self.block_range_end
        block_discard_dofs = self.block_discard_dofs
        
        row_start, row_end = self.vec().getOwnershipRange()
        I = np.argmax(block_range_end > row_start)
        i = row_start - block_range_start[I]
        if block_discard_dofs is not None and block_discard_dofs.need_to_discard_dofs[I]:
            block_row_reposition_dofs = block_discard_dofs.space_dofs_restricted[I]
        else:
            block_row_reposition_dofs = None
        for k in range(row_start, row_end):
            if block_row_reposition_dofs is not None:
                block_row = block_row_reposition_dofs[i]
            else:
                block_row = i
            val = self.vec().array[k - row_start]
            assert not isinstance(block_vector[I], BlockOuterVector)
            block = as_backend_type(block_vector[I]).vec()
            block.setValues(block_row, val, addv=PETSc.InsertMode.INSERT)
            if k < row_end - 1:
                # increment
                i += 1
                if i >= n[I]:
                    I += 1
                    i = 0
                    # also update block_row_reposition_dofs for the new I
                    if block_discard_dofs is not None and block_discard_dofs.need_to_discard_dofs[I]:
                        block_row_reposition_dofs = block_discard_dofs.space_dofs_restricted[I]
                    else:
                        block_row_reposition_dofs = None
        for I in range(N):
            as_backend_type(block_vector[I]).vec().assemble()
            as_backend_type(block_vector[I]).vec().ghostUpdate()
        
    def _block_add(self, block, I, n, row_reposition_dofs):
        block = as_backend_type(block).vec()
        row_start, row_end = block.getOwnershipRange()
        for i in range(row_start, row_end):
            if row_reposition_dofs is not None:
                if i not in row_reposition_dofs:
                    continue
                row = row_reposition_dofs[i]
            else:
                row = i
            row += sum(n[:I])
            val = block.array[i - row_start]
            self.vec().setValues(row, val, addv=PETSc.InsertMode.ADD)

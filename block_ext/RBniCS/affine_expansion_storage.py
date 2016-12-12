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

from numpy import ndarray as array
from ufl import Form
from block_ext import block_adjoint, block_assemble, BlockDirichletBC
from RBniCS.backends.abstract import AffineExpansionStorage as AbstractAffineExpansionStorage
from RBniCS.utils.decorators import array_of, BackendFor, Extends, list_of, override, tuple_of
from block_ext.RBniCS.matrix import Matrix
from block_ext.RBniCS.vector import Vector
from block_ext.RBniCS.function import Function

@Extends(AbstractAffineExpansionStorage)
@BackendFor("block_ext", inputs=((tuple_of(BlockDirichletBC), tuple_of(list_of(Form)), tuple_of(list_of(list_of(Form))), tuple_of(array_of(Form)), tuple_of(array_of(array_of(Form))), tuple_of(Function.Type()), tuple_of(Matrix.Type()), tuple_of(Vector.Type())), ))
class AffineExpansionStorage(AbstractAffineExpansionStorage):
    @override
    def __init__(self, args):
        self._content = None
        self._type = None
        # Type checking
        is_Form = self._is_Form(args[0])
        is_DirichletBC = self._is_DirichletBC(args[0])
        is_Function = self._is_Function(args[0])
        is_Tensor = self._is_Tensor(args[0])
        assert is_Form or is_DirichletBC or is_Function or is_Tensor
        for i in range(1, len(args)):
            if is_Form:
                assert self._is_Form(args[i])
            elif is_DirichletBC:
                assert self._is_DirichletBC(args[i])
            elif is_Function:
                assert self._is_Function(args[i])
            elif is_Tensor:
                assert self._is_Tensor(args[i])
            else:
                return TypeError("Invalid input arguments to AffineExpansionStorage")
        # Actual init
        if is_Form:
            # keep_diagonal is enabled because it is needed to constrain DirichletBC eigenvalues in SCM
            self._content = [block_assemble(arg, keep_diagonal=True) for arg in args]
            self._type = "BlockForm"
        elif is_DirichletBC:
            self._content = args
            self._type = "BlockDirichletBC"
        elif is_Function:
            self._content = args
            self._type = "BlockFunction"
        elif is_Tensor:
            self._content = args
            self._type = "BlockForm"
        else:
            return TypeError("Invalid input arguments to AffineExpansionStorage")
        
    @staticmethod
    def _is_Form(arg):
        if isinstance(arg, list):
            if isinstance(arg[0], Form): # block vector
                return True
            elif isinstance(arg[0], list):
                if isinstance(arg[0][0], Form): # block matrix
                    return True
                else:
                    return False
            else:
                return False
        elif isinstance(arg, array):
            assert len(arg.shape) in (1, 2)
            if isinstance(arg.item(0), Form):
                return True
            else:
                return False
        else:
            return False
        
    @staticmethod
    def _is_DirichletBC(arg):
        return isinstance(arg, BlockDirichletBC)
        
    @staticmethod
    def _is_Function(arg):
        return isinstance(arg, Function.Type())

    @staticmethod
    def _is_Tensor(arg):
        return isinstance(arg, (Matrix.Type(), Vector.Type()))
        
    def type(self):
        return self._type
        
    @override
    def __getitem__(self, key):
        return self._content[key]
        
    @override
    def __iter__(self):
        return self._content.__iter__()
        
    @override
    def __len__(self):
        assert self._content is not None
        return len(self._content)
        

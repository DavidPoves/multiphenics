# Copyright (C) 2015-2017 by the RBniCS authors
# Copyright (C) 2016-2017 by the block_ext authors
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

import types
from block_ext import BlockDirichletBC, BlockNonlinearProblem, BlockPETScSNESSolver
from RBniCS.backends.abstract import NonlinearSolver as AbstractNonlinearSolver
from block_ext.RBniCS.function import Function
from RBniCS.utils.decorators import BackendFor, dict_of, Extends, override

@Extends(AbstractNonlinearSolver)
@BackendFor("block_ext", inputs=(types.FunctionType, Function.Type(), types.FunctionType, (BlockDirichletBC, dict_of(str, BlockDirichletBC), None)))
class NonlinearSolver(AbstractNonlinearSolver):
    @override
    def __init__(self, block_jacobian_eval, block_solution, block_residual_eval, block_bcs=None):
        assert isinstance(block_bcs, (dict, BlockDirichletBC))
        if isinstance(block_bcs, BlockDirichletBC):
            block_bcs_preprocessed = block_bcs
        elif isinstance(block_bcs, dict):
            block_bcs_preprocessed = list()
            for key in block_bcs:
                for (index, bcs) in enumerate(block_bcs[key].bcs):
                    if len(block_bcs_preprocessed) < index:
                        assert len(block_bcs_preprocessed) == index - 1
                        block_bcs_preprocessed.append(list())
                    block_bcs_preprocessed[index].extend(bcs)
            block_bcs_preprocessed = BlockDirichletBC(block_bcs_preprocessed)
        else:
            raise AssertionError("Invalid type for bcs.")
        problem = BlockNonlinearProblem(block_residual_eval, block_solution, block_bcs_preprocessed, block_jacobian_eval)
        self.solver  = BlockPETScSNESSolver(problem)
            
    @override
    def set_parameters(self, parameters):
        self.solver.parameters.update(parameters)
        
    @override
    def solve(self):
        return self.solver.solve()
        

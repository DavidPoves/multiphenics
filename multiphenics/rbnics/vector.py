# Copyright (C) 2015-2017 by the RBniCS authors
# Copyright (C) 2016-2017 by the multiphenics authors
#
# This file is part of the RBniCS interface to multiphenics.
#
# RBniCS and multiphenics are free software: you can redistribute them and/or modify
# them under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RBniCS and multiphenics are distributed in the hope that they will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with RBniCS and multiphenics. If not, see <http://www.gnu.org/licenses/>.
#

from multiphenics.block_vector import BlockVector

def Vector():
    raise NotImplementedError("This is dummy function (not required by the interface) just store the Type")
    
def _Vector_Type():
    return BlockVector
Vector.Type = _Vector_Type

# Preserve generator attribute in algebraic operators, as required by DEIM
def preserve_generator_attribute(operator):
    original_operator = getattr(BlockVector, operator)
    def custom_operator(self, other):
        if hasattr(self, "generator"):
            output = original_operator(self, other)
            output.generator = self.generator
            return output
        else:
            return original_operator(self, other)
    setattr(BlockVector, operator, custom_operator)
    
for operator in ("__add__", "__radd__", "__iadd__", "__sub__", "__rsub__", "__isub__", "__mul__", "__rmul__", "__imul__"):
    preserve_generator_attribute(operator)

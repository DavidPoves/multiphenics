# Copyright (C) 2016-2017 by the block_ext authors
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

from dolfin import *
from mshr import *
from block_ext import *

"""
In this tutorial we compare the formulation and solution
of a Navier-Stokes by standard FEniCS code (using the
MixedElement class) and block_ext code.
"""

# Geometrical parameters
pre_step_length = 4.
after_step_length = 14.
pre_step_height = 3.
after_step_height = 5.

# Constitutive parameters
nu = Constant(0.01)
u_in = Constant((1., 0.))
u_wall = Constant((0., 0.))

# Solver parameters
snes_solver_parameters = {"nonlinear_solver": "snes",
                          "snes_solver": {"linear_solver": "mumps",
                                          "maximum_iterations": 20,
                                          "report": True,
                                          "error_on_nonconvergence": True}}
                                          
## -------------------------------------------------- ##

##                  MESH GENERATION                   ##
# Create mesh
domain = \
    Rectangle(Point(0., 0.), Point(pre_step_length + after_step_length, after_step_height)) - \
    Rectangle(Point(0., 0.), Point(pre_step_length, after_step_height - pre_step_height))
mesh = generate_mesh(domain, 62)

# Create boundaries
class Inlet(SubDomain):
    def inside(self, x, on_boundary):
        return on_boundary and abs(x[0]) < DOLFIN_EPS

class Bottom(SubDomain):
    def inside(self, x, on_boundary):
        return on_boundary and ( \
            (x[0] <= pre_step_length and abs(x[1] - after_step_height + pre_step_height) < DOLFIN_EPS) or \
            (x[1] <= after_step_height - pre_step_height and abs(x[0] - pre_step_length) < DOLFIN_EPS) or \
            (x[0] >= pre_step_length and abs(x[1]) < DOLFIN_EPS) \
        )
        
class Top(SubDomain):
    def inside(self, x, on_boundary):
        return on_boundary and abs(x[1] - after_step_height) < DOLFIN_EPS
    
boundaries = FacetFunction("size_t", mesh)
boundaries.set_all(0)
inlet = Inlet()
inlet_ID = 1
inlet.mark(boundaries, inlet_ID)
bottom = Bottom()
bottom_ID = 2
bottom.mark(boundaries, bottom_ID)
top = Top()
top_ID = 2
top.mark(boundaries, top_ID)

# Function spaces
V_element = VectorElement("Lagrange", mesh.ufl_cell(), 2)
Q_element = FiniteElement("Lagrange", mesh.ufl_cell(), 1)

## -------------------------------------------------- ##

## STANDARD FEniCS FORMULATION BY FEniCS MixedElement ##
def run_monolithic():
    # Function spaces
    W_element = MixedElement(V_element, Q_element)
    W = FunctionSpace(mesh, W_element)

    # Test and trial functions: monolithic
    vq  = TestFunction(W)
    (v, q) = split(vq)
    dup = TrialFunction(W)
    up = Function(W)
    (u, p) = split(up)

    # Variational forms
    F = (   nu*inner(grad(u), grad(v))*dx
          + inner(grad(u)*u, v)*dx
          - div(v)*p*dx
          + div(u)*q*dx
        )
    J = derivative(F, up, dup)

    # Boundary conditions
    inlet_bc = DirichletBC(W.sub(0), u_in, boundaries, 1)
    wall_bc = DirichletBC(W.sub(0), u_wall, boundaries, 2)
    bc = [inlet_bc, wall_bc]

    # Solve
    problem = NonlinearVariationalProblem(F, up, bc, J)
    solver  = NonlinearVariationalSolver(problem)
    solver.parameters.update(snes_solver_parameters)
    solver.solve()

    # Extract solutions
    (u, p) = up.split()
    #plot(u, title="Velocity monolithic", mode="color")
    #plot(p, title="Pressure monolithic", mode="color")
    
    return (u, p)
    
(u_m, p_m) = run_monolithic()

## -------------------------------------------------- ##

##                  block_ext FORMULATION             ##
def run_block():
    # Function spaces
    W_element = BlockElement(V_element, Q_element)
    W = BlockFunctionSpace(mesh, W_element)

    # Test and trial functions
    vq  = BlockTestFunction(W)
    (v, q) = block_split(vq)
    dup = BlockTrialFunction(W)
    up = BlockFunction(W)
    u, p = block_split(up)

    # Variational forms
    F = [nu*inner(grad(u), grad(v))*dx + inner(grad(u)*u, v)*dx - div(v)*p*dx,
           div(u)*q*dx]
    J = block_derivative(F, up, dup)

    # Boundary conditions
    inletc = DirichletBC(W.sub(0), u_in, boundaries, 1)
    wallc = DirichletBC(W.sub(0), u_wall, boundaries, 2)
    bc = BlockDirichletBC([[inletc, wallc], []])

    # Solve
    problem = BlockNonlinearProblem(F, up, bc, J)
    solver  = BlockPETScSNESSolver(problem)
    solver.parameters.update(snes_solver_parameters["snes_solver"])
    solver.solve()

    # Extract solutions
    (u, p) = up.block_split()
    #plot(u, title="Velocity block", mode="color")
    #plot(p, title="Pressure block", mode="color")
    
    return (u, p)
    
(u_b, p_b) = run_block()

## -------------------------------------------------- ##

##                  ERROR COMPUTATION                 ##
def run_error(u_m, u_b, p_m, p_b):
    plot(u_b - u_m, title="Velocity error", mode="color")
    plot(p_b - p_m, title="Pressure error", mode="color")
    interactive()

run_error(u_m, u_b, p_m, p_b)

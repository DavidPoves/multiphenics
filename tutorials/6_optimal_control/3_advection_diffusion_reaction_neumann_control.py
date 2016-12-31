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
from block_ext import *

"""
In this tutorial we solve the optimal control problem

min J(y, u) = 1/2 \int_{\Omega} (y - y_d)^2 dx + \alpha/2 \int_{\Omega} u^2 dx
s.t.
       - \epsilon \Delta y + \beta \cdot \nabla y + \sigma y = f    in \Omega
                                                \partial_n y = 0    on \Gamma_1
                                                \partial_n y = u    on \Gamma_2
                                                \partial_n y = 0    on \Gamma_3
                                                           y = 0    on \Gamma_4
             
where
    \Omega                      unit square
    u \in L^2(\Omega)           control variable
    y \in H^1_0(\Omega)         state variable
    \alpha > 0                  penalization parameter
    y_d                         desired state
    \epsilon > 0                diffusion coefficient
    \beta in IR^2               advection field
    \sigma > 0                  reaction coefficient
    f                           forcing term
    
using an adjoint formulation solved by a one shot approach
"""

## MESH ##
# Interior mesh
mesh = Mesh("data/square.xml")
boundaries = MeshFunction("size_t", mesh, "data/square_facet_region.xml")
# Neumann boundary mesh
boundary_mesh = Mesh("data/boundary_square_2.xml")

## FUNCTION SPACES ##
# Interior spaces
Y = FunctionSpace(mesh, "Lagrange", 2)
U = FunctionSpace(mesh, "Lagrange", 2)
Q = FunctionSpace(mesh, "Lagrange", 2)
# Boundary control space
boundary_U = FunctionSpace(boundary_mesh, "Lagrange", 2)
# Block space
W = BlockFunctionSpace([Y, U, Q], keep=[Y, boundary_U, Q])

## PROBLEM DATA ##
alpha = Constant(1.e-5)
y_d = Constant(1.)
epsilon = Constant(1.e-1)
beta = Constant((-1., -2.))
sigma = Constant(1.)
f = Constant(1.)

## TRIAL/TEST FUNCTIONS ##
yup = BlockTrialFunction(W)
(y, u, p) = block_split(yup)
zvq = BlockTestFunction(W)
(z, v, q) = block_split(zvq)

## MEASURES ##
ds = Measure("ds")(subdomain_data=boundaries)

## OPTIMALITY CONDITIONS ##
state_operator = epsilon*inner(grad(y),grad(z))*dx + inner(beta, grad(y))*z*dx + sigma*y*z*dx
adjoint_operator = epsilon*inner(grad(p),grad(q))*dx - inner(beta, grad(p))*q*dx + sigma*p*q*dx
a = [[y*q*dx        , 0              , adjoint_operator], 
     [0             , alpha*u*v*ds(2), - p*v*ds(2)     ],
     [state_operator, - u*z*ds(2)    , 0               ]]
f =  [y_d*q*dx,
      0       ,
      f*z*dx   ]
bc = BlockDirichletBC([[DirichletBC(W.sub(0), Constant(0.), boundaries, 4)],
                       [],
                       [DirichletBC(W.sub(2), Constant(0.), boundaries, 4)]])

## SOLUTION ##
yup = BlockFunction(W)
(y, u, p) = block_split(yup)

## FUNCTIONAL ##
J = 0.5*inner(y - y_d, y - y_d)*dx + 0.5*alpha*inner(u, u)*ds(2)

## UNCONTROLLED FUNCTIONAL VALUE ##
A_state = assemble(a[2][0])
F_state = assemble(f[2])
[bc_state.apply(A_state) for bc_state in bc[0]]
[bc_state.apply(F_state)  for bc_state in bc[0]]
solve(A_state, y.vector(), F_state)
print "Uncontrolled J =", assemble(J)
plot(y, title="uncontrolled state")
interactive()

## OPTIMAL CONTROL ##
A = block_assemble(a)
F = block_assemble(f)
bc.apply(A)
bc.apply(F)
block_solve(A, yup.block_vector(), F)
print "Optimal J =", assemble(J)
plot(y, title="state")
plot(u, title="control")
plot(p, title="adjoint")
interactive()


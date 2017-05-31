// Copyright (C) 2016-2017 by the block_ext authors
//
// This file is part of block_ext.
//
// block_ext is free software: you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// block_ext is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with block_ext. If not, see <http://www.gnu.org/licenses/>.
//

#ifndef __BLOCK_PETSC_SUB_VECTOR_H
#define __BLOCK_PETSC_SUB_VECTOR_H

#ifdef HAS_PETSC

#include <dolfin/la/PETScVector.h>
#include <block/la/BlockInsertMode.h>
#include <block/la/BlockPETScVector.h>

namespace dolfin
{
  class BlockPETScVector;
  
  /// This is an extension of PETScVector to be used while assemblying block forms, that
  /// a) carries out the extraction of a sub vector
  /// b) in case of restrictions, overrides get/set/add methods to convert original index without restriction to index with restriction
  class BlockPETScSubVector : public PETScVector
  {
  public:
    /// Constructor
    BlockPETScSubVector(const GenericVector & x,
                        const std::vector<dolfin::la_index> & block_owned_dofs__global_numbering,
                        const std::map<dolfin::la_index, dolfin::la_index> & original_to_sub_block,
                        const std::map<dolfin::la_index, dolfin::la_index> & original_to_block,
                        std::shared_ptr<const IndexMap> sub_index_map,
                        std::size_t unrestricted_size,
                        BlockInsertMode insert_mode);

    /// Destructor
    virtual ~BlockPETScSubVector();
    
    //--- Implementation of the GenericVector interface ---
    
    /// Return size of vector.
    /// Note that the number returned here is the size of the *unrestricted* subvector,
    /// and *not* the actual size of the existing (*restricted*) subvector.
    virtual std::size_t size() const;
    
    /// Get block of values using global indices (all values must be
    /// owned by local process, ghosts cannot be accessed)
    virtual void get(double* block, std::size_t m,
                     const dolfin::la_index* rows) const;

    /// Get block of values using local indices
    virtual void get_local(double* block, std::size_t m,
                           const dolfin::la_index* rows) const;

    /// Set block of values using global indices
    virtual void set(const double* block, std::size_t m,
                     const dolfin::la_index* rows);

    /// Set block of values using local indices
    virtual void set_local(const double* block, std::size_t m,
                           const dolfin::la_index* rows);

    /// Add block of values using global indices
    virtual void add(const double* block, std::size_t m,
                     const dolfin::la_index* rows);

    /// Add block of values using local indices
    virtual void add_local(const double* block, std::size_t m,
                           const dolfin::la_index* rows);

    /// Get all values on local process
    virtual void get_local(std::vector<double>& values) const;

    /// Set all values on local process
    virtual void set_local(const std::vector<double>& values);

    /// Add values to each entry on local process
    virtual void add_local(const Array<double>& values);
    
    /// Add multiple of given vector (AXPY operation)
    virtual void axpy(double a, const GenericVector& x);

    /// Replace all entries in the vector by their absolute values
    virtual void abs();

    /// Return inner product with given vector
    virtual double inner(const GenericVector& v) const;

    /// Return norm of vector
    virtual double norm(std::string norm_type) const;

    /// Return minimum value of vector
    virtual double min() const;

    /// Return maximum value of vector
    virtual double max() const;

    /// Return sum of values of vector
    virtual double sum() const;

    /// Return sum of selected rows in vector
    virtual double sum(const Array<std::size_t>& rows) const;

    /// Multiply vector by given number
    virtual const PETScVector& operator*= (double a);

    /// Multiply vector by another vector pointwise
    virtual const PETScVector& operator*= (const GenericVector& x);

    /// Divide vector by given number
    virtual const PETScVector& operator/= (double a);

    /// Add given vector
    virtual const PETScVector& operator+= (const GenericVector& x);

    /// Add number to all components of a vector
    virtual const PETScVector& operator+= (double a);

    /// Subtract given vector
    virtual const PETScVector& operator-= (const GenericVector& x);

    /// Subtract number from all components of a vector
    virtual const PETScVector& operator-= (double a);

    /// Assignment operator
    virtual const GenericVector& operator= (const GenericVector& x);

    /// Assignment operator
    virtual const PETScVector& operator= (double a);

    //--- Special functions ---

    /// Return linear algebra backend factory
    virtual GenericLinearAlgebraFactory& factory() const;

    //--- Special PETSc functions ---

    /// Sets the prefix used by PETSc when searching the options
    /// database
    void set_options_prefix(std::string options_prefix);

    /// Returns the prefix used by PETSc when searching the options
    /// database
    std::string get_options_prefix() const;

    /// Call PETSc function VecSetFromOptions on the underlying Vec
    /// object
    void set_from_options();

    /// Assignment operator
    const PETScVector& operator= (const PETScVector& x);
    
  private:
  
    void to_restricted_subvector_indices(
      const std::vector<dolfin::la_index> & block_unrestricted_subvector_indices, std::vector<dolfin::la_index> & block_restricted_subvector_indices,
      std::vector<bool> * is_in_restriction = NULL
    ) const;
    void to_restricted_vector_indices(
      const std::vector<dolfin::la_index> & block_unrestricted_subvector_indices, std::vector<dolfin::la_index> & block_restricted_vector_indices,
      std::vector<bool> * is_in_restriction = NULL
    ) const;
    void to_restricted_subvector_indices_and_values(
      const std::vector<dolfin::la_index> & block_unrestricted_subvector_indices, std::vector<dolfin::la_index> & block_restricted_subvector_indices,
      const std::vector<double> & block_unrestricted_subvector_values, std::vector<double> & block_restricted_subvector_values
    ) const;
    void from_restricted_subvector_values(
      Array<double> & block_unrestricted_subvector_values, const std::vector<double> & block_restricted_subvector_values,
      const std::vector<bool> & is_in_restriction
    ) const;
    
    const BlockPETScVector & _global_vector;
    const std::map<dolfin::la_index, dolfin::la_index> & _original_to_sub_block;
    const std::map<dolfin::la_index, dolfin::la_index> & _original_to_block;
    const std::size_t _unrestricted_size;
    /*PETSc*/ InsertMode _insert_mode;
    IS _is;
    Vec _x;
    VecScatter _scatter;
  };
  
}

#endif

#endif

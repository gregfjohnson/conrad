"""
Copyright 2016 Baris Ungun, Anqi Fu

This file is part of CONRAD.

CONRAD is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

CONRAD is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with CONRAD.  If not, see <http://www.gnu.org/licenses/>.
"""
from conrad.compat import *

import abc

from conrad.optimization.preprocessing import ObjectiveMethods

@add_metaclass(abc.ABCMeta)
class ClusteredProblem(object):
	def __init__(self, case, reference_frame_name, clustered_frame_name):
		self.__case = case
		self.__reference_frame = reference_frame_name
		self.__clustered_frame = clustered_frame_name
		self.__reference_anatomy = None
		self.reload_reference_frame()
		self.__reference_anatomy = case.anatomy.clone()
		self.reload_clustered_frame()
		self.methods = ObjectiveMethods

	@property
	def case(self):
		return self.case

	@property
	def reference_anatomy(self):
		return self.reference_anatomy

	def reload_reference_frame(self):
		self.case.physics.load_frame(self.__reference_frame)

	def reload_clustered_frame(self):
		self.case.physics.load_frame(self.__clustered_frame)

	def dose_objective_primal_eval(self, anatomy):
		return sum(listmap(self.methods.primal_eval, anatomy))

	@abc.abstractmethod
	def clear(self):
		raise NotImplementedError

	@abc.abstractmethod
	def solve_and_bound_clustered_problem(self, case, reference_anatomy,
										  **solver_options):
		raise NotImplementedError

	@abc.abstractmethod
	def cluster_and_bound(self, case, reference_frame_name,
						  clustered_frame_name, **solver_options):
		raise NotImplementedError

	def plan(self, **solver_options):
		ub, lb, run = self.cluster_and_bound(**solver_options)
		run.output.optimal_variables['upper_bound'] = ub
		run.output.optimal_variables['lower_bound'] = lb
		run.output.optimal_variables['suboptimality'] = 100. * (ub - lb) / lb
		return run


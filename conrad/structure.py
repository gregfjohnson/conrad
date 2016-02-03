from np import ndarray, array, squeeze
from scipy.sparse import csr_matrix, csc_matrix
from conrad.dvh import DVHCurve

# TODO: unit test
"""
TODO: structure.py docstring
"""

DOSE_DEFAULT = 1.
W_UNDER_DEFAULT = 1.
W_OVER_DEFAULT = 0.05
W_NONTARG_DEFAULT = 0.1

class Structure(object):
	""" TODO: docstring """
	def __init__(self, label, **options):
		""" TODO: docstring """
		# basic information
		self.label = label
		self.name = options['name'] if 'name' in options else ''
		self.is_target = options['is_target'] if 'is_target' in options else False

		# number of voxels in structure
		self.size = options['size'] if 'size' in options else None

		# prescribed dose
		self.dose = options['dose'] if 'dose' in options else 0.
		if self.dose is not None:
			self.is_target = self.dose > 0 
		if self.is_target is not None:
			if self.is_target and self.dose is None:
			self.dose = DOSE_DEFAULT

		# dictionary of DoseConstraint objects attached to 
		# structure, keyed by constraint id (which is passed 
		# in by owner of Structure object).
		self.dose_constraints = {}

		# dvh curve and constraints data for plotting
		self.dvh_curve = DVHCurve()

		# (pointer to) subsection of dose matrix corresponding to structure
		self.A_full = options['A'] if 'A' in options else None

		# TODO:
		# clustered version of same dose matrix, voxels
		# voxel->cluster mapping vector
		# voxel counts per cluster
		# self.A_clu = None
		# self.v2c = None
		# self.voxel_per_cluster = None

		# fully compressed version of same dose matrix
		# self.A_lin = None


		self.A = A_full
		# TODO: switching to clustered / fully compressed
		# representation of matrix based on **options keyword args

		# dose vector
		self._y = None

		# objective weights (set to defaults if not provided)
		self._w_under = options['w_under'] if 'w_under' in options else None
		self._w_over = options['w_over'] if 'w_over' in options else None
		if self.is_target is not None:
			if self.is_target:
				if self._w_under is None: 
					self._w_under = W_UNDER_DEFAULT
				if self._w_over is None:
					self._w_over = W_OVER_DEFAULT
			else:
				if self._w_over is None:
					self._w_over = W_NONTARG_DEFAULT


	def set_objective(dose, w_under, w_over):
		if self.is_target:
			if dose is not None:
				self.dose = dose
			if w_under is not None:
				self.w_under = w_under
		if w_over is not None:
			self.w_over = w_over

	@property
	def w_under(self):
		""" TODO: docstring """
		if isinstance(self._w_under, (float, int)):
		    return self._w_under / float(self.size)
		else:
			return None
	
	@property
	def w_under_raw(self):
	    return self._w_under
	
	@property
	def w_over(self):
		""" TODO: docstring """
		if isinstance(self._w_oveer, (float, int)):
		    return self._w_over / float(self.size)
		else:
			return None
	
	@property
	def w_over_raw(self):
	    return self._w_under

	def calc_y(self, x):
		""" TODO: docstring """
		x = squeeze(array(x))
		if isinstance(self.A, (csr_matrix, csc_matrix)):
			self.y = squeeze(self.A * x)
		elif isinstance(A, ndarray):
			self.y = A.dot(x)
		else:
			TypeError("input A must by a numpy or "
				"scipy sparse matrix")

	def get_y(self, x):
		""" TODO: docstring """
		self.calc_y(x)
		return self._y

	@property
	def y(self):
		""" TODO: docstring """
	    return self._y
	
	def has_constraint(self, constr_id):
		""" TODO: docstring """
		return constr_id in self.dose_constraints

	def remove_constraint(self, constr_id):
		""" TODO: docstring """
		if self.has_constraint(constr_id):
			del self.dose_constraints[constr_id]

	def add_constraint(self, constr_id, constr):
		""" TODO: docstring """
		self.dose_constraints[constr_id] = constr	

	@property
	def plotting_data(self):
		""" TODO: docstring """
		d = {}
		d['curve'] = self.dvh_curve.plotting_data
		d['constraints'] = [dc.plotting_data for dc in self.dose_constraints]


	def __header_string(self):
		out = 'Structure: {}'.format(self.label)
		if self.name != '':
			out += " ({})".format(self.name)
			out += "\n"
		return out		

	def objective_string(self):
		""" TODO: docstring """
		out = self.__header_string()
		out += "target? {}\n".format(self.is_target)
		out += "rx dose: {}\n".format(self.dose)
		if self.is_target:
			out += "weight_under: {}\n".format(self._w_under)
			out += "weight_over: {}\n".format(self._w_over)			
		else:
			out += "weight: {}\n".format(self._w_over)
		out += "\n"
		return out

	def constraints_string(self):
		""" TODO: docstring """
		out = self.__header_string()
		for dc in self.dose_constraints.itervals():
			out += dc.__str__()
		return out
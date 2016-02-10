import numpy as np
from numpy import copy as np_copy, sort as np_sort, linspace, insert
from collections import OrderedDict

"""
TODO: dvh.py docstring
"""

def canonical_string_to_tuple(string_constraint):
	""" TODO: docstring

	convert input string, in canonical form:
		"D{p} <= {d}" or "D{p} >= {d}"

	to canonical tuple 
		(d, p/100, '<') or (d, p/100, '>'), respectively
	"""
	left, right = string_constraint.split('=')
	fraction = float(left.strip('<').strip('>').strip('D')) / 100.
	dose = float(right.strip('Gy'))
	direction = '<' if '<' in string_constraint else '>'
	return (dose, fraction, direction)


def tuple_to_canonical_string(tuple_constraint):
	""" TODO: docstring

	convert input tuple, in canonical form:
		(d, f, '<') or (d, f, '>')

	to canonical string 
		"D{f * 100} <= {d}" or "D{f * 100} >= {d}", respectively
	"""
	d, f, ineq = tuple_constraint
	return "D{} {}= {}Gy".format(f * 100, ineq, d)

	return (dose, fraction, direction)

class DoseConstraint(object):
	"""
		Dose constraint is specified as a tuple:
		(dose, fraction, direction)

		`dose' must be a float in [0, +infty)
		`fraction' must be float in [0, 1]
		`direction' is a character in {'<', '>'}

		For instance,

		(30, 0.2, '<')

		is interpreted as the (upper) DVH constraint:

			D20 <= 30 Gy, i.e.,

		"no more than 20 percent of the structure voxels 
		may receive over 30Gy of dose",

		Conversely,
		(55, 0.8, '>')

		is interpreted as the (lower) DVH constaint:

			D80 >= 55 Gy, i.e.,
		
		"at least 80 percent of the structure voxels 
		must receive at least 55Gy of dose"

	"""

	def __init__(self, dose, fraction, direction):
		""" TODO: docstring """
		if fraction < 0. or fraction > 1.:
			raise ValueError("fraction %f must be in [0,1]" % (fraction))
		
		self.dose_requested = dose
		self.fraction = fraction
		self.direction = direction
		self.dose_actual = None


	def set_actual_dose(self, slack):
		""" TODO: docstring """
		if slack is None:
			self.dose_actual = self.dose_requested
			return

		if self.direction == '<':
			self.dose_actual = self.dose_requested + slack
		else:
			self.dose_actual = self.dose_requested - slack

	@property
	def upper(self):
		""" TODO: docstring """
		return self.direction == '<'

	@property
	def plotting_data(self):
		""" TODO: docstring """
		return {'percentile' : 2 * [100 * self.fraction], 
			'dose' :[self.dose_requested, self.dose_actual], 
			'symbol' : self.direction}


	def get_maxmargin_fulfillers(self, y, had_slack = False):
		""" 
		given dose vector y, get the indices of the voxels that
		fulfill this dose constraint (self) with maximum margin

		given len(y), if m voxels are required to respect the
		dose constraint exactly, y is assumed to contain 
		at least m entries that respect the constraint
		(for instance, y is generated by a convex program
		that includes a convex restriction of the dose constraint)


		procedure:
		- get margins: (y - self.dose_requested)
		- sort margin indices by margin values 
		- if upper bound, return indices of p most negative entries 
			(first p of sorted indices; numpy.sort sorts small to large)
		- if lower bound, return indices p most positive entries 
			(last p of sorted indices; numpy.sort sorts small to large)
		
		p = percent non-violating * structure size
			= percent non-violating * len(y)

		"""

		non_viol = self.fraction if not self.upper else (1 - self.fraction)
		
		# int() conversion truncates
		n_returned = int(non_viol * len(y))

		start = 0 if self.upper else -n_returned
		end = n_returned if self.upper else -1
		if had_slack and self.dose_actual is not None:
			dose = self.dose_actual
		else:
			dose = self.dose_requested
		return (y - dose).argsort()[start:end]

	def __str__(self):
		return 'D{} {}= {}Gy\n'.format(
			100 * self.fraction,
			self.direction, 
			self.dose_requested)
			
class DoseSummary(object):
	"""
	TODO: DoseSummary docstring
	"""
	
	def __init__(self, percentiles = [0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]):
		""" TODO: docstring """
		self.percentiles = percentiles
		self.scores = None
		self.mean = None
		self.stdev = None
		self.minimum = None
		self.maximum = None
	
	def make(self, y):
		self.mean = np.mean(y)
		self.stdev = np.std(y)
		self.minimum = np.amin(y)
		self.maximum = np.amax(y)
		self.scores = np.percentile(y, self.percentiles)
	
	@property
	def table_data(self):
		""" TODO: docstring """
		table = OrderedDict({'mean': self.mean})
		table['stdev'] = self.stdev
		table['min'] = self.minimum
		table['max'] = self.maximum
		# TODO: Append percentiles in summary table
		# for idx in xrange(1, len(self.scores)):
		#	plabel = 'p' + str(self.percentiles[idx])
		#	table[plabel] = self.scores[idx]
		return table
	
	@property
	def header(self):
		return self.table_data.keys()

class DVHCurve(object):
	""" 
	TODO: DVHCurve docstring
	"""

	MAX_LENGTH = 1000

	def __init__(self):
		""" TODO: docstring """
		self.doses = None
		self.percentiles = None

	def make(self, y, maxlength = MAX_LENGTH):
		""" TODO: docstring """
		if len(y) <= maxlength:
			doses = y[:]
		elif len(y) <= 2 * maxlength:
			doses = y[::2]
		else:
			doses = y[::len(y) / maxlength]

		self.doses = insert(np_sort(np_copy(doses)), 0, 0.)
		self.percentiles = insert(linspace(100, 0, len(self.doses) - 1), 0, 100.)

	@property
	def plotting_data(self):
		""" TODO: docstring """
		return {'percentile' : self.percentiles, 'dose' : self.doses}

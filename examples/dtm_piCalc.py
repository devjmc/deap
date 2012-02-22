#    This file is part of DEAP.
#
#    DEAP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    DEAP is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with DEAP. If not, see <http://www.gnu.org/licenses/>.

"""
Calculation of Pi using a Monte Carlo method.
"""

from math import hypot
from random import random

from deap import dtm

def test(tries):
    return sum(hypot(random(), random()) < 1 for i in xrange(tries))

def calcPi(n, t):
    expr = dtm.repeat(test, n, t)
    pi_value = 4. * sum(expr) / float(n*t)
    print("pi = " + str(pi_value))
    return pi_value

dataPi = dtm.start(calcPi, 3000, 5000)

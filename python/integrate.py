#!/usr/bin/env python
# coding=utf-8

from math import *
from ROOT import TF1

gamma = 0.679
dgamma = -0.17629 * 0.679
CPd = 0.224
CPdbar = 0.224

intlo = 0.2
inthi = 10

norm_num = lambda d, dbar: 4*gamma + (d + dbar)*dgamma
norm_den = 4*gamma*gamma - dgamma*dgamma

# common constants
num = norm_num(CPd, CPdbar)
den = norm_den

# basic forms
cDsform = 'cosh(%E * x/2) + %E * sinh(%E * x/2)'  % (dgamma, CPd, dgamma)
cDbsform = 'cosh(%E * x/2) + %E * sinh(%E * x/2)'  % (dgamma, CPdbar, dgamma)
expform = 'exp(%E * x)' % -gamma
sinhform = 'sinh(%E * x/2)' % dgamma

commonform1 = '(%E * x + log(%s) + log(%E))' % (-gamma, cDsform, den/num + 1)

## Integrals
# final integral forms (assuming D and Dbar are equal)
term1 = '%s * %s * (%s)' % (commonform1, expform, cDsform)
term2 = '%s * %s * %s' % (commonform1, expform, sinhform)
term3 = '%s/%s * (%s - %E * %s)**2' % (expform, cDsform, sinhform, dgamma/num, cDsform)

coef1 = 2 * dgamma * dgamma * den / (num * num * num)
coef2 = 2 * dgamma * den / (num * num)
coef3 = den / num

# ∂²/∂D²(LL)
DDint1 = TF1('DDint1', term1, 0, 100)
DDint2 = TF1('DDint2', term2, 0, 100)
DDint3 = TF1('DDint3', term3, 0, 100)

DDintegral = 2 * coef1 * DDint1.Integral(intlo, inthi)
DDintegral -= coef2 * DDint2.Integral(intlo, inthi)
DDintegral += coef3 * DDint3.Integral(intlo, inthi)

# ∂²/∂D̄∂D(LL)
commonform2 = '(%E * x + log(%s) + log(%E))' % (-gamma, cDsform, den/num + 2)

term4 = '%s * %s * (%s)' % (commonform2, expform, cDsform)
term5 = '%s * %s * %s' % (commonform2, expform, sinhform)

DDbarint1 = TF1('DDbarint1', term4, 0, 100)
DDbarint2 = TF1('DDbarint2', term5, 0, 100)

DDbarintegral = 2 * coef1 * DDbarint1.Integral(intlo, inthi) # 2 + 2 because of Dbar terms
DDbarintegral -= coef2 * DDbarint2.Integral(intlo, inthi) # 1 + 1 because of Dbar terms
DDbarintegral *= 2

# since CPd and CPdbar are equal, no need to recalculate integrals
mat = [
    [0.5*13000 * DDintegral,    0.5*13000 * DDbarintegral],
    [0.5*13000 * DDbarintegral, 0.5*13000 * DDintegral]
]

print 'Matrix'
for i in range(2):
    print '( %E   %E )' % (mat[i][0], mat[i][1])

diag_ele = mat[0][0]
offd_ele = mat[0][1]

correlation = -offd_ele / sqrt(diag_ele*diag_ele)
print 'Correlation: %E' % correlation

# factor of sqrt(2) missing
error = sqrt(1 / (diag_ele * diag_ele - offd_ele * offd_ele) * diag_ele)
print 'Error: %E' % error

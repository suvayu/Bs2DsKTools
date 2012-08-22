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

# basic forms
cDsform = 'cosh(%E*x/2) + %E*sinh(%E*x/2)'  % (dgamma, CPd, dgamma)
cDbsform = 'cosh(%E*x/2) + %E*sinh(%E*x/2)'  % (dgamma, CPdbar, dgamma)
expform = 'exp(%E*x)' % -gamma
sinhform = 'sinh(%E*x/2)' % dgamma
Gtform = '%E*x' % gamma

## Integrals
# final integral forms
xlnxform = '%s*(%s)*log(%s)'
sinhlnform = '%s*%s*(1 + log(%s))'
sinh2form = '%s*%s*%s'

# coefficients
num = norm_num(CPd, CPdbar)
den = norm_den
coef1 = den * dgamma * dgamma / (num * num * num)
coef2 = - den * dgamma / (num * num)
coef3 = den / num

# ∂²/∂D²(LL)
DDint1 = TF1('DDint1', xlnxform % (expform, cDsform, cDsform), 0, 100)
DDint2 = TF1('DDint2', sinhlnform % (expform, sinhform, cDsform), 0, 100)
DDint3 = TF1('DDint3', sinh2form % (expform, sinhform, sinhform), 0, 100)

# These assume D and Dbar are equal
DDintegral = 4 * coef1 * DDint1.Integral(intlo, inthi) # 2 + 2 because of Dbar terms
DDintegral += -2 * coef2 * DDint2.Integral(intlo, inthi)
DDintegral += coef3 * DDint3.Integral(intlo, inthi)

# ∂²/∂D̄∂D(LL)
DDbarintegral = 4 * coef1 * DDint1.Integral(intlo, inthi) # 2 + 2 because of Dbar terms
DDbarintegral += -2 * coef2 * DDint2.Integral(intlo, inthi) # 1 + 1 because of Dbar terms

# integral forms
Gtxform = '%s*%s*(%s)'
Gtsinhform = '%s*%s*%s'
xform = '%s*(%s)'
sinhintform = '%s*%s'

# coefficients
coef4 = 2 * den * dgamma * dgamma / (num * num * num)
coef5 = 2 * den * dgamma / (num * num)

# ∂²/∂D²(PDF·Γt)
DDint4 = TF1('DDint4', Gtxform % (expform, Gtform, cDsform), 0, 100)
DDint5 = TF1('DDint5', Gtsinhform % (expform, Gtform, sinhform), 0, 100)

# one extra 2 because of equal contribution from D and D̄
DDintegral += -2 * coef4 * DDint4.Integral(intlo, inthi)
DDintegral += 2 * coef5 * DDint5.Integral(intlo, inthi)

# ∂²/∂D̄∂D(PDF·Γt)
DDbarintegral += -2 * coef4 * DDint4.Integral(intlo, inthi)

# ∂²/∂D²(PDF·ln[Norm])
DDint6 = TF1('DDint6', xform % (expform, cDsform), 0, 100)
DDint7 = TF1('DDint7', sinhintform % (expform, sinhform), 0, 100)

coef6 = 2 * den * den * dgamma * dgamma / (num * num * num)
coef7 = -2 * 2 * den * den * dgamma / (num * num)
coef8 = 2 * (dgamma - 1) * den / (num * num) * log(num/den)

# one extra 2 because of equal contribution from D and D̄
DDintegral += coef6 * DDint6.Integral(intlo, inthi)
DDintegral += (coef7 + coef8) * DDint7.Integral(intlo, inthi)

# ∂²/∂D̄∂D(PDF·ln[Norm])
coef9 = 2 * dgamma * den / (num * num) * log(num/den)

DDbarintegral += 2 * coef6 * DDint6.Integral(intlo, inthi)
DDbarintegral += (coef7 / 2 + coef9) * DDint7.Integral(intlo, inthi)

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

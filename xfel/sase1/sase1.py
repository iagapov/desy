'''
input deck for XFEL SASE3 beamline
'''

from ocelot.cpbd.elements import *
from ocelot.optics.elements import Crystal
from ocelot.optics.bragg import *
from ocelot.cpbd.beam import *
import numpy as np

m = 1.0
cm = 1.e-2
mm = 1.e-3
mum = 1.e-6

und = Undulator (nperiods=125,lperiod=0.040,Kx=0.0, id = "und"); voodoo=0.69

d = Drift (l=1.0, id = "d")

d1 = Drift (l=0.55, id = "d1")
d2 = Drift (l=0.45, id = "d2")
d3 = Drift (l=0.27, id = "d0.05nm3")

b1 = RBend (l=0.0575, angle=0.0, id = "b1")
b2 = RBend (l=0.0575, angle=-0.0, id = "b2")

#psu=(b1,b2,b2,b1,d3)
psu= Drift (l=b1.l*2 + b2.l*2 + d3.l, id = "d1")

qf = Quadrupole (l=0.1, id = "qf")
qd = Quadrupole (l=0.1, id = "qd")
qfh = Quadrupole (l=0.05, id = "qf")
qdh = Quadrupole (l=0.05, id = "qf")

cell_ps = (und, d2, qf, psu, und, d2, qd, psu)

sase1 = (und, d2, qd, psu) + 17*cell_ps
sase1_cell = (und, d2, qf, psu, und)
def sase1_segment(n=0): return (und, d2, qd, psu) + n*cell_ps

# for matching
extra_fodo = (und, d2, qdh)
l_fodo = qf.l / 2 + (b1.l + b2.l + b2.l + b1.l + d3.l) + und.l + d2.l + qf.l / 2 

#self-seeding
chicane = Drift(l=5.1)
chicane.cryst = Crystal(r=[0,0,0*cm], size=[5*cm,5*cm,100*mum], no=[0,0,-1], id="cr1")
chicane.cryst.lattice =  CrystalLattice('C')
chicane.cryst.psi_n = -pi/2. #input angle psi_n according to Authier (symmetric reflection, Si)

'''
TODO: for future
geo = Geometry([cr1])
chicane.geo = geo
chicane.geo_transform = t
'''

# uncomment this for simplified SR calculation
## und = Undulator (nperiods=125*35,lperiod=0.040,Kx=1.9657, id = "und")
## sase1=(und)


# example settings 28m beta, 0.05nm wavelength
und.Kx = 1.9657
qf.k1 = 0.7181242
qd.k1 = -0.7181242
qfh.k1 = 0.7181242
qdh.k1 = -0.7181242
b1.angle = 1.7926311e-5
b2.angle =-1.7926311e-5


# setting xxxnm wavelength
#und.Kx = 1.8

und.Kx = 2.395

beam = Beam()
beam.E = 14.0
beam.sigma_E = 0.002
beam.emit_xn = 0.4e-6 
beam.emit_yn = 0.4e-6 
beam.gamma_rel = beam.E / (0.511e-3)
beam.emit_x = beam.emit_xn / beam.gamma_rel
beam.emit_y = beam.emit_yn / beam.gamma_rel
beam.beta_x = 33.7
beam.beta_y = 23.218
beam.alpha_x = 1.219
beam.alpha_y = -0.842

beam.tpulse = 80    # electron bunch length in fs (rms)
beam.C = 1.0        # bunch charge (nC)
beam.I = 1.0e-9 * beam.C / ( np.sqrt(2*pi) * beam.tpulse * 1.e-15 ) 

#beam.emit = {0.02: [0.32e-6,0.32e-6], 0.1: [0.39e-6,0.39e-6], 0.25: [0.6e-6,0.6e-6], 0.5: [0.7e-6,0.7e-6], 1.0: [0.97e-6,0.97e-6]}
beam.emit = {0.02: [0.2e-6,0.18e-6], 0.1: [0.32e-6,0.27e-6], 0.25: [0.4e-6,0.36e-6], 0.5: [0.45e-6,0.42e-6], 1.0: [0.8e-6,0.84e-6]}

def f1(n, n0, a0, a1, a2):
    '''
    piecewise-quadratic tapering function
    '''
    for i in xrange(1,len(n0)):
        if n < n0[i]:
            return a0 + (n-n0[i-1])*a1[i-1] + (n-n0[i-1])**2 * a2[i-1]
        a0 += (n0[i]-n0[i-1])*a1[i-1] + (n0[i]-n0[i-1])**2 * a2[i-1]
    
    return 1.0

def f2(n, n0, a0, a1, a2):
    '''
    exponential tapering
    '''
    
    if n <= n0:
        return a0
    
    return a0 * (  1 + a1 * (n - n0)**a2 )



def get_taper_coeff(ebeam, ephoton):
    if ebeam == 14:
        if ephoton > 400 and ephoton < 1000:
            n0 = [0,6,25,35]
            a0 = 0.999
            a1 = [-0., -0.001,  -0.00 ]
            a2 = [0., -0.00012, -0.000 ]
            return n0, a0, a1, a2
        if ephoton >= 1000 and ephoton < 2000:
            n0 = [0,7, 25,35]
            a0 = 0.999
            a1 = [-0., -0.001,  -0.00 ]
            a2 = [0., -0.00012, -0.000 ]
            return n0, a0, a1, a2
        if ephoton >= 2000 and ephoton < 2999:
            n0 = [0,8, 25,35]
        #n0 = [0,10, 25,35] # 1nc
            a0 = 0.999
            a1 = [-0., -0.001,  -0.00 ]
            a2 = [0., -0.0001, -0.000 ]
        #a2 = [0., -0.00005, -0.000 ]
            return n0, a0, a1, a2
        if ephoton >= 2999:
            n0 = [0,10, 25,35]
        #n0 = [0,13, 25,35] # 1nc
            a0 = 0.999
            a1 = [-0., -0.001,  -0.00 ]
            a2 = [0., -0.0001, -0.000 ]
            return n0, a0, a1, a2

    if ebeam == 8.5:
        pass



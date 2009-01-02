#!/usr/bin/env python
#coding=utf-8

from pylab import *
from scipy import *


class lnlif:

    def __init__(self):
        # a place to store the spikes
        self.spikes = [0]

        # number of time slots to integrate until
        self.t_max = 1000
        self.dt = 1

        # leak reversal potential : milli Volt
        self.V_leak = 0.9
        # membrane leak conductance : siemens
        self.g =  1.e-2
        # reset voltage : milli Volt
        self.V_reset = 0
        # potential voltage : milli Volt
        self.V_threshold = 1

        # model of the stimulus as a vector : milli Ampere
        self.stim = zeros(self.t_max) 

        # st.d. of the gaussian white noise process.
        self.sigma = 0.02
        self.noise = False
        self.h_scale = 0.5

        # spationtemporal linear kernel
        # in this case modeled as a difference of gaussians
        n = stats.distributions.norm
        x = arange(-10,10,0.05)
        pos = stats.distributions.norm_gen.pdf(n,x,loc=0)
        neg = stats.distributions.norm_gen.pdf(n,x,loc=-4,scale=2)
        self.k = ( pos - neg)
        

    def set_rand_input(self):
        """ random input current """
        self.stim =rand(self.t_max)

    def set_const_input(self,current):
        """ constant input current """
        self.stim[:] = current

    def set_depolarizing_h(self):
        self.h = self.h_scale * 1/exp(self.get_time())

    def set_const_h(self):
        self.h = zeros(len(self.get_time()))

    def set_hyperdepolarizing_h(self):
        self.h =  self.h_scale * -1/exp(self.get_time())

    def get_time(self):
        return arange(0,self.t_max/self.dt,self.dt)

    def reset_spikes(self):
        self.spikes = [0]


    def set_convolved_input(self):
        """ setup the input convolved with the linear filter"""
        # now convolve the linear filter k with the stimulus
        # this really should be of length t_max
        # check that the convolution does indeed return this.
        # may need to pad out the linear kernel
        self.i_stim = 0.2 + convolve(self.stim,self.k, mode='same')

    def integrate(self,x,t):
        return -self.g*(x - self.V_leak) + self.i_stim[t] + self.i_hist(t)
        
  
    def i_hist(self,t):
        # in the case where the temporal basis functions are not knowen
        # returning zero here brings us back to the more standard lif
        # model
        return self.h[t-self.spikes[-1]]

    def add_noise(self, dt):
        """ gaussian additive white noise"""
        if (self.noise):
            return self.sigma * sqrt(dt) * random.randn();
        else:
            return 0


    def euler(self, x_0):
        """ euler method for for solving ODEs
        lif - a class that implements the integrate(x,t) function
        x_0 initial value for x
        t_max maximum time
        dt change in time """
        potential = zeros(self.t_max/self.dt)
        potential[0] = x_0 
        time = arange(0,self.t_max,self.dt)
        for i in xrange (1,int(self.t_max/self.dt)):
            if potential[i-1] >= self.V_threshold:
                self.spikes.append(i)
                potential[i] = self.V_reset;
            else:
                potential[i] = potential[i-1] + \
                self.integrate(potential[i-1],time[i-1]) * self.dt + \
                self.add_noise(self.dt)
        return (time, potential)


lif = lnlif() # init model
lif.set_const_input(0.01); # set constant input
lif.i_stim = lif.stim # setup stimulus
# lif.set_convolved_input();
lif.noise = True
lif.set_const_h();



time, potential = lif.euler(lif.V_reset)

subplot(3,2,1), plot(time,potential), title('const h')
subplot(3,2,2), plot(lif.h)

lif.reset_spikes()
lif.set_depolarizing_h();
time, potential = lif.euler(lif.V_reset)

subplot(3,2,3), plot(time,potential), title('depolarizing h')
subplot(3,2,4), plot(lif.h)


lif.reset_spikes()
lif.set_hyperdepolarizing_h();
time, potential = lif.euler(lif.V_reset)

subplot(3,2,5), plot(time,potential), title('depolarizing h')
subplot(3,2,6), plot(lif.h)

print len(lif.h)

#subplot(2,3,2), plot(lif.k), title('k')
#subplot(2,3,3), plot(time,lif.i_stim), title('I_stim')
#subplot(2,3,4), plot(lif.stim), title('stim')
#subplot(2,3,5), plot(lif.h),
show()


# notes:
# integrate for length of stimulus

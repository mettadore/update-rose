from __future__ import division
from GChartWrapper import *
from math import pi, radians, degrees, sin, cos, atan2

class RoseBase(object):
    def __init__(self):
        self._lst = None
        self._bad = -1
        self.rose = None
        self.coding = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        self._range = (0.0, 360.0)
        self._step = 5
        self._color = 'red'
        self._size = 500
        self._labels = ['N','E','S','W']
        self._mean = None
        self._mod = None

    def set_list(self, lst): self._lst = lst
    def get_list(self): return self._lst
    list = property(get_list, set_list)

    def set_bad(self, val): self._bad = val
    def get_bad(self): return self._bad
    bad = property(get_bad, set_bad)

    def set_color(self, val): self._color = val
    def get_color(self): return self._color
    color = property(get_color, set_color)

    def set_mod(self, val): self._mod = val
    def get_mod(self): return self._mod
    mod = property(get_mod, set_mod)

    def set_size(self, val): self._size = val
    def get_size(self): return self._size
    size = property(get_size, set_size)
    
    def set_range(self, tup): self._range = tup
    def get_range(self): return self._range
    range = property(get_range, set_range)

    def set_step(self, tup): self._step = tup
    def get_step(self): return self._step
    step = property(get_step, set_step)

    def set_labels(self, tup): self._labels = tup
    def get_labels(self): return self._labels
    labels = property(get_labels, set_labels)

    def get_mean(self, lst):
        if not len(lst): mean = 0 # We're blank, throw up a placeholder chart
        else:
            #########################################
            # Calculate the average azimuth
            rads = [radians(i) for i in lst] #Convert to radians
            # Convenience functions
            ave = lambda x: sum(x)/len(x)
            rotate = lambda x: x+(2*pi) if x<0 else x # bring back to positive angle values
    
            sa = ave([sin(i) for i in rads])
            ca = ave([cos(i) for i in rads])
            # Take the arctan of this, using atan2 to preserve the quadrant information
            # We divide this (in degrees) by ten because there are only 36 values
            # around our rose diagram
            mean = degrees(rotate(atan2(sa,ca)))
            ########################################
        return mean
        
    def generate(self):
        lst = [i for i in filter(lambda x: x != self._bad, self._lst)]
        if not len(lst): raise Exception("No data")
        bins = {0:0} # Initialize with a zero value at due north
        ####################################################
        # Separate values into bins of 10 degree increments. The values
        # Are the number of azimuth readings within each 10 degree increment
        # where 10 degrees includes all readings in the range (5,15], 20
        # degrees includes all readings in the range (15,25], and 0 degrees
        # includes all readings in the range (355,5].
        a = 0
        bot, top = [int(i) for i in self._range]
        st = self._step/2
        step = self._step
        for b in range(st,top,step):
            rng = lambda x: (x >= a) and (x < b)
            bins[b+st] = len([i for i in filter(rng, lst)])
            a = b
        ############################################
        # Move values at 360 to zero and copy the full set of values
        # to 360. This is so that we can have a full circle of data
        # rather than having the data end at 355.
        
        try:
            bins[bot] += bins[top]
            bins[top] = bins[bot]
        except KeyError:
            pass
        ############################################
        # Grab the highest value so that we can have a max and
        # percentages of the max for the histogram bar heights
        # and set up some convenience variables for use in the
        # loops
        highest = max(bins.values())
        vals = [] # String of values for use in the URL
        # The outer loop looks only at values at increments
        # of ten. This is a variable to help build the inner
        # loop (values 1-9)
        a = 0 
        ############################################
        # Go through all of our values at ten degree increments
        # if the degrees are 5 (25, 255, etc) then we set the
        # value equal to 'A' (i.e. zero). Otherwise, set all the
        # values from 6-9 and 0-4 to whatever percentage we have.
        # This ends up creating a zero point at 5, values at some
        # magnitude centered on a ten degree increment, and then
        # another zero point at 15. The result is something that
        # visually resembles a bar extending from zero
        ###
        # NOTE: We have so many points only because we want a single
        # zero point at each 5, 15, 25... degree interval in order
        # to make the bars. Because of that, and because we want a
        # flat bar top, we have have to have values at 1 degree increments
        # so we fill it up with data. It makes a long URL, but I'll
        # accept that until Google gets a more functional API
        for i in range(st,top,step):
            num = bins[i+st]
            try:
                key = int((bins[i+st]/highest) * (len(self.coding)-1))
                val = self.coding[key]
            except ZeroDivisionError:
                val = 'A'
            for j in range(a,i):
                if (j%step == st):
                    vals.append('A')
                else:
                    vals.append(val)
            a = i

        # Copy the first 5 values to the end of the dataset to complete
        # the circle (otherwise, 355-360 is blank)
        vals += vals[:int(st)]
        # There's a slight gap between 359 and 0, so we add whatever
        # value is at 0 to fully close that circle. This north bar is
        # the hackiest bar of all, because the radar diagram WANTS to
        # go to 361 and higher.
        vals += vals[bot]
        ######################################################
        # Now we generate labels. We need as many labels as we have
        # datapoints, but most of them we fill with blank strings.
        # Here, we make N,S,E,W labels as well as labels at every
        # ten degrees.
        labels = [0]
        mx = int(top/len(self._labels))
        mod = 0
        for i in self._labels:
            labels.append(i)
            for j in range(1,mx):
                if not j%step:
                    v = j+mod
                    if self._mod:
                        v = int(v/ self._mod) 
                    labels.append(v)
                else: labels.append('')
            mod += mx
        ########################################
        # Create the pseudo-rose diagram using Google's Radar
        self.G = Radar([vals],encoding='simple')
        self.G.size(self._size,self._size)
        self.G.color(self._color)
        self.G.line(1,2,0)
        self.G.axes('x')
        self.G.axes.label(*labels)
        self.G.axes.range(0, *self._range)
#        self.G.marker('h','aaaaaa',0,1.0,2)
#        self.G.marker('h','aaaaaa',0,0.5,2)
#        self.G.marker('h','dddddd',0,0.25,1)
#        self.G.marker('h','dddddd',0,0.75,1)
#        self.G.marker('B','FF000080',1,0,5)
        try:
            self.G.marker('V','008000',0,self._mean,5)
        except:
            pass
    def URL(self):
        return self.G.url
    url = property(URL)
    
class Rose(RoseBase):
    def __init__(self):
        RoseBase.__init__(self)
        self.color = 'red'
        self.size = 300
        self.range = (0.0,360.0)
        self.step = 10

if __name__ == "__main__":
    # Generate a rose with a sample dataset.
    l =[111, 266, 169, 232, 128, 208, 196, 95, 230, 148, 182, 193, 161, 194, 147, 139, 201, 155, 177, 145, 152, 173, 163, 143, 196, 166, 183, 198, 215, 198, 172, 199, 208, 173, 188, 188, 140, 163, 150, 150, 144, 178, 168, 212, 195, 153, 178, 152, 213, 156, 196, 134, 122, 228, 218, 162, 219, 147, 170, 258, 332, 295, 332, 350, 315, 18, 26, 48, 22, 21, 0, 0, 1,1,1,1,4,10,10,9,9,9,9,9]
    #l = [1,2,3,3,3,3,4,4,10,10,10,10, 25,25, 30]
    r = Rose()
    r.list = l
    r.range = (0, 360)
    r.step = 10
    r.generate()
    print(r.url)

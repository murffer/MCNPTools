#! /usr/bin/python -W all
#
# Page numbers refer to MCNPX 2.7.0 manual

import sys, re, string
import os, os.path
from array import array
import copy
import xlwt

class Header:
    """mctal header container"""
    def __init__(self,data=None):
        """Header initialisation"""
        self.kod = 0            # name of the code, MCNPX
        self.ver = 0            # code version
        self.probid = []        # date and time when the problem was run
        self.knod = 0           # the dump number
        self.nps = 0            # number of histories that were run
        self.rnr = 0            # number of pseudorandom numbers that were used
        self.title = None       # problem identification line
        self.ntal = 0           # number of tallies
        self.ntals = []         # array of tally numbers
        self.npert = 0          # number of perturbations
        if data:
            self.parse(data)

    def parse(self,data):
        """ Parses the header data """
        for line in data.split('\n'):
            if self.kod == 0:
                self.kod, self.ver, probid_date, probid_time, self.knod, self.nps, self.rnr = line.split()
                self.probid.append(probid_date)
                self.probid.append(probid_time)
                continue
            else:
                if self.title is None and line[0] == " ":
                    self.title = line.strip()
                    continue

            words = line.split()

            if not self.ntal and words[0] == 'ntal':
                self.ntal = int(words[1])
                if len(words) == 4 and words[2] == 'npert':
                    self.npert = int(words[3])
                continue

            if self.ntal:
                for w in words:
                    self.ntals.append(int(w))

    def __str__(self):
        """Prints the class members"""
        s ="code:\t\t{}\n".format(self.kod)
        s+="version:\t{}\n".format(self.ver)
        s+="date and time:\t{}\n".format(self.probid)
        s+="dump number:\t{}\n".format(self.knod)
        s+="number of histories:\t{}\n".format(self.nps)
        s+="number of pseudorandom numbers used:\t{}\n".format(self.rnr)
        s+="title: {}\n".format(self.title)

        if self.ntal>1: 
            s +=str(self.ntal)+' tallies: '+str(self.ntals)+'\n'
        else: 
            s +=str(self.ntal)+' tally: '+str(self.ntals)+'\n'

        if self.npert != 0: s+="number of perturbations: {}\n".format(self.npert)

        return s

class Tally:
    def __init__(self,text=None):
        self.number = None
        self.title = ""
        self.particle = None
        self.type = None    
   
        self.axes = dict()
        self.axes['f'] = None
        self.axes['d'] = None
        self.axes['u'] = None
        self.axes['s'] = None
        self.axes['m'] = None
        self.axes['c'] = None
        self.axes['e'] = None
        self.axes['t'] = None

        self.data = []
        self.errors = []
        self.tfc_n =  None
        self.tfc_jtf = []
        self.tfc_data = []

        if text:
            self.parse(text)
    
    def __str__(self):
        return "tally #{}:\t{}\n".format(self.number, self.title)

    def __repr__(self):
        """Tally printer"""
        types = ['nondetector', 'point detector', 'ring', 'FIP', 'FIR', 'FIC']
        s="tally {}:\t{}\n".format(self.number, self.title)
        s+="\tparticles: ".join(self.GetParticleNames())+'\n'
        s+="\ttype: {} ({})\n".format(self.type, types[self.type])

        if self.axes['d'] == 1:
            s+='\tthis is a cell or surface tally unless there is CF or SF card\n'
        elif self.axes['d'] == 2:
            s+='\tthis is a detector tally (unless thre is an ND card on the F5 tally)\n'
        
        for ax in self.axes:
            s += '\t'+str(self.axes[ax])+''
        
        s += 'Also have data and errors fields\n'
        return s
   
    def parse(tally,data):
        """ Parsing the tally """
        is_vals = False          # True in the data/errors section
        is_list_of_particles = False # True if the line with the list of particles follows the ^tally line
        for line in data.split('\n'):
            if not line:
                break
            words = line.split()
            if words[0] == 'tally':
                tally.number = int(words[1])
                tally.particle = int(words[2])
                if tally.particle < 0: # then tally.particle is number of particle types and the next line lists them
                    is_list_of_particles = True
                tally.type = int(words[3])
                continue

            if is_list_of_particles:
                tally.particle = map(int, words)
                is_list_of_particles = False

            if tally.axes['f'] and tally.axes['d'] is None and line[0] == ' ':
                for w in words:
                    tally.axes['f'].arraycsn.append(str(w))

            if tally.axes['t'] and is_vals == False and len(tally.data) == 0 and line[0] == ' ':
                for w in words: tally.axes['t'].arraycsn.append(float(w))

            if tally.axes['c'] and tally.axes['e'] is None and line[0] == ' ':
                for w in words: tally.axes['c'].arraycsn.append(float(w))
            
            if tally.axes['e'] and tally.axes['t'] is None and line[0] == ' ':
                for w in words: tally.axes['e'].arraycsn.append(float(w))

            if tally.axes['u'] and tally.axes['s']is None and line[0] == ' ':
                for w in words: tally.axes['u'].arraycsn.append(float(w))

            if   not tally.axes['f'] and re.search('^f', line[0]):        tally.axes['f'] = Axis(words[0], map(int, words[1:]))
            elif not tally.axes['d'] and re.search('^d', line[0]):        tally.axes['d'] = Axis(words[0], map(int, words[1:]))
            elif not tally.axes['u'] and re.search("^u[tc]?", line[0:1]): tally.axes['u'] = Axis(words[0], map(int, words[1:]))
            elif not tally.axes['s'] and re.search('^s[tc]?', line[0:1]): tally.axes['s'] = Axis(words[0], map(int, words[1:]))
            elif not tally.axes['m'] and re.search('^m[tc]?', line[0:1]): tally.axes['m'] = Axis(words[0], map(int, words[1:]))
            elif not tally.axes['c'] and re.search("^c[tc]?", line[0:1]): tally.axes['c'] = Axis(words[0], map(int, words[1:]))
            elif not tally.axes['e'] and re.search("^e[tc]?", line[0:1]): tally.axes['e'] = Axis(words[0], map(int, words[1:]))
            elif not tally.axes['t'] and re.search("^t[tc]?", line[0:1]): tally.axes['t'] = Axis(words[0], map(int, words[1:]))
            elif line[0:2] == 'tfc':
                tally.tfc_n = words[1]
                tally.tfc_jtf = words[2:]

            if tally.tfc_n and line[0] == ' ':
                tally.tfc_data = words

            if words[0] == 'vals':
                is_vals = True
                continue

            if is_vals:
                if line[0] == ' ':
                    for iw, w in enumerate(words):
                        if not iw % 2: tally.data.append(float(w))
                        else: tally.errors.append(float(w))
                else:
                    is_vals = False
   

    def GetParticleNames(self):
        """Convert the array of 1 and 0 to the list of particles
        according to the Table 4-1 on page 4-10 (48) of the MCNP 2.7.0 Manual
        """
        # '!' stands for 'anti'
        names = ['neutron', '-neutron', 'photon', 'electron', 'positron',
             'mu-', '!mu-', 'tau-', 'nue', '!nue', 'num', 'nut',
             'proton', '!proton', 'lambda0', 'sigma+', 'sigma-', 'cascade0', 'cascade-', 'omega-', 'lambdac+', 'cascadec+', 'cascadec0', 'lambdab0',
             'pion+', 'pion-', 'pion0', 'kaon+', 'kaon-', 'K0short', 'K0long', 'D+', 'D0', 'Ds+', 'B+', 'B0', 'Bs0',
             'deuteron', 'triton', 'He3', 'He4', 'heavy ions']
        vals = []
        for i in range(len(self.particle)):
            if self.particle[i] == 1: vals.append(names[i])
            elif self.particle[i] != 0:
                print 'strange values (not 0 or 1) found in the list of particles:', a
        return vals
    
    def GetBins(self,binName):
        """ Returns the bins of binName """
        return self.axes[binName].GetBins()

    def getName(self):
        """
        Return the name of the tally
        """
        return "f%s" % self.number
    

class Axis:
    """Axis of a tally"""
    def __init__(self, name, numbers):
        """Axis Constructor"""
        self.name = name
        self.numbers = numbers # we keep all array numbers, but not the first one only (in the case of mesh tally there are > than 1 number)
        self.number = int(self.numbers[0]) # see page 320
        self.arraycsn = [] # array of cell or surface numbers (written for non-detector tallies only)
        
        # ni, nj and nk make sense for mesh tallies only (see e.g. tally 4 in figs/cold-neutron-map/2/case001/small-stat/mctal)
        # these are number of bins in i,j,k directions
        self.ni = None
        self.nj = None
        self.nk = None
        if len(self.numbers)>1:
            self.ni, self.nj, self.nk = self.numbers[2:]
            print self.ni, self.nj, self.nk
    
    def __str__(self):
        s = "Axis: "+self.name+' Number Bins: {}\n'.format(self.number)
        return s

    def GetBins(self):
        """ Returns the bins for the tally """
        return [float(i) for i in self.arraycsn]

    def Print(self):
        """Axis printer"""
        print "\t Axis %s" % self.name
        print "\t\tcsn %s" % self.arraycsn


class MCTAL:
    """mctal container"""
    good_tallies = [5] # list of 'good' tally types

    def __init__(self, fname='mctal'):
        """Constructor"""
        self.fname = fname      # mctal file name
        self.tallies = dict()   # list of tallies
        self.header = None      # Header
        self.read()
    
    def __repr__(self):
        """ String  """
        s = 'Filename: {}\n'.format(str(self.fname))
        s += str(self.header)
        for t in self.tallies:
            s += str(self.tallies[t])
        return s

    def read(self):
        """method to parse the mctal file"""

        probid_date = None       # date from probid
        probid_time = None       # time from probid
        tally = None             # current tally
        self.header = Header()

        lines = open(self.fname).read()
        data = lines.split('tally')
        
        # Header
        self.header = Header(data[0])
        for i in range(1,len(data)):
            self.tallies[self.header.ntals[i-1]] = Tally('tally'+data[i])

    def GetTally(self,tallyNum):
        """ Writes the tallyNum to worksheet ws"""
        # Checking Arguments
        if not tallyNum in self.tallies.keys():
            print 'ERROR: Tally '+str(tallyNum)+' is not a valid tally number.'
            print '\tValid tally numbers are: '+str(self.tallies.keys())
        else:
            return self.tallies[tallyNum]

    def WriteTally(self,tallyNum,ws):
        """ Writes the tallyNum to worksheet ws"""
        tally = self.GetTally(tallyNum)
        row = 0
        col = 0
        val = 0
        for f in tally.axes['f'].GetBins():
            for c in tally.axes['c'].GetBins():
                # Printing the header
                longName = 'f'+str(f) + ' c'+str(c)
                ws.write(0,col,longName)     # Long Name
                ws.write(1,col,"MeV")        # Energy
                ws.write(2,col,str(f))       # Comments
                row = 3
                
                for e in tally.axes['e'].GetBins():
                    ws.write(row,col,e)                                                   # Energy
                    ws.write(row,col+1,float(tally.data[val]))                            # Value
                    ws.write(row,col+2,float(tally.data[val])*float(tally.errors[val]))   # absolute error
                    val += 1
                    row += 1
                
                # Adding the total bin
                ws.write(row,col,'total')
                ws.write(row,col+1,float(tally.data[val]))                            # Value
                ws.write(row,col+2,float(tally.data[val])*float(tally.errors[val]))   # absolute error
                val += 1

                # Incrementing col
                col += 3

    def ConvertToXLS(self,filename='mctal.xls'):
        """ Converts MCTAL file to an xls file of filename"""
        wb = xlwt.Workbook() 
        for t in self.tallies:
            self.WriteTally(t,wb.add_sheet(str(t)))
        wb.save(filename)

if __name__ == "__main__":
    # Loops through the directory, converting all of the mctal files to xls
    for f in os.listdir('.'):
        if f.endswith('.m'):
            fnew = f.strip('.m')
            m = MCTAL(f)
            m.ConvertToXLS(fnew+'.xls')
    print 'Converted all mctal files to xls'

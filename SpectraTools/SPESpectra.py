class SPESpectra(object):


    def parseField(self,fieldname,token):
        """ parses text for a given field name
            fieldname - the name of the field
            token     - paresed fieldname token    
        """
        content = token.splitlines()
        field = ''
        for c in content:
            if not c.lower().startswith(fieldname):
                field += c
        return field
        
    def __init__(self,filename):
        """ File format from ORTEC Manual 
        
        Attributes:
          filename    - filename of the spectra
          spec_id     - one line of text describing the data
          spec_rem    - any number of lines containing remarks about data
          date_mea    - measurement date in the form mm/dd/yyyy hh:mm:ss
          meas_tim    - live time and realtime of the spectrum 
          data        - channel number and corresponding data
          roi         - regions of intrest
          energ_fit   - energy calibration (a+b*chn)
          mca_cal     - energy calibration along with mca calibration
          shape_cal   - FWHM calibration factors
        """
        self.filename = filename
        with open(filename,'r') as f:
            data = f.read()
        tokens = data.split('$')
        for t in tokens:
            # Ignorning strings that don't contain characters
            if not t.strip():
                continue
            # Getting the corresponding field
            field = t.splitlines()[0].lower()
            
            # Filling the fields
            if field.startswith('spec_id'):
                self.spec_id = self.parseField('spec_id',t)
            elif field.startswith('spec_rem'):
                self.spec_rem = self.parseField('spec_rem',t)
            elif field.startswith('date_mea'):
                date = self.parseField('date_mea',t)
                self.date_mea = date
            elif field.startswith('meas_tim'):
                data = self.parseField('meas_tim',t)
                times = data.split()
                self.meas_tim = {'Live time (s)':float(times[0]),'Real Time (s)':float(times[1])}
            elif field.startswith('data'):
                lines = t.splitlines()
                channels = [int(i) for i in lines[1].split()]
                channels = range(channels[0],channels[1])
                data = [int(i) for i in lines[2:-1]]
                self.data = {'channels':channels,'data':data}
            elif field.startswith('roi'):
                pass
            elif field.startswith('presets'):
                pass
            elif field.startswith('ener_fit'):
                pass
            elif field.startswith('mca_cal'):
                pass
            elif field.startswith('shape_cal'):
                pass
            else:   
                print 'Unkown field: '+field
                
    def __str__(self):
        attrs = vars(self)
        return ''.join("%s\n" for a in attrs)
    
    def __repr__(self):
        attrs =  vars(self)
        return ''.join("%s: %s\n" % item for item in attrs.items())
""" 
Debugging Main
"""         
if __name__ == '__main__':
    s = SPESpectra('Test.Spe')
    print s



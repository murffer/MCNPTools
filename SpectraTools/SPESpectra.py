class SPESpectra:
  """ ASCII SPE Spectrum File """

  def __init__(self,filename):
    """ File format from ORTEC Manual 
    
    Attributes:
      filename    - filename of the spectra
      spec_id     - one line of text describing the data
      spec_rem    - any number of lines containing remarks about the data
      date_meas   - measurement date in the form mm/dd/yyyy hh:mm:ss
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
      # Getting the SPEC_ID
      if t.lower.startswith('spec_id'):
        content = t.splitlines()
        for c in content:
          if not c in t.lower.starts('spec_id'):
            self.spec_id += c
      elif t.lower.startswith('spec_rem'):



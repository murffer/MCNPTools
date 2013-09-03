class SPESpectra:
  """ ASCII SPE Spectrum File """

  def __init__(self,filename):
    """ File format from ORTEC Manual 
    
    Attributes:
      
    """
    
    self.filename = filename
    self.spec_id = ''         # One line of text describing the data


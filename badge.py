class Badge:
    def __init__(self, number='', name=''):
    
        if number != '':
          self.scanned = True
        else:
          self.scanned = False
          
        self.number = number
        self.name = name
        
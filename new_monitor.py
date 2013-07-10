import csv
import numpy as np
import psychopy.monitors.calibTools as T
from matplotlib.mlab import csv2rec

# Constructs and saves a new monitor to the given pathname based on the
# given photometer data. Photo data file should be in tab delimited form:
# "input level", "grayscale lum", "red gun lum", green gun lum", "blue gun lum"

# Note: When you want to access a monitor saved into a custom path, must
# change the monitorFolder variable inside of the calibTools module, then 
# get the monitor using <module>.Monitor(monitorName)

# Set runtime parameters for monitor:
path = './calibration/'     # where monitors will be stored
# Make sure to change monitorFolder in this module for custom save location
T.monitorFolder = path

class Monitor(object):
    def __init__(self,attr_dict):
        """

        Initialize the monitor based on attributes read from a dict and
        calibration file
        
        """ 
        for k in attr_dict.keys():
            self.__setattr__(k, attr_dict[k])

        r = csv2rec('%s%s'%(path, self.calib_file))
        self.calib = {} 
        for d in r.dtype.fields:
            self.calib[d] = r[d]
        print self.calib.keys()
        
    def calculate_gamma(self):
        """
        
        """

        # Initialize a list to operate on. Set the first line ('RGB' to
        # nans. This shouldn't concern you too much, because psychopy.visual
        # throws that away anyway. See line 225 in visual.py):
        gammaGrid = [[np.nan, np.nan, np.nan]]

        for val in ['r','g','b']:
            calculator = T.GammaCalculator(inputs=self.calib['input'],
                                           lums=self.calib[val])
            
            gammaGrid.append([calculator.a, calculator.b, calculator.gamma])
            
        return np.array(gammaGrid)
        
    def save_gamma(self):
        
        """
        
        """

        # Create the new monitor, set values and save
        newMon = T.Monitor(self.monitor_name,
                           self.width,
                           self.distance)
        
        newMon.setSizePix(self.size)
        newMon.setNotes(self.notes)
        newMon.setGammaGrid(self.calculate_gamma())
        if 'calib_date' in self.__dict__.keys(): 
            newMon.setCalibDate(self.calib_date)
        newMon.saveMon()

if __name__=="__main__":

    monitors_file = 'monitors'
    monitors = __import__(monitors_file)
    for mon_dict in monitors.monitors:
        m = Monitor(mon_dict)
        m.save_gamma()

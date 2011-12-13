"""
Hold information about different monitors. Use the dict format outlined below. 

""" 
monitors = [dict(monitor_name = 'cni_lcd', # name of the new monitor
                 calib_file = 'cni_lums_20110718.csv', # photometer data calculated
                 # from Franco's calibration data.
                 calib_date = '20110718', # Date of calibration
                 width = 25.5, # width of the screen in cm
                 distance = 190, # viewing distance from the screen in cm
                 size = [2560, 1600], # size of the screen in pixels
                 notes = """
                 Parameters taken from the CNI wiki:
                 http://cni.stanford.edu/wiki/MR_Hardware#Flat_Panel. Accessed on 8/9/2011
                 """
                 ),
            dict(monitor_name = 'testMonitor', # name of the new monitor
                 calib_file = 'dummy_calib.csv', # dummy photometer data
                 width = 32, # approximate width of the screen in cm
                 distance = 100, # distance from the screen in cm
                 size = [800, 500], # size of the screen in pixels
                 notes = """ Rough estimate of parameters on a laptop.
                 just for testing"""
                 ),
            dict(monitor_name='hp_lp2475w',
                 calib_file= 'cni_lums_20110718.csv',
                 calib_date= '20110718',
                 width=25.5,
                 distance=50,
                 size = [1920, 1200],
                 notes = """
                 This is my desktop monitor in 482 Jordan Hall, but with the
                 gamma calibration from Franco's measurements of the CNI LCD.
                 """ 
                 ),
            
            dict(monitor_name = 'ESI_psychophys', # name of the new monitor
                 calib_file = 'caliESI_psychophys10262011.csv', # dummy photometer data
                 width = 47, # approximate width of the screen in cm
                 distance = 57, # distance from the screen in cm
                 size = [1680, 1050], # size of the screen in pixels
                 notes = """
                 This is the psychophysics CRT used at the ESI Frankfurt
                 """
                 )
                 ]

import os
import time

import numpy as np
try:
    import wx
    has_wx = True
except:
    has_wx = False
    pass

try:
    from psychopy import core, visual, event, gui
    has_psychopy = True
except:
    has_psychopy = False
    
import matplotlib
from matplotlib.mlab import window_hanning,csv2rec
import matplotlib.pyplot as plt
from scipy.optimize import leastsq
from scipy.special import erf

#User input GUI:
if has_wx:
    class GetFromGui(wx.Dialog):
        """ Allows user to set input parameters of ss through a simple GUI"""    
        def __init__(self, parent, id, title):
            wx.Dialog.__init__(self, parent, id, title, size=(280,280))
            # Add text label
            wx.StaticText(self, -1, 'Subject ID:', pos=(10,20))
            # Add the subj id text box:
            self.textbox1 = wx.TextCtrl(self, -1, pos=(100, 18), size=(150, -1))

            # Add text label
            wx.StaticText(self, -1, 'Center ori:', pos=(10, 50))
            # Add the text box for the center orientation:
            self.textbox2 = wx.TextCtrl(self, -1, pos=(100, 48), size=(150, -1))

            # Add text label
            wx.StaticText(self, -1, 'Surr ori:', pos=(10, 80))
            # Add the text box for the surround orientation:
            self.textbox3 = wx.TextCtrl(self, -1, pos=(100, 78), size=(150, -1))

            wx.StaticText(self, -1, "Surround with target", pos=(10,110))
            self.textbox4 = wx.TextCtrl(self, -1, pos=(150, 108), size=(100, -1))

            wx.StaticText(self, -1, "Audio feedback", pos=(10,140))
            self.textbox5 = wx.TextCtrl(self, -1, pos=(150, 138), size=(100, -1))

            wx.StaticText(self, -1, "Neutral Cue?", pos=(10,170))
            self.textbox6 = wx.TextCtrl(self, -1, pos=(150, 168), size=(100, -1))

            # Add OK/Cancel buttons
            wx.Button(self, 1, 'Done', (60, 210))
            wx.Button(self, 2, 'Quit', (150, 210))

            # Bind button press events to class methods for execution
            self.Bind(wx.EVT_BUTTON, self.OnDone, id=1)
            self.Bind(wx.EVT_BUTTON, self.OnClose, id=2)
            self.Centre()
            self.ShowModal()        

        # If "Done" is pressed, set important values and close the window
        def OnDone(self,event):

            self.success = True
            self.subject = self.textbox1.GetValue()
            center_ori = self.textbox2.GetValue()
            surr_ori = self.textbox3.GetValue()
            swt = self.textbox4.GetValue()
            audio = self.textbox5.GetValue()
            cue_reliability = self.textbox6.GetValue()

            if center_ori:
                  self.center_ori = center_ori
            else:
                  self.center_ori = 0

            if surr_ori:
                self.surr_ori = surr_ori
            else:
                self.surr_ori = 0

            if swt:
                self.swt = True
            else:
                self.swt = False

            if audio:
                self.audio = True
            else:
                self.audio = False

            if cue_reliability:
                self.cue_reliability = False
            else:
                self.cue_reliability = 0.7

            self.Close()

        # If "Quit" is pressed" , toggle failure and close the window
        def OnClose(self, event):
            self.success = False
            self.Close()


class Params(object):
    """
    The Params class stores all of the parameters needed during the execution
    of ss_run.

    Once a parameter is set, it is protected and cannot be changed, unless it
    is explicitely removed from the _dont_touch variable. 

    Some parameters are set upon initialization from the file 'ss_params.py'

    Others are set through a gui which is generated by the method set_by_gui
    
    """
    def __init__(self, p_file='params'):
        """
        Initializer for the params object.

        Parameters
        ----------

        p_file: string, the name of a parameter file, defaults to 'ss_params'

        """
        self._dont_touch = []
        #The following params are read in from a file with dict p.
        im = __import__(p_file)
        for k in im.p.keys():
            self.__setattr__(k,im.p[k])
            self._dont_touch.append(k)

    def __setattr__(self,name,value):
        """
        
        Overloading __setattr__, such that attributes cant be changed once they
        are set, unless they are explicitely removed from the _dont_touch list.

        """

        if name == '_dont_touch':
            super.__setattr__(self,name,value) 
        elif name in self._dont_touch:
            raise ValueError("Parameter %s is protected, please don't touch!"%name)
        else:
            super.__setattr__(self,name,value)
            self._dont_touch.append(name)

    def set_by_gui(self):
        """
        Set additional parameters through a wx GUI object. The wx app needs to
        be started and set in the main loop
        
        """

        # Use the GetFromGui class (below):
        user_choice = GetFromGui(None, -1, 'Params')
        # success is achieved if the user presses 'done': 
        if user_choice.success:                
                user_params = {
                    "subject" : user_choice.subject,
                    "center_ori" : user_choice.center_ori,
                    "surr_ori" : user_choice.surr_ori,
                    "surround_w_target": user_choice.swt,
                    "audio_feedback": user_choice.audio,
                    "cue_reliability":user_choice.cue_reliability,
                    }
        else:
            user_choice.Destroy()
            raise ValueError("Program stopped by user")
        # Stop execution of the window
        user_choice.Destroy()
        
        for k in user_params.keys():
            self.__setattr__(k,user_params[k])

    def save(self,f,open_and_close=False):
        """

        This saves the parameters to a text file.

        Takes as an input an already opened file object and returns it in the
        end. Does not open or close the file, unless the variable
        open_and_close is set to True, in which case, the input should be a
        file-name, not a file object

        f is returned either way
        """

        if open_and_close:
            f = file(file_name,'w')
            for k in self.__dict__.keys():
                if k[0]!='_': #Exclude 'private' variables ('_dont_touch')
                    f.write('# %s : %s \n'%(k,self.__dict__[k]))
            f.close()

        else:
            for k in self.__dict__.keys():
                if k[0]!='_': #Exclude 'private' variables ('_dont_touch')
                    f.write('# %s : %s \n'%(k,self.__dict__[k]))
        return f
    
def sound_freq_sweep(startFreq, endFreq, duration, samples_per_sec=None):
    """   
    Creates a normalized sound vector (duration seconds long) where the
    frequency sweeps from startFreq to endFreq (on a log2 scale).

    Parameters
    ----------

    startFreq: float, the starting frequency of the sweep in Hz
    
    endFreq: float, the ending frequency of the sweep in Hz

    duration: float, the duration of the sweep in seconds

    samples_per_sec: float, the sampling rate, defaults to 44100 


    """
    from psychopy.sound import Sound as Sound

    if samples_per_sec is None:
        samples_per_sec = 44100

    time = np.arange(0,duration*samples_per_sec)

    if startFreq != endFreq:
        startFreq = np.log2(startFreq)
        endFreq = np.log2(endFreq)
        freq = 2**np.arange(startFreq,endFreq,(endFreq-startFreq)/(len(time)))
        freq = freq[:time.shape[0]]
    else:
        freq = startFreq
    
    snd = np.sin(time*freq*(2*np.pi)/samples_per_sec)

    # window the sound vector with a 50 ms raised cosine
    numAtten = np.round(samples_per_sec*.05);
    # don't window if requested sound is too short
    if len(snd) >= numAtten:
        snd[:numAtten/2] *= window_hanning(np.ones(numAtten))[:numAtten/2]
        snd[-(numAtten/2):] *= window_hanning(np.ones(numAtten))[-(numAtten/2):]

    # normalize
    snd = snd/np.max(np.abs(snd))

    return snd

def compound_sound(freqs, duration, samples_per_sec=None):
    """
    Generate a sound made out of several frequencies

    Parameters
    ---------
    freqs: list
        A list of frequencies to be included in the 
    
    """
    if samples_per_sec is None:
        samples_per_sec = 44100

    time = np.arange(0,duration*samples_per_sec)
    snd = np.zeros_like(time)
    
    for f in freqs:
        snd =  snd + np.sin(time*f*(2*np.pi)/samples_per_sec)

    # window the sound vector with a 50 ms raised cosine
    numAtten = np.round(samples_per_sec*.05);
    # don't window if requested sound is too short
    if len(snd) >= numAtten:
        snd[:numAtten/2] *= window_hanning(np.ones(numAtten))[:numAtten/2]
        snd[-(numAtten/2):] *= window_hanning(np.ones(numAtten))[-(numAtten/2):]

    # normalize
    snd = snd/np.max(np.abs(snd))

    return snd
    
def start_data_file(subject_id):

    """Start a file object into which you will write the data, while making
    sure not to over-write previously existing files """
    
    #Check the data_file:
    
    list_data_dir = os.listdir('./data')

    i=1
    this_data_file = '%s_%s_%s_att_ss.csv'%(subject_id,
                                                time.strftime('%m%d%Y'),i)

    #This makes sure that you don't over-write previous data:
    while this_data_file in list_data_dir:
        i += 1
        this_data_file='%s_%s_%s_att_ss.csv'%(subject_id,
                                                  time.strftime('%m%d%Y'),i)
        
    #Open the file for writing into:
    f = file('./data/%s'%this_data_file,'w')

    #Write some header information
    f.write('# Time : %s#\n'%(time.asctime()))

    return f

def save_data(f,*arg):

    for a in arg[0:-1]:
        f.write('%s,'%a)

    #Don't put a comma after the last one:
    f.write('%s \n'%arg[-1])
    
    return f

class Text(object):

    """
    A class for showing text on the screen until a key is pressed 
    """

    def __init__ (self,win,text='Press a key to continue',**kwargs):
        """
        
        Will do the default thing(show 'text' in white on gray background),
        unless you pass in kwargs, which will just go through to
        visual.TextStim (see docstring of that class for more details)

        keys: list. The keys to which you listen for input
        """

        self.win = win
        
        self.text = visual.TextStim(win,text=text,**kwargs)
        
    
    def __call__(self,duration=np.inf):
        """
        Text is shown to the screen, until a key is pressed or until duration
        elapses (default = inf)
        
        """

        clock = core.Clock()
        t=0
        while t<duration: #Keep going for the duration
            t=clock.getTime()

            self.text.draw()
            self.win.flip()

            for key in event.getKeys():
                if key:
                    return

def get_data(file_name):
    file_read = file(file_name,'r')
    l = file_read.readline()
    p = {} #This will hold the params
    l = file_read.readline()
    data_rec = []
    
    if l=='':
        return p,l,data_rec

    while l[0]=='#':
        try:
            p[l[1:l.find(':')-1]]=float(l[l.find(':')+1:l.find('\n')]) 

        #Not all the parameters can be cast as float (the task and the
        #subject): 
        except:
            p[l[2:l.find(':')-1]]=l[l.find(':')+1:l.find('\n')]

        l = file_read.readline()

    try:
        data_rec = csv2rec(file_name)
    except ValueError:
        p = []
    
    return p,l,data_rec



class Staircase(object):
    """
    This is an object for holding, updating and potentially analyzing
    A psychophysical staircase

    """ 
    def __init__(self,start,step,n_up=3,n_down=1,harder=-1,ub=1,lb=0):
        """
        Initialization function for the staircase class

        Parameters
        ----------
        start: The starting value of the staircase
        step: The size of the step used when updating the staircase
        n_up,n_down: The kind of staircase to be used, defaults to a 3-up,
                     1-down staircase 

        harder: {-1,1} The direction which would make the task harder. Defaults
        to -1, which is true for a contrast detection task.

        ub: float, the upper bound on possible values in the staircase
        lb: float, the lower bound on possible values in the staircase
        
        """
        
        self.value = start
        self.n_up = n_up
        self.step = step
        self.n = 0 #This is what will be compared to n_up for udpating.
        self.harder = np.sign(harder) #Make sure that this is only -1 or 1.
        self.record = [start]
        self.correct = []
        self.ub = ub
        self.lb = lb
        
    def update(self,correct):
        """

        This function updates the staircase value, according to the state of
        the staircase, the n/n_up values and whether or not the subject got it
        right. This staircase is then propagated on to the next trial.

        Parameters
        ----------
        correct: {True|False|None => don't update, but record the value} 

        """
        self.correct.append(correct)

        #If none is the input, don't change anything (not even n!) and record
        #the value in this trial:
        if correct is not None:
            if correct:
                if self.n>=self.n_up-1:
                    self.value += self.harder * self.step #'harder' sets the
                                                          #sign of the change
                                                          #to make it harder
                    self.n = 0
                else:
                    self.n +=1

            else:
                self.n = 0
                self.value -= self.harder * self.step #Change in the
                                            #opposite direction than above to
                                            #make it easier!
            #Make sure that the staircase doesn't     
            if self.value > self.ub:
                self.value = self.ub
            if self.value < self.lb:
                self.value = self.lb
            
        #Add to the records the updated value (even on trials where
        #correct=None):
        self.record.append(self.value)
        
    def analyze(self,guess=0.5,flake=0.01,slope=3.5,fig_name=None,
                bootstrap_n=1000):
        """
        Perform a psychometric curve analysis of the data in the staircase and
        save a figure, if needed.

        Parameters
        ----------

        guess: The expected hit rate when the subject is blind-folded (default:
        0.5)

        flake: The expected rate of misses on trials on which the subjects
        should actually succeed, if they are really doing the task (default: 0.1)

        slope: The slope of the psychometric curve at the inflection point
        (default to 3.5)

        fig_name: string
           A file name for saving a figure. If none provided, don't save the
           generated figure

        bootstrap_n: int
           The number of boot samples to take for the bootstrapping analysis
           
        Note
        ----

        The fitting procedure is applied to the slope, as well as to the
        threshold.
        
        """
        def weibull(x,threshx,slope,guess,flake,threshy=None):
                if threshy is None:
                    threshy = 1-(1-guess)*np.exp(-1)

                k = (-np.log( (1-threshy)/(1-guess) ))**(1/slope)
                weib = flake - (flake-guess)*np.exp(-(k*x/threshx)**slope)
                return weib 

        def get_thresh(amp,c):
            """Calculate a threshold given amp, c(orrect) values  """ 
            #Helper functions for fitting the psychometric curve, need to be
            #defined within the local scope, so that they can grok the data:
            
            def weib_fit(pars):
                thresh,slope = pars
                return weibull(x,thresh,slope,guess,flake)

            def err_func(pars):
                return y-weib_fit(pars)

            #Throw away the None's:
            hit_amps = amp[c==1]
            miss_amps = amp[c==0]

            # Get rid of floating point error:
            hit_amps = defloaterrorize(hit_amps)
            miss_amps = defloaterrorize(miss_amps)

            all_amps = np.hstack([hit_amps,miss_amps])
            stim_intensities = np.unique(all_amps)

            n_correct = [len(np.where(hit_amps==i)[0]) for i in stim_intensities]
            n_trials = [len(np.where(all_amps==i)[0]) for i in stim_intensities]
            Data = zip(stim_intensities,n_correct,n_trials)
            x = []
            y = []
            n = []
            for idx,this in enumerate(Data):
                #Take only cases where there were at least n_up observations:
                if n_trials[idx]>=self.n_up:
                    #Contrast values: 
                    x = np.hstack([x,this[2] * [this[0]]])
                    #% correct:
                    y = np.hstack([y,this[2] * [this[1]/float(this[2])]])

            initial = np.mean(x),slope
            this_fit , msg = leastsq(err_func,initial)
            return this_fit,x,y
        
        #Convert the flake into the expected format for the weibull function:
        flake = 1-flake
        amp = np.array(self.record[:-1]) #The last one will be the next trials
                                        #amp 
        c = np.array(self.correct) #Which is why correct is one item shorter
        
        this_fit,keep_x,keep_y = get_thresh(amp,c)
        #print keep_x
        #print keep_y
        
        bootstrap_th = []
        bootstrap_slope = []
        keep_amp = amp
        keep_c = c
        keep_slope = this_fit[1]
        keep_th = this_fit[0]
        for b in xrange(bootstrap_n):
            b_idx = np.random.randint(0,c.shape[0],c.shape[0])
            amp = keep_amp[b_idx]
            c = keep_c[b_idx]
            this_fit,x,y = get_thresh(amp,c)
            bootstrap_th.append(this_fit[0])

        upper = np.sort(bootstrap_th)[bootstrap_n*0.84]
        lower = np.sort(bootstrap_th)[bootstrap_n*0.16]

        #Make a figure, if required:
        if fig_name is not None: 
            fig = plt.figure()
            ax = fig.add_subplot(1,1,1)
            for idx,this_x in enumerate(keep_x):
                n = np.sum(keep_x==this_x)  # How many trials, sets the markersize
                ax.plot(this_x,keep_y[idx],'o',color = 'b',markersize = n)

            x_for_plot = np.linspace(np.min(keep_x)-0.05,np.max(keep_x)+0.05,100)
            ax.plot(x_for_plot,weibull(x_for_plot,keep_th,
                                       keep_slope,
                                       guess,
                                       flake),
                    color = 'g')
            ax.set_title('Threshold=%1.2f +/- %1.2f ::Slope=%1.2f'
                         %(keep_th,(upper-lower)/2,keep_slope))
            fig.savefig(fig_name)

        return keep_th,lower,upper

# Helper function in order to get rid of small round-off error in the
# representation of trial contrasts in the staircase object:
def defloaterrorize(a):
    # Turn into units of % contrast: 
    a *= 100
    # Truncate anything smaller than 1% contrast:
    a = a.astype(int)
    # Recover the original units (0-1):
    a = a/100.0
    return a

def get_data(file_name=None):
    """
    Get the data from file, returning parameters, the line with variable names
    and a data_rec using these variable names.

    """

    if file_name is None: 
        path_to_files = './data/'
        file_name =  str(gui.fileOpenDlg(path_to_files)[0])
    
    file_read = file(file_name,'r')
    l = file_read.readline()
    p = {} #This will hold the params
    l = file_read.readline()
    data_rec = []
    
    if l=='':
        return p,l,data_rec

    while l[0]=='#':
        try:
            p[l[1:l.find(':')-1]]=float(l[l.find(':')+1:l.find('\n')]) 
        except:
            p[l[2:l.find(':')-1]]=l[l.find(':')+1:l.find('\n')]
        l = file_read.readline()
        
    try:
        data_rec = csv2rec(file_name)
    except ValueError:
        p = []
    
    return p,l,data_rec

def analyze_constant(data_file=None, fig_name=None, cue_cond='cued',
                     fitfunc='cumgauss',boot=1000):
    """
    This analyzes data from the constant stimuli experiment
    """
    
    def cumgauss(x, mu,sigma):
        """
        The cumulative Gaussian at x, for the distribution with mean mu and
        standard deviation sigma.

        Based on: http://en.wikipedia.org/wiki/Normal_distribution#Cumulative_distribution_function
        """
        return 0.5 * (1 + erf((x-mu)/(np.sqrt(2)*sigma)))

    def fit_th(x, ans, ask, initial):
        """
        The core of the fitting. Get x values and get the responses (between 0
        and 1). Then, fit the function according to these values
        """
        # Define the fit/error functions in the scope of the wrapper function:
        def cumgauss_fit(params):
            """
            fit func
            """
            mu,sigma = params
            return cumgauss(x, mu, sigma)

        def err_func(params):
            """
            Error function
            """
            return y-cumgauss_fit(params)
        
        # Generate the y axis:
        y = []
        for i in range(len(ans)):
            y.append(np.mean(ans[ask==ask[i]]))

        this_fit, msg = leastsq(err_func, initial)

        return x, y, this_fit

    p,l,data_rec = get_data(data_file)
        
    if cue_cond == 'cued':
        cue_cond_idx = np.where(data_rec['cue_side']==data_rec['ask_side'])[0]
    elif cue_cond == 'other':
        cue_cond_idx = np.where(data_rec['cue_side']!=data_rec['ask_side'])[0]

    center_contrasts = [float(t) for t in
    p['center_contrast'].split('[')[1].split(']')[0].split(' ')[1::2]]
    
    base_contrast = []
    for i,ask_side in enumerate(data_rec['ask_side'][cue_cond_idx]):
        base_contrast.append(data_rec[ask_side + '_contrast2'][cue_cond_idx][i])

    if fig_name is not None: 
        # Get the color cycle from the mpl rc params:
        rc = matplotlib.rc_params()
        colors = rc['axes.color_cycle'][:len(center_contrasts)]
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)

    fits = []
    keep_x = []
    keep_y = []

    boot_th_ub = []
    boot_sl_ub = []
    boot_th_lb = []
    boot_sl_lb = []

    min_x=1
    max_x=0
    for contrast in center_contrasts:
        c_idx = np.where(np.abs(np.array(base_contrast)-contrast)<0.01)[0]
        this_ask = data_rec['ask_contrast'][cue_cond_idx][c_idx]
        # Move it into the interval [0,1] with the right directionality: when
        # the value of this_ask was high, the chances were higher for a '1'
        # answer than for a '2' answer (that's the "1 - " at the beginning of
        # next line):
        this_ans = 1 - (data_rec['answer'][cue_cond_idx][c_idx] - 1) 
        x = np.array(contrast) + this_ask

        # Begin by guessing that the mean is the same as the contrast shown
        # (no bias):
        initial = contrast, 1
        x,y,this_fit = fit_th(x,this_ans,this_ask,initial)
        
        # Store stuff for plotting:
        fits.append(this_fit)
        keep_x.append(x)
        keep_y.append(y)

        min_x = min([min_x, np.min(x)])
        max_x = max([max_x, np.max(x)])
        boot_th = []
        boot_sl = []
        # Bootstrap estimate the parameters
        for b in range(boot):
            # Choose this boot sample
            idx = np.random.randint(0, len(x), len(x))
            boot_x = x[idx]
            boot_ans = this_ans[idx]
            boot_ask = this_ask[idx]
            # Use the same initial value guess as above:
            this_x, this_y, boot_fit = fit_th(boot_x, boot_ans, boot_ask,initial)
            boot_th.append(boot_fit[0])
            boot_sl.append(boot_fit[1])
            
        sort_th = np.sort(boot_th)
        sort_sl = np.sort(boot_sl)

        boot_th_ub.append(sort_th[0.84*boot])
        boot_th_lb.append(sort_th[0.16*boot])
        boot_sl_ub.append(sort_sl[0.84*boot])
        boot_sl_lb.append(sort_sl[0.16*boot])

    if fig_name is not None:
        for i,fit in enumerate(fits):
            for idx, this_x in enumerate(keep_x[i]):
                n = np.sum(keep_x[i]==this_x) # How many trials, sets the
                                               # markersize
                ax.plot(this_x,keep_y[i][idx],
                        'o',color = colors[i], markersize = n)
                
                x_for_plot = np.linspace(min_x-0.05,
                                         max_x+0.05,100)

            ax.plot(x_for_plot,cumgauss(x_for_plot,fits[i][0],
                                        fits[i][1]),
                    color = colors[i])
            texter = (
                'PSE: %1.2f +/- %1.2f \nslope: %1.2f +/- %1.2f'%(fits[i][0],
                                            (boot_th_ub[i]-boot_th_lb[i])/2,
                                                      fits[i][1],
                                            (boot_sl_ub[i]-boot_sl_lb[i])/2))
            print("For the file: %s \n %s \n"%(data_file, cue_cond) +texter)

            # Indicate the values of the fit:
            ax.text(fits[i][0] + 0.1, fits[i][0] + 0.1,texter)

        fig.savefig(fig_name)

    out = dict(x=[], y=[], trials=[],
               fit=[],
               boot_th_lb=boot_th_lb, boot_th_ub=boot_th_ub,
               boot_sl_lb=boot_sl_lb, boot_sl_ub=boot_sl_ub)

    # Make the return values:
    for i, fit in enumerate(fits):
        out['fit'].append(dict(th=fit[0], sl=fit[1]))
        for idx, this_x in enumerate(np.unique(keep_x[i])):
            x_idx = np.where(keep_x[i]==this_x)[0]
            out['x'].append(x[x_idx[0]])
            out['y'].append(y[x_idx[0]])
            out['trials'].append(np.sum(keep_x[i]==this_x))
    return out

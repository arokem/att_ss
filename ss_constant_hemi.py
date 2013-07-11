"""
Surround Suppression per hemisphere
===================================

Following the design used by Rokem and Landau's 2013 VSS presentation (and
forthcoming paper...), examine surround suppression in each hemisphere.

In this version, the judgement is a simultaneous contrast comparison. Which has
higher contrast, the one on top or the one on the bottom? In each trial, the
stimuli can appear in either hemi-field, and they are brief (120 msec),
encouraging fixation that way.

Assessment of bias can then be done on a per-hemifield basis, or on both
together. 

"""

import numpy as np 
from numpy.random import random, shuffle, randn
from tools import *
from psychopy import visual, core, misc, event
import psychopy.monitors.calibTools as calib
import os

# We'll need this to analyze the data:
import hemi_analysis 

def wait_for_key():
    response = False
    while not response:
        for key in event.getKeys():
            if key in ['escape','q']:
                core.quit()
            else:
                response = True

def make_stimuli(p, win):
    """
    Make the stimuli
    """
    # Short-hand:
    fs = p.fixation_size

    # Standard fixation:
    fixation = visual.PatchStim(win, tex=None, mask = 'circle',color=1.0*p.rgb,
                                size= 0.5 * fs)

    fixation_surround = visual.PatchStim(win, tex=None, mask='circle',
                                         color=-1*p.rgb,
                                         size=0.5 * fs * 1.5)

    fix = [fixation_surround, fixation]
    
    surround = dict(l=dict(u=visual.PatchStim(win,
                                       tex='sin',
                                       mask='circle',
                                       color=p.rgb * p.surr_contrast,
                                       size=p.surr_size,
                                       sf = p.sf,
                                       pos=[-p.ecc, p.height],
                                       ori = p.surr_ori),
                            d=visual.PatchStim(win,
                                       tex='sin',
                                       mask='circle',
                                       color=p.rgb * p.surr_contrast,
                                       size=p.surr_size,
                                       sf = p.sf,
                                       pos=[-p.ecc, -p.height],
                                       ori = p.surr_ori)),
                    r=dict(u=visual.PatchStim(win,
                                        tex='sin',
                                        mask='circle',
                                        color=p.rgb * p.surr_contrast,
                                        size=p.surr_size,
                                        sf = p.sf,
                                        pos=[p.ecc, p.height],
                                        ori = p.surr_ori),
                               d=visual.PatchStim(win,
                                        tex='sin',
                                        mask='circle',
                                        color=p.rgb * p.surr_contrast,
                                        size=p.surr_size,
                                        sf = p.sf,
                                        pos=[p.ecc, -p.height],
                                        ori = p.surr_ori)))
    
    center = dict(l=dict(u=visual.PatchStim(win,
                                     tex='sin',
                                     mask='circle',
                                     color=p.rgb,
                                     size=p.center_size,
                                     sf = p.sf,
                                     pos = [-p.ecc, p.height],
                                     ori = p.center_ori),

                         d=visual.PatchStim(win,
                                     tex='sin',
                                     mask='circle',
                                     color=p.rgb,
                                     size=p.center_size,
                                     sf = p.sf,
                                     pos = [-p.ecc, -p.height],
                                     ori = p.center_ori)),
                                     
                  r=dict(u=visual.PatchStim(win,
                                     tex='sin',
                                     mask='circle',
                                     color=p.rgb,
                                     size=p.center_size,
                                     sf = p.sf,
                                     pos = [p.ecc, p.height],
                                     ori = p.center_ori),
                         d=visual.PatchStim(win,
                                     tex='sin',
                                     mask='circle',
                                     color=p.rgb,
                                     size=p.center_size,
                                     sf = p.sf,
                                     pos = [p.ecc, -p.height],
                                     ori = p.center_ori)))
                                    
    divider = dict(l=dict(u=visual.PatchStim(win,
                                      tex = np.ones((p.res,p.res)),
                                      mask='circle',
                                      color= p.div_color * p.rgb,
                                      size=p.center_size*1.05,
                                      pos = [-p.ecc, p.height]),
                           d=visual.PatchStim(win,
                                      tex = np.ones((p.res,p.res)),
                                      mask='circle',
                                      color= p.div_color * p.rgb,
                                      size=p.center_size*1.05, 
                                      pos = [-p.ecc, -p.height])),
                    r=dict(u=visual.PatchStim(win,
                                      tex = np.ones((p.res,p.res)),
                                      mask='circle',
                                      color= p.div_color * p.rgb,
                                      size=p.center_size*1.05,
                                      pos = [p.ecc, p.height]),
                           d=visual.PatchStim(win,
                                      tex = np.ones((p.res,p.res)),
                                      mask='circle',
                                      color= p.div_color * p.rgb,
                                      size=p.center_size*1.05, 
                                      pos = [p.ecc, -p.height])))

    return fix, center, surround, divider

if __name__ == "__main__":

    p = Params('params_hemi')
    app = wx.App()
    app.MainLoop()
    p.set_by_gui(full=False)
    # Different number of trials for different cue reliability conditions:

    # Just do 75 trials per block:
    n_trials = p.n_trials
    break_trials = p.break_trials # To be on the safe side.
    
    calib.monitorFolder = os.path.join('.','calibration')# over-ride the usual
                                                         # setting of where
                                                         # monitors are stored

    mon = calib.Monitor(p.monitor) #Get the monitor object and pass that as an
                                   #argument to win:    
    
    win = visual.Window(
        size=mon.getSizePix(),
        monitor=mon,
        units='deg',
        screen=p.screen_number,
        fullscr=p.full_screen)

    f = start_data_file(p.subject, 'data_hemi')
    p.save(f)
    
    f = save_data(f, 'trial', 'side', 'surround','contrast1','contrast2','answer', 'rt')

    fix, center, surround, divider = make_stimuli(p, win)
                  
    sides = ['r','l'] # Right or left 
    up_down = ['u','d']
    
    # Get subject input to start: 
    Text(win)()

    # Draw the fixation and flip it on: 
    for this in fix: this.draw()
    win.flip()

    # Wait for an iti before starting the first trial:
    core.wait(p.iti)

    conds = []

    # How many conditions are there:
    for center_c in p.center_contrast:
        for center_comp in p.center_comparison:
            conds.append([center_c, center_comp])
    conds = np.array(conds)
    n_conds = conds.shape[0]
    
    cond_randomizer = np.mod(np.random.permutation(n_trials), n_conds)
    # For the surrounded stimulus:
    center_contrast = conds[cond_randomizer][:,0]
    # For the comparison stimulus:
    center_comparison = conds[cond_randomizer][:,1]
    
    for trial in xrange(n_trials):
        # Randomly choose a side for the stimulus:
        side_idx = np.random.randint(2)
        this_side = sides[side_idx]
        this_surround = surround[this_side]
        this_center = center[this_side]
        this_divider = divider[this_side]

        # Randomly choose where the surrounded stimulus will be:
        updown_idx = np.random.randint(2)
        surround_ud = up_down[updown_idx]
        # This gives you the other one:
        comparison_ud = up_down[np.mod(updown_idx+1,2)]
        
        # dbg:
        #win.getMovieFrame()
        #win.saveMovieFrames('/Users/arokem/projects/att_ss/figures/fig.png')
              
        # Draw the fixation and move on: 
        for this in fix: this.draw()
        win.flip()
        core.wait(p.cue_to_stim)

        # Choose one random phase for all the gratings in this trial: 
        ph_rand = (np.random.rand(1) * 2*np.pi) - np.pi

        # Get a clock just for this:
        stim_clock = core.Clock()
        t = 0

        this_center_contrast = np.min([np.max([center_contrast[trial], 0.01]), 1.0]) * p.rgb
        this_center_comparison = np.min([np.max(
            [center_contrast[trial] + center_comparison[trial], 0.01]), 1.0]) * p.rgb
        
        # Set the contrasts of both of the center stimuli:
        this_center[surround_ud].setColor(this_center_contrast)
        this_surround[surround_ud].setColor(p.surr_contrast * p.rgb)
        
        this_center[comparison_ud].setColor(this_center_comparison * p.rgb)
        this_surround[comparison_ud].setColor(0 * p.rgb)

        # Draw all yer elements:
        for part in [this_surround, this_divider, this_center]:
            for this_part in part:
                part[this_part].draw()
        for this in fix: this.draw()

        win.flip()
        # dbg:
        #win.getMovieFrame()
        #win.saveMovieFrames('/Users/arokem/projects/att_ss/figures/fig.png')
                                
        # Wait for the stimulus duration
        core.wait(p.stim_dur)
        # Then take it away:
        for this in fix: this.draw()
        win.flip()
            
        # Get a response:
        response = False
        while not response:
            for key in event.getKeys():
                if key in ['escape','q']:
                    f.close()
                    win.close()
                    core.quit()
                elif key in ['1','2']:
                        response = True
                        rt = stim_clock.getTime()
                                
        core.wait(p.iti)
        event.clearEvents()  # keep the event buffer from overflowing
        
        f = save_data(f,
                      trial,
                      this_side,
                      surround_ud,
                      this_center['u'].color[0],
                      this_center['d'].color[0],
                      key,
                      rt)

        # Is it time for a break?
        if trial>0 and np.mod(trial, break_trials)==0:
            Text(win,"Take a break. \n Press any key to continue")()

    win.close()
    f.close()

    # Per default the analysis proceeds with cumulative Gaussian as the
    # fit function:

    fig_stem = f.name.split('/')[-1].split('.')[0]

    # XXX Need to put the analysis here...
    hemi_analysis.analyze(f.name, fig_name='data_hemi/%s_cued.png'%fig_stem)
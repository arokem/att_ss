"""
Attention Surround Suppression
==============================

Examine surround suppression under simple conditions of attentional
expectation. In each trial, a cue indicates a more likely location for a
contrast 2AFC location. After the stimuli appear, a target appears in only one
location and a judgement (which interval had higher contrast?) is done in the
location.

This version will have constant stimuli presented and no feedback during the 
block (to prevent calibration), instead of the previous staircase and trial-by-trial
feedback. 

"""

import numpy as np 
from numpy.random import random, shuffle, randn
from tools import *
from psychopy import visual, core, misc, event
import psychopy.monitors.calibTools as calib
import os

def wait_for_key():
    response = False
    while not response:
        for key in event.getKeys():
            if key in ['escape','q']:
                core.quit()
            else:
                response = True
    
if __name__ == "__main__":

    p = Params('params_constant')
    app = wx.App()
    app.MainLoop()
    p.set_by_gui()
    # Different number of trials for different cue reliability conditions:

    # If this is a predictive cue, do 250 trials, with breaks every 50:
    if p.cue_reliability:
        n_trials = 250
        break_trials = 50

    # If this is a neutral cue, do 75 trials, with no break:
    else:
        n_trials = 75
        break_trials = 76 # To be on the safe side.
    


        
    # calib.monitorFolder = os.path.join('.','calibration')# over-ride the usual
                                                         # setting of where
                                                         # monitors are stored

    # mon = calib.Monitor(p.monitor) #Get the monitor object and pass that as an
                                   #argument to win:
                                   
    
    win = visual.Window(
        monitor=p.monitor,
        units='deg',
        screen=p.screen_number,
        fullscr=p.full_screen)

    f = start_data_file(p.subject)
    p.save(f)
    
    f = save_data(f, 'trial', 'cue_side', 'ask_side', 'r_contrast1',
                  'r_contrast2', 'l_contrast1', 'l_contrast2', 'answer',
                  'ask_contrast', 'rt')

    # Make the stimuli: 
    
    # Short-hand:
    fs = p.fixation_size

    # Standard fixation:
    fixation = visual.PatchStim(win, tex=None, mask = 'circle',color=0.5*p.rgb,
                                size= 0.5 * fs)

    fixation_surround = visual.PatchStim(win, tex=None, mask='circle',
                                         color=-0.5*p.rgb,
                                         size=0.5 * fs * 1.5)

    fix = [fixation_surround, fixation]

    cue_vert = dict(r=dict(cue=((fs/2, 0),(-fs/2, fs/2),(-fs/2,-fs/2)),
                           surr=((fs/1.5, 0),(-fs/1.5, fs/1.5),(-fs/1.5,
                           -fs/1.5))),
                    l=dict(cue=((-fs/2, 0),(fs/2, fs/2),(fs/2,-fs/2)),
                           surr=((-fs/1.5, 0),(fs/1.5, fs/1.5),(fs/1.5,
                           -fs/1.5))))
                                   
    if p.cue_reliability:
    # Triangle fixation (with black penumbra), used as a cue for the
    # target-detection task:
        cue = dict(r=dict(cue=visual.ShapeStim(win, fillColor=1*p.rgb,
                                           lineColor=1*p.rgb,
                                            vertices=cue_vert['r']['cue']),
                          surr=visual.ShapeStim(win, fillColor=-1*p.rgb,
                                            lineColor=-1*p.rgb,
                                            vertices=cue_vert['r']['surr'])),
                   l=dict(cue=visual.ShapeStim(win, fillColor=1*p.rgb,
                                           lineColor=1*p.rgb,
                                           vertices=cue_vert['l']['cue']),
                      surr=visual.ShapeStim(win, fillColor=-1*p.rgb,
                                            lineColor=-1*p.rgb,
                                            vertices=cue_vert['l']['surr'])))

    else:
        c = ((-fs/2,0),(0, fs/2), (fs/2, 0),(0,-fs/2))
        s = ((-fs/1.5,0),(0, fs/1.5),(fs/1.5, 0),(0,-fs/1.5))
        neutral_cue = visual.ShapeStim(win, fillColor=1*p.rgb,
                                       lineColor=1*p.rgb,
                                        vertices=c)
        neutral_surr = visual.ShapeStim(win, fillColor=-1*p.rgb,
                                        lineColor=-1*p.rgb,
                                    vertices=s)
        # Show an uninformative diamond at the same time (neutral cue)
        cue = dict(r=dict(cue=neutral_cue,surr=neutral_surr),
                   l=dict(cue=neutral_cue,surr=neutral_surr))
        
    surround = dict(r=visual.PatchStim(win,
                                       tex='sin',
                                       mask='circle',
                                       color=p.rgb * p.surr_contrast,
                                       size=p.surr_size,
                                       sf = p.sf,
                                       pos=[p.ecc, 0],
                                       ori = p.surr_ori),
                    l=visual.PatchStim(win,
                                       tex='sin',
                                       mask='circle',
                                       color=p.rgb * p.surr_contrast,
                                       size=p.surr_size,
                                       sf = p.sf,
                                       pos=[-p.ecc, 0],
                                       ori = p.surr_ori))
    
    center = dict(r=visual.PatchStim(win,
                                     tex='sin',
                                     mask='circle',
                                     color=p.rgb,
                                     size=p.center_size,
                                     sf = p.sf,
                                     pos = [p.ecc, 0],
                                     ori = p.center_ori),
                  l=visual.PatchStim(win,
                                     tex='sin',
                                     mask='circle',
                                     color=p.rgb,
                                     size=p.center_size,
                                     sf = p.sf,
                                     pos = [-p.ecc, 0],
                                     ori = p.center_ori))

    divider = dict(l=visual.PatchStim(win,
                                      tex = np.ones((p.res,p.res)),
                                      mask='circle',
                                      color= p.div_color * p.rgb,
                                      size=p.center_size*1.05,
                                      pos = [-p.ecc, 0]),
                   r=visual.PatchStim(win,
                                      tex = np.ones((p.res,p.res)),
                                      mask='circle',
                                      color= p.div_color * p.rgb,
                                      size=p.center_size*1.05, 
                                      pos = [p.ecc, 0]))
                  
    sides = ['r','l'] # Right or left 

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
    center_contrast1 = conds[cond_randomizer][:,0]
    center_comparison1 = conds[cond_randomizer][:,1]
    # Randomize again the for the foil side:
    cond_randomizer = np.mod(np.random.permutation(n_trials), n_conds)
    center_contrast2 = conds[cond_randomizer][:, 0]
    center_comparison2 = conds[cond_randomizer][:,1]
    
    for trial in xrange(n_trials):
        # Randomly choose a side for the cue:
        side_idx = np.random.randint(2)
        cue_side = sides[side_idx]
        other_side = sides[np.mod(side_idx + 1, 2)]
                  
        # Is the cue reliable this trial?  
        cue_true = np.random.rand() < p.cue_reliability # If p.cue_reliability
                                        # is set to "False", this always
                                        # evaluates to False
        if cue_true:
            ask_side = cue_side
            foil_side = other_side
        else:
            ask_side = other_side  
            foil_side = cue_side

        # Initialize a dict for the contrasts:
        contrasts = {}

        # The second contrast is always the baseline and the question is always
        # whether the first contrast is higher or lower than that, where the
        # first interval contrast was set pseudo-randomly above:
        ask_contrast = center_comparison1[trial]
        contrasts[ask_side] = [
            center_contrast1[trial] + ask_contrast, 
            center_contrast1[trial]
            ]

        # For the foil side, the second contrast is always 0: 
        contrasts[foil_side] = [
            center_contrast2[trial] + center_comparison2[trial], 
                0]
        
        #Draw the cue, wait for the alloted time and move on:
        for this in  [cue[cue_side]['surr'], cue[cue_side]['cue']] : this.draw()
        win.flip()

        # dbg:
        win.getMovieFrame()
        win.saveMovieFrames('/Users/arokem/projects/att_ss/figures/fig.png')
              
        core.wait(p.cue_dur)

        # Draw the fixation and move on: 
        for this in fix: this.draw()
        win.flip()
        core.wait(p.cue_to_stim)

        # Choose one random phase for all the gratings for this trial: 
        ph_rand = (np.random.rand(1) * 2*np.pi) - np.pi

        for interval in range(2):
            # Get a clock just for this:
            stim_clock = core.Clock()
            t = 0 
            # Keep going for the duration:
            while t < p.stim_dur:
                t = stim_clock.getTime()
                # Set the contrasts of the center stimuli:
                for this in center:
                    center[this].setColor(contrasts[this][interval] * p.rgb)
                for this in surround.values():
                    if interval==0 or p.surround_w_target:
                        # Only flicker if temporal_freq is not 0:
                        if p.temporal_freq:
                            # Counter-phase flicker: 
                            this.setContrast(np.sin(ph_rand +
                                                    t * p.temporal_freq *
                                                    np.pi *2))
                        # Draw either way:
                        this.draw()
                for this in divider.values(): 
                    # This one needs no flicker:
                    this.draw()
                for this in center.values():
                    # Only flicker if temporal_freq is not 0:
                    if p.temporal_freq:
                        this.setContrast(np.sin(ph_rand +
                                                t * p.temporal_freq *
                                                np.pi *2))
                    # Draw either way:
                    this.draw()
                for this in fix: this.draw()
                win.flip()

                # dbg:
                #win.getMovieFrame()
            #win.saveMovieFrames('/Users/arokem/projects/att_ss/figures/fig.png')
                
            # Before going into the second interval, set the contrast for the
            # other side to be 0:
            surround[foil_side].setColor(0)
            divider[foil_side].setColor(0)                
                
            # Wait for the ISI
            for this in fix: this.draw()
            win.flip()
            core.wait(p.stim_to_stim)

        # Once out of this loop, set the color back for the next trial:
        surround[foil_side].setColor(p.surr_contrast * p.rgb)
        divider[foil_side].setColor(p.div_color * p.rgb)

        for this in fix: this.draw()
        win.flip()

        if contrasts[ask_side][0]>contrasts[ask_side][1]:
            correct_ans = '1'
        elif contrasts[ask_side][0]<contrasts[ask_side][1]:
            correct_ans = '2'

        # If this is a 0 difference trial, choose a random correct answer from
        # the two options: 
        else:
            correct_ans = ['1','2'][np.random.randint(2)]

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
                        # RT from the onset of the second stimulus:
                        rt = stim_clock.getTime()
                        if p.audio_feedback:
                            if key==correct_ans:
                                p.correct_sound.play()
                            else:
                                p.incorrect_sound.play()
                                
        core.wait(p.iti)
        event.clearEvents()  # keep the event buffer from overflowing
        
        # Save this trial to file:
        f = save_data(f,
                      trial,
                      cue_side,
                      ask_side,
                      contrasts['r'][0],
                      contrasts['r'][1],
                      contrasts['l'][0],
                      contrasts['l'][1],
                      key,
                      ask_contrast,
                      rt)

        # Is it time for a break?
        if trial>0 and np.mod(trial, break_trials)==0:
            Text(win,"Take a break. \n Press any key to continue")()

    win.close()
    f.close()
    fig_stem = f.name.split('/')[-1].split('.')[0]

    # Per default the analysis proceeds with cumulative Gaussian as the
    # fit function:

    if p.cue_reliability: 
        # There was a cued and an 'other' condition:
        analyze_constant(f.name, fig_name='data/%s_cued.png'%fig_stem,
                         cue_cond='cued')
    
        analyze_constant(f.name, fig_name='data/%s_other.png'%fig_stem,
                         cue_cond='other')
    else: 
        analyze_constant(f.name, fig_name='data/%s_neutral.png'%fig_stem,
                         cue_cond='other') # In the neutral cue condition, all
                                        # the trials are considered to be
                                        # 'other' trials.
    

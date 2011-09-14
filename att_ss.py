"""
Attention Surround Suppression
==============================

Examine surround suppression under simple conditions of attentional
expectation. In each trial, a cue indicates a more likely location for a
contrast decrement. After the stimuli appear, a post-cue appears, which tells
you for which location you are supposed to report in this trial. Post-cue
follows the pre-cue location with some probability 

"""

import numpy as np 
from numpy.random import random, shuffle, randn
from tools import *
from psychopy import visual, core, misc, event
import psychopy.monitors.calibTools as calib

def wait_for_key():
    response = False
    while not response:
        for key in event.getKeys():
            if key in ['escape','q']:
                core.quit()
            else:
                response = True
    
if __name__ == "__main__":

    p = Params()
    app = wx.App()
    app.MainLoop()
    p.set_by_gui()
        
    calib.monitorFolder = './calibration/'# over-ride the usual setting of where
                                      # monitors are stored

    mon = calib.Monitor(p.monitor) #Get the monitor object and pass that as an
                                   #argument to win:
                                   
    win = visual.Window(monitor=mon,units='deg',screen=p.screen_number,
                    fullscr=p.full_screen)

    # Get the fps 
    fps = 1/(visual.getMsPerFrame(win)[2]/1000)

    f = start_data_file(p.subject)
    p.save(f)
    
    f = save_data(f,'trial','cue','target','amp','correct','rt')

    # Make the stimuli: 
    # ================
    # Short-hand:
    fs = p.fixation_size

    # Standard fixation:
    fixation = visual.PatchStim(win, tex=None, mask = 'circle',color=1*p.rgb,
                                size=fs)

    fixation_surround = visual.PatchStim(win, tex=None, mask='circle',
                                         color=-1*p.rgb,
                                         size=fs*1.5)

    fix = [fixation_surround, fixation]
    
    # Cues:
    # Triangle fixation, used as a cue for the target-detection task: 
    cue_r = visual.ShapeStim(win, fillColor=1*p.rgb, lineColor=1*p.rgb,
                                 vertices=((fs/2, 0),(-fs/2, fs/2),(-fs/2, -fs/2)))
    #With a black penumbra:
    cue_r_surround = visual.ShapeStim(win, fillColor=-1*p.rgb, lineColor=-1*p.rgb,
                vertices=((fs/1.5, 0),(-fs/1.5, fs/1.5),(-fs/1.5, -fs/1.5)))   

    #Triangle fixation, used as a cue for the target-detection task: 
    cue_l = visual.ShapeStim(win, fillColor=1*p.rgb, lineColor=1*p.rgb,
                                vertices=((-fs/2, 0),(fs/2, fs/2),(fs/2, -fs/2)))
    #With a black penumbra:
    cue_l_surround = visual.ShapeStim(win, fillColor=-1*p.rgb, lineColor=-1*p.rgb,
                vertices=((-fs/1.5, 0),(fs/1.5, fs/1.5),(fs/1.5, -fs/1.5)))    
    
    surr_r = visual.PatchStim(win,
                              tex='sin',
                              mask='circle',
                              color=p.rgb * p.surr_contrast,
                              size=p.surr_size,
                              sf = p.sf,
                              pos=[p.ecc, 0])

    surr_l = visual.PatchStim(win,
                              tex='sin',
                              mask='circle',
                              color=p.rgb * p.surr_contrast,
                              size=p.surr_size,
                              sf = p.sf,
                              pos=[-p.ecc, 0])
    
    center_r = visual.PatchStim(win,
                                tex='sin',
                                mask='circle',
                                color=p.center_contrast * p.rgb,
                                size=p.center_size,
                                sf = p.sf,
                                pos = [p.ecc, 0],
                                ori = p.center_ori)

    center_l = visual.PatchStim(win,
                                tex='sin',
                                mask='circle',
                                color=p.center_contrast * p.rgb,
                                size=p.center_size,
                                sf = p.sf,
                                pos = [-p.ecc, 0],
                                ori = p.center_ori)

    center_bkgrnd_l = visual.PatchStim(win,
                                       tex = np.ones((p.res,p.res)),
                                     mask='circle',
                                     color= -1 * p.rgb,
                                     size=p.center_size*1.05,
                                     pos = [-p.ecc, 0])

    center_bkgrnd_r = visual.PatchStim(win,
                                       tex = np.ones((p.res,p.res)),
                                       mask='circle',
                                       color= -1 * p.rgb,
                                       size=p.center_size*1.05, 
                                       pos = [p.ecc, 0])


    # Start your staircases:
    # ======================

    stair_cued = Staircase(p.start_amp, p.step)
    stair_other = Staircase(p.start_amp, p.step)
    
    sides = ['r','l'] # Right or left 
    stim_dir = [1,-1] # Increase or decrease contrast 

    # Get subject input to start: 
    Text(win)()

    # Draw the fixation and flip it on: 
    for this in fix: this.draw()
    win.flip()

    # Get a time-keeper: 
    clock = core.Clock()

    # Wait for an iti before starting the first trial:
    core.wait(p.iti)

    for trial in xrange(p.n_trials):
        # In each trial, reset the clock:
        clock.reset()

        # Randomly choose a side for the cue:
        side_idx = np.random.randint(2)
        cue_side = sides[side_idx]

        # Is the cue reliable this trial? 
        if np.random.rand() > p.cue_reliability:
            cue_true = True
            ask_side = cue_side
        else:
            cue_true = False
            ask_side = sides[np.mod(side_idx+1, 2)]  # the other one

        if cue_side == 'r':
            arrow = [cue_r_surround, cue_r]
        else:
            arrow = [cue_l_surround, cue_l]

        #Draw the cue, wait for the alloted time and move on:
        for this in arrow: this.draw()
        win.flip()
        core.wait(p.cue_dur)

        # Draw the fixation and move on: 
        for this in fix: this.draw()
        win.flip()
        core.wait(p.cue_to_stim)

        # Randomly choose increasing or decreasing contrast for each side:
        change_cue = stim_dir[np.random.randint(2)]
        change_other = stim_dir[np.random.randint(2)]        

        # Calculate how many amps you need to have for the duration, given the
        # fps provided by the monitor: 
        n_amps = p.refresh_rate * p.stim_dur

        # What are the current amps: 
        amp_cue = np.linspace(p.center_contrast + change_cue*stair_cued.value,
                              p.center_contrast - change_cue*stair_cued.value,
                              n_amps)
                              
        amp_other = np.linspace(p.center_contrast + change_cue*stair_other.value,
                                p.center_contrast - change_cue*stair_other.value,
                                n_amps)
                          
        # Get a clock just for this:
        stim_clock = core.Clock()
        
        # Choose one random phase for all the gratings for this trial: 
        ph_rand = (np.random.rand(1) * 2*np.pi) - np.pi

        # We iterate over frames:
        for frame in range(n_amps):
            t = stim_clock.getTime()
            # Set the contrast of the centers:
            if cue_side == 'l':
                center_l.setColor(amp_cue[frame]*p.rgb)
                center_r.setColor(amp_other[frame]*p.rgb)
            else:
                center_r.setColor(amp_cue[frame]*p.rgb)
                center_l.setColor(amp_other[frame]*p.rgb)
            # Set the phase in the 
            for this in [surr_l, surr_r]:
                # Counter-phase flicker: 
                this.setContrast(np.sin(ph_rand + t*p.temporal_freq * np.pi *2))
                this.draw()
            for this in [center_bkgrnd_r, center_bkgrnd_l]: 
                # This one needs no flicker:
                this.draw()
            for this in [center_l, center_r]:
                # Counter-phase flicker: 
                this.setContrast(np.sin(ph_rand + t*p.temporal_freq * np.pi *2))
                this.draw()
            for this in fix: this.draw()

            win.flip()
        
        # Where do we show the question mark?
        if cue_true:
            if cue_side=='l':
                ask_pos = -p.ecc
            else:
                ask_pos = p.ecc

            if change_cue > 0:
                correct_ans = '1'
            else:
                correct_ans = '2'
            stair_to_update = stair_cued

        else:
            if cue_side=='r':
                ask_pos = -p.ecc
            else:
                ask_pos = p.ecc

            if change_other > 0:
                correct_ans = '1'
            else:
                correct_ans = '2'
            stair_to_update = stair_other

        question = visual.TextStim(win, '?', pos = [ask_pos, 0])
        question.draw()
        for this in fix: this.draw() 
        win.flip()
                        
        response = False
        while not response:
            for key in event.getKeys():
                if key in ['escape','q']:
                    f.close()
                    win.close()
                    core.quit()
                elif key in ['1','2']:
                    if key in correct_ans:
                        p.correct_sound.play()
                        correct = 1
                        response = True
                        rt = clock.getTime()
                    else:
                        p.incorrect_sound.play()
                        correct = 0
                        response = True
                        rt = clock.getTime()
                    stair_to_update.update(correct)
                            
        core.wait(p.iti)
        event.clearEvents()  # keep the event buffer from overflowing
        # 'trial','cue','target','amp','correct','rt'
        f = save_data(f,
                      trial,
                      cue_side,
                      ask_side,
                      stair_to_update.value,
                      correct,
                      rt)

    win.close()
    f.close()
            

"""
Attention Surround Suppression
==============================

Examine surround suppression under simple conditions of attentional
expectation. In each trial, a cue indicates a more likely location for a
contrast 2AFC location. After the stimuli appear, a target appears in only one
location and a judgement (which interval had higher contrast?) is done in the
location.

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

    f = start_data_file(p.subject)
    p.save(f)
    
    f = save_data(f, 'trial', 'cue_side', 'ask_side', 'r_contrast1', 'r_contrast2',
                  'l_contrast1', 'l_contrast2', 'correct', 'rt')

    # Make the stimuli: 
    
    # Short-hand:
    fs = p.fixation_size

    # Standard fixation:
    fixation = visual.PatchStim(win, tex=None, mask = 'circle',color=1*p.rgb,
                                size=fs)

    fixation_surround = visual.PatchStim(win, tex=None, mask='circle',
                                         color=-1*p.rgb,
                                         size=fs*1.5)

    fix = [fixation_surround, fixation]
    
    # Triangle fixation (with black penumbra), used as a cue for the target-detection task:
    cue = dict(r=dict(cue=visual.ShapeStim(win, fillColor=1*p.rgb, lineColor=1*p.rgb,
                                    vertices=((fs/2, 0),(-fs/2, fs/2),(-fs/2,-fs/2))),
                      surr=visual.ShapeStim(win, fillColor=-1*p.rgb, lineColor=-1*p.rgb,
                        vertices=((fs/1.5, 0),(-fs/1.5, fs/1.5),(-fs/1.5, -fs/1.5)))),
               l=dict(cue=visual.ShapeStim(win, fillColor=1*p.rgb, lineColor=1*p.rgb,
                            vertices=((-fs/2, 0),(fs/2, fs/2),(fs/2,-fs/2))),
                      surr=visual.ShapeStim(win, fillColor=-1*p.rgb, lineColor=-1*p.rgb,
                vertices=((-fs/1.5, 0),(fs/1.5, fs/1.5),(fs/1.5, -fs/1.5)))))    
    
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
                                     color=p.center_contrast * p.rgb,
                                     size=p.center_size,
                                     sf = p.sf,
                                     pos = [p.ecc, 0],
                                     ori = p.center_ori),
                  l=visual.PatchStim(win,
                                     tex='sin',
                                     mask='circle',
                                     color=p.center_contrast * p.rgb,
                                     size=p.center_size,
                                     sf = p.sf,
                                     pos = [-p.ecc, 0],
                                     ori = p.center_ori))

    divider = dict(l=visual.PatchStim(win,
                                      tex = np.ones((p.res,p.res)),
                                      mask='circle',
                                      color= -1 * p.rgb,
                                      size=p.center_size*1.05,
                                      pos = [-p.ecc, 0]),
                   r=visual.PatchStim(win,
                                      tex = np.ones((p.res,p.res)),
                                      mask='circle',
                                      color= -1 * p.rgb,
                                      size=p.center_size*1.05, 
                                      pos = [p.ecc, 0]))
                  
    # Start staircases:
    stair_cued = Staircase(p.start_amp, p.step)
    stair_other = Staircase(p.start_amp, p.step)
    
    sides = ['r','l'] # Right or left 

    # Get subject input to start: 
    Text(win)()

    # Draw the fixation and flip it on: 
    for this in fix: this.draw()
    win.flip()

    # Wait for an iti before starting the first trial:
    core.wait(p.iti)

    for trial in xrange(p.n_trials):
        # Randomly choose a side for the cue:
        side_idx = np.random.randint(2)
        cue_side = sides[side_idx]
        other_side = sides[np.mod(side_idx + 1, 2)]

        # Initialize a dict to hold the staircases for this trial:
        trial_stairs = {cue_side:stair_cued,
                        other_side:stair_other}
                  
        # Is the cue reliable this trial? 
        cue_true = np.random.rand() < p.cue_reliability

        # What's the right answer this trial (1 for high first, -1 for high second)? 
        contrast_order = np.sign(np.random.randn())

        # Set this up so that you can collect responses later:
        if contrast_order > 0:
            correct_ans = '1'
        else:
            correct_ans = '2'
                  
        if cue_true:
            ask_side = cue_side
            foil_side = other_side
        else:
            ask_side = other_side  
            foil_side = cue_side

        # Have the 'standard' contrasts rove a little bit, so that the task
        # cannot be solved purely by examining interval 2 (limit it between
        # 0.75 and 0.25, though), or by comparing the two patches to each other:
        center_contrast = {}
        for side in [ask_side,foil_side]:
            rove_contrast = p.center_contrast + np.random.randn() * p.center_c_var
            if rove_contrast > 0.75:
                rove_contrast = 0.75
            if rove_contrast < 0.25:
                rove_contrast = 0.25
            center_contrast[side] = rove_contrast

        # Initialize a dict for the contrasts:
        contrasts = {}

        # And fill it in (note the staircase values are in % of the 'base' contrast):
        contrasts[ask_side] = [

            center_contrast[ask_side] +
            (contrast_order * trial_stairs[ask_side].value/2 *
            center_contrast[ask_side]),
            
            (center_contrast[ask_side] -
             contrast_order * trial_stairs[ask_side].value/2
             * center_contrast[ask_side])
            ]
        
        # Set the contrast for the first interval randomly, based on the
        # relevant staircase. The second interval is 0:
        contrasts[foil_side] = [center_contrast[foil_side] +
                                np.sign(np.random.randn()) *
                                trial_stairs[foil_side].value/2,  0]
        
        #Draw the cue, wait for the alloted time and move on:
        for this in  [cue[cue_side]['surr'], cue[cue_side]['cue']] : this.draw()
        win.flip()
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
                # Only in the first interval
                if interval == 0:
                    for this in surround.values():
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

            # Wait for the ISI
            for this in fix: this.draw()
            win.flip()
            core.wait(p.stim_to_stim)

        for this in fix: this.draw()
        win.flip()

        # Get a responsee:
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
                        # RT from the onset of the second stimulus:
                        rt = stim_clock.getTime()
                    else:
                        p.incorrect_sound.play()
                        correct = 0
                        response = True
                        # RT from the onset of the second stimulus:
                        rt = stim_clock.getTime()

                    # Update the staircase:
                    trial_stairs[ask_side].update(correct)
                            
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
                      correct,
                      rt)

    win.close()
    f.close()
    fig_stem = f.name.split('/')[-1].split('.')[0]

    stair_cued.analyze(fig_name='data/%s_cued.png'%fig_stem)
    stair_other.analyze(fig_name='data/%s_other.png'%fig_stem)
    

import numpy as np
from tools import sound_freq_sweep
from psychopy.sound import Sound

p = dict(
    # Display:
    monitor = 'ESI_psychophys',
    full_screen = False,
    screen_number = 0, #1,
    refresh_rate = 60, # Hz
    # Sounds:
    correct_sound = Sound(sound_freq_sweep(2000,2000,.1)),
    incorrect_sound = Sound(sound_freq_sweep(8000, 200, .1)),
    # General:
    fixation_size = 0.25,
    rgb = np.array([1.,1.,1.]),
    # The reliability of the cue. Set to a probability or to False (for neutral
    # cue): 
    #trying to change this to a input parameter
    #cue_reliability = False, 
    # cue_reliability = 0.7, 
    
    
    # Stimuli:
    res = 128,
    temporal_freq = 4, # 0 for no flicker
    sf = 2, # cycles/deg
    ecc = 6, # dva 
    center_size = 3,
    surr_size = 8,
    center_contrast = np.array([0.3]),
    center_comparison = np.array( [-0.29, -0.2, -0.1, 0., 0.1, 0.2,
                                   0.25, 0.3, 0.35, 0.4, 0.6]),
    surr_contrast = 1,
    div_color = -1,
    # Timing: 
    cue_dur = 0.5,
    cue_to_stim = 0.3,
    stim_dur = 0.38,
    stim_to_stim = 0.4,
    iti = .2,
    )

# Different number of trials for different cue reliability conditions:

# If this is a predictive cue, do 250 trials, with breaks every 50:
if p['cue_reliability']:
   p['n_trials'] = 250
   p['break_trials'] = 50

# If this is a neutral cue, do 75 trials, with no break:
else:
   p['n_trials'] = 75
   p['break_trials'] = 76 # To be on the safe side.
    

from tools import sound_freq_sweep,compound_sound
import numpy as np
from psychopy.sound import Sound
from psychopy import visual

p = dict(
    # Display:
    monitor = 'testMonitor',
    full_screen = False, #True,
    screen_number = 0, #1,
    refresh_rate = 60,
    # Sounds:
    correct_sound = Sound(sound_freq_sweep(2000,2000,.1)),
    incorrect_sound = Sound(sound_freq_sweep(8000, 200, .1)),
    # General:
    n_trials = 150,
    fixation_size = 0.1,
    rgb = np.array([1.,1.,1.]),
    cue_reliability = 0.7,
    # Stimuli:
    res = 128,
    temporal_freq = 4,
    sf = 4, # cycles/deg
    ecc = 4, # dva 
    center_size = 2.5,
    surr_size = 5,
    center_contrast = 0.5,
    surr_contrast = 1,
    # Staircase: 
    start_amp = 0.2,
    step = 0.05, 
    # Timing: 
    cue_dur = 2,
    cue_to_stim = 0.05,
    stim_dur = 1, 
    iti = .2,
    )

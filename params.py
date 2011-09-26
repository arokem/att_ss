import numpy as np
from tools import sound_freq_sweep
from psychopy.sound import Sound

p = dict(
    # Display:
    monitor = 'testMonitor',
    full_screen = False,
    screen_number = 0, #1,
    refresh_rate = 60, # Hz
    # Sounds:
    correct_sound = Sound(sound_freq_sweep(2000,2000,.1)),
    incorrect_sound = Sound(sound_freq_sweep(8000, 200, .1)),
    # General:
    n_trials = 250,
    break_trials = 50,
    fixation_size = 0.25,
    rgb = np.array([1.,1.,1.]),
    cue_reliability = 0.7,
    # Stimuli:
    res = 128,
    temporal_freq = 4, # 0 for no flicker
    sf = 4, # cycles/deg
    ecc = 6, # dva 
    center_size = 3,
    surr_size = 8,
    center_contrast = 0.5,
    center_c_var = 0.05,
    surr_contrast = 1,
    div_color = -1,
    # Staircase: 
    start_amp = 0.05,
    step = 0.01, 
    # Timing: 
    cue_dur = 0.5,
    cue_to_stim = 0.3,
    stim_dur = 0.38,
    stim_to_stim = 0.4,
    iti = .2,
    )

import numpy as np
from tools import sound_freq_sweep
from psychopy.sound import Sound

p = dict(
    surr_contrast =1,
    # Display:
    monitor = 'VISTA_DellP1130',
    full_screen = True,
    screen_number = 1, #1,
    refresh_rate = 120, # Hz
    # Sounds:
    #correct_sound = Sound(sound_freq_sweep(2000,2000,.1)),
    #incorrect_sound = Sound(sound_freq_sweep(8000, 200, .1)),
    # General:
    fixation_size = 0.25,
    rgb = np.array([1.,1.,1.]),
    # Stimuli:
    res = 128,
    temporal_freq = 4, # 0 for no flicker
    sf = 2, # cycles/deg
    ecc = 6, # dva 
    center_size = 3,
    surr_size = 8,
    center_contrast = np.array([0.3, 0.45, 0.6]),
    center_comparison = np.array( [-0.29, -0.2, -0.1, 0., 0.1, 0.2,
                                                       0.25, 0.3, 0.35, 0.4, 0.6]),
    div_color = -1,
    # Timing: 
    cue_dur = 0,
    cue_to_stim = 0.1,
    stim_dur = 0.3,
    stim_to_stim = 0.2,
    iti = .2,
    cue_reliability=False,
    surround_w_target=False,
    audio_feedback=False
    )


import numpy as np
from tools import sound_freq_sweep

p = dict(
    # Display:
    monitor = 'VISTA_DellP1130',
    full_screen = True,
    screen_number = 1, #1,
    refresh_rate = 60, # Hz
    # General:
    fixation_size = 0.5,
    rgb = np.array([1.,1.,1.]),
    # Stimuli:
    res = 128,
    temporal_freq = 4, # 0 for no flicker
    sf = 2, # cycles/deg
    ecc = 6, # dva
    height = 4,
    center_size = 3,
    surr_size = 8,
    center_contrast = np.array([0.15, 0.3, 0.6]),
    center_comparison = np.array( [-0.29, -0.2, -0.1, 0., 0.1, 0.2,
                                   0.25, 0.3, 0.35, 0.4, 0.6]),
    surr_contrast = 1,
    div_color = -1,
    # Timing: 
    cue_dur = 0.5,
    cue_to_stim = 0.3,
    stim_dur = 0.2,
    iti = .2,
    )


"""

Make a simple model of contrast discrimination and modulation thereof by
attention and surround suppression

"""

import numpy as np
import tools
reload(tools)
from analyze_constant import run_analysis

if __name__=="__main__":
    sides = ['l', 'r']
    suppression = 0.2
    cue_reliability = 0.7
    std1 = [0.1, 0.3]
    std2 = 0.1
    answer = []
    comparison = []

    center_contrast = np.array([0.3])
    center_comparison = np.array( [-0.29, -0.2, -0.1, 0., 0.1, 0.2,
                                   0.25, 0.3, 0.35, 0.4, 0.6])

    f = file('model_results.csv','w')
    f.write('### MODEL SIMULATION RESULTS:\n')
    # Write in some params that the analysis will be looking for:
    f.write('# cue_reliability : %s \n'%cue_reliability)
    f.write('# center_contrast : %s \n'%center_contrast)
    f.write('# center_comparison : %s\n'%center_comparison)
    f.write('# std1 : %s\n'%std1)
    f.write('# std2 : %s\n'%std2)
    
    f.write('trial,cue_side,ask_side,r_contrast1,r_contrast2,l_contrast1,l_contrast2,answer,ask_contrast\n')
    

    # Run an integer multiple of the center_comparison conditions trials:
    for trial in range(20 * len(center_comparison)):
        f.write('%s,'%trial)
    
        side_idx = np.random.randint(0,2)
        cue_side = sides[side_idx]
        f.write('%s,'%cue_side)
        if np.random.rand() < cue_reliability:
            ask_side = cue_side
            std_atten = std1[0]
        else:
            ask_side = sides[np.mod(side_idx + 1, 2)]
            std_atten = std1[1]
            
        f.write('%s,'%ask_side)
        
        this_comparison = center_comparison[np.mod(trial,
                                                   center_comparison.shape[0])]

        # Just pretend both sides had exactly the same thing. We'll only deal
        # with one anyway:
        f.write('%f,'%(center_contrast + this_comparison))
        f.write('%f,'%(center_contrast))
        
        f.write('%f,'%(center_contrast + this_comparison))
        f.write('%f,'%(center_contrast))
        
        comparison.append(center_contrast + this_comparison)
        # Get stimuli from an actual experiment:
        percept1 = (center_contrast + this_comparison - suppression +
                    np.random.randn() * std_atten)
        percept2 = center_contrast + np.random.randn() * std2 

    
        if percept1>percept2:
            answer.append(1)
        else:
            answer.append(2)

        f.write('%s,'%answer[-1])
        f.write('%s,'%this_comparison)
        f.write('\n')
    f.close()    
    run_analysis(['model_results.csv'])
    

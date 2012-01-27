"""

Post-experiment analysis data from the constant stimuli experiment

"""

from tools import *

path_to_files = './data/'

file_name =  gui.fileOpenDlg(path_to_files)

if len(file_name)>1: 
    for f in file_name:
        fig_name = f.split('/')[-1].split('.')[0] 
        analyze_constant(f, fig_name=fig_name)

else:
    fig_name = file_name.split('/')[-1].split('.')[0] 
    analyze_constant(file_name, fig_name=fig_name)

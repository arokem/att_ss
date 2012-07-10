"""

Post-experiment analysis data from the constant stimuli experiment

"""

from tools import *

def run_analysis(file_name):

    cue_conds = ['cued', 'other']
    if len(file_name)>1: 
        for f in file_name:
            fig_name = f.split('/')[-1].split('.')[0]
            p,l,data_rec = get_data(f)
            if p.has_key('cue_reliability'):
                cue_reliability = p['cue_reliability']
            else:
                cue_reliability = p[' cue_reliability']

            if isinstance(cue_reliability, float):
                for cue in cue_conds:
                    analyze_constant(f, fig_name=fig_name + '_%s'%cue,
                                    cue_cond=cue,
                fit_func='weib')
            else:
                analyze_constant(f, fig_name=fig_name + '_neutral',
                                cue_cond='other',
                fit_func='weib')
                
    else:
        fig_name = file_name[0].split('/')[-1].split('.')[0]
        p,l,data_rec = get_data(file_name[0])
        if p.has_key('cue_reliability'):
            cue_reliability = p['cue_reliability']
        else:
            cue_reliability = p[' cue_reliability']

        if isinstance(cue_reliability, float):
            for cue in cue_conds:
                analyze_constant(file_name[0], fig_name=fig_name + '_%s'%cue,
                                cue_cond=cue,
                    fit_func='weib')
        else:
            print fig_name
            analyze_constant(file_name[0], fig_name= fig_name + '_neutral',
                            cue_cond='other',
                fit_func='weib')

if __name__=="__main__":
    path_to_files = './data/'
    file_name = gui.fileOpenDlg(path_to_files, allowed="CSV files (*.csv)|*.csv")
    run_analysis(file_name)


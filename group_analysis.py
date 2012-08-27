"""

Create input data files for SPSS (subject per line, column per condition) and
for R (row for each subject/condition)

Create figures:

- 12 figures (1 per condition) of average across subjects

- Summary figure of all conditions - psychometric curves with error bars. 

- 4 subplots 1 per orientation: 3 sub-plot per figure (attention effects)

- Ditto per attention condition: 4 curves per figure (ortho/para by
  horizontal/para)

- How to normalize between-subject variability? 

"""

import os 
import numpy as np
import scipy.stats as stats
from scipy.special import erf
import pandas
import matplotlib.pyplot as plt
from matplotlib import rc
from rpy2.robjects import r as rstats

rc('lines', linewidth=2)
rc('font', size=14)

# Import our own analysis stuff
import tools
reload(tools)
from tools import analyze_constant, get_data


def cumgauss(x, mu, sigma):
        """
        The cumulative Gaussian at x, for the distribution with mean mu and
        standard deviation sigma.

        Based on: http://en.wikipedia.org/wiki/Normal_distribution#Cumulative_distribution_function
        """
        return 0.5 * (1 + erf((x-mu)/(np.sqrt(2)*sigma)))

############################
fit_func = 'cumgauss'
############################

path_to_files = '/Users/arokem/Dropbox/att_ss/Analysis/'
dirlist = os.listdir(path_to_files)

cue_conds = ['cued', 'other', 'neutral']

n_subjects = 17
sub_id = ['S%02d'%(i+1) for i in range(n_subjects)]

# Excluding S13 - that's a non-starter :
sub_id = sub_id[:12] + sub_id[13:]

# Excluding S08 - outlier:
sub_id = sub_id[:7] + sub_id[8:]

print sub_id

file_out_R = file('/Users/arokem/Dropbox/att_ss/file4R.csv', 'w')
file_out_R.write('subject,abs_ori,rel_ori,cue,th,sl \n')

df = {}
for this_sub in sub_id:
    print("Analyzing %s"%this_sub)
    df[this_sub] = {(0,0):{}, (0,90):{}, (90,0):{}, (90,90):{}}
    for this_file in dirlist:
        # Only look at files from this subject:
        if this_file.startswith(this_sub):
            print("File: %s"%this_file)
            p,l,d = get_data(path_to_files + this_file)
            # The key differs, depending on the 
            if p.has_key('cue_reliability'):
                cue_reliability = p['cue_reliability']
            else:
                cue_reliability = p[' cue_reliability']
            if isinstance(cue_reliability, float):
                conds = cue_conds[:2]
                for cue in conds:
                    print("Condition: %s"%cue)
                    this = analyze_constant(path_to_files + this_file,
                                            cue_cond=cue, log_scale=False,
			                    fit_func=fit_func)
		    print this['fit'][0]['th']
                    df[this_sub][p[' center_ori'],p[' surr_ori']][cue] = this
                    file_out_R.write('%s,%s,%s,%s,%s,%s\n'%(this_sub,
                                p[' center_ori'],
                                np.abs(p[' center_ori'] - p[' surr_ori']),
                                cue,
                                this['fit'][0]['th'],
                                this['fit'][0]['sl']))
                        

            else:
                print("Condition: neutral")
                # The neutral condition takes "other as input"
                this = analyze_constant(path_to_files + this_file,
                                        cue_cond='other', log_scale=False,
			                fit_func=fit_func)
		print this['fit'][0]['th']
                df[this_sub][p[' center_ori'],p[' surr_ori']]['neutral'] = this
                file_out_R.write('%s,%s,%s,neutral,%s,%s\n'%(this_sub,
                                    p[' center_ori'],
                                    np.abs(p[' center_ori'] - p[' surr_ori']),
                                    this['fit'][0]['th'],
                                    this['fit'][0]['sl']))
                
file_out_R.close()
df = pandas.DataFrame(df)
rstats(
'''
    library(ez)

    # Read the data you just made above:

    data = read.table("/Users/arokem/Dropbox/att_ss/file4R.csv",
                      sep=',',header = TRUE)

    aov_th = ezANOVA(data,
                 wid=.(subject),
                 dv=.(th),
                 within=.(cue, rel_ori, abs_ori),
                 )

    aov_sl = ezANOVA(data,
                 wid=.(subject),
                 dv=.(sl),
                 within=.(cue, rel_ori, abs_ori),
                 )
           '''
)

print("***** ANOVA : THRESHOLDS:*******")
print(rstats.aov_th)

print("***** ANOVA : SLOPES:*******")
print(rstats.aov_sl)


## rstats('''

##  #Read the data you just made above:
##  data = read.table("/Users/arokem/Dropbox/att_ss/file4R.csv",
##                                        sep=',',header = TRUE)

##  aov_th = aov(th ~ (cue*rel_ori*abs_ori) + Error(subject/(cue+rel_ori+abs_ori)),
##  data=data)

##  aov_sl = aov(sl ~ (cue*rel_ori*abs_ori) + Error(subject/(cue+rel_ori+abs_ori)), 
##  data=data)

## attach(data)
##  y = cbind(th, sl)
##  maov = manova(y ~ (cue*rel_ori*abs_ori) + Error(subject/(cue+rel_ori+abs_ori)))

##  ''')
## print("***** ANOVA : THRESHOLDS:*******")
## print(rstats.summary(rstats.aov_th))

## print("***** ANOVA : SLOPES:*******")
## print(rstats.summary(rstats.aov_sl))

## print("***** MANOVA :*******")
## print(rstats.summary(rstats.maov))



file_out_th = file('/Users/arokem/Dropbox/att_ss/file4SPSS_th.csv', 'w')
file_out_sl = file('/Users/arokem/Dropbox/att_ss/file4SPSS_sl.csv', 'w')

# Make the header row:
for file_out in [file_out_th, file_out_sl]:
    file_out.write('subject, ' + ''.join(['%s_%s_%s, '%(i,j,k)
                                 for i in cue_conds
                                 for j in [0,90]
                                 for k in [0,90]]) + '\n')

for sub in df.columns:
    file_out_th.write('%s, '%sub +
                   ''.join(['%s, '%df[sub][i,j][cond]['fit'][0]['th']
                            for cond in cue_conds
                            for i in [0,90]
                            for j in [0,90]
                            ]) + '\n')

    file_out_sl.write('%s, '%sub +
                   ''.join(['%s, '%df[sub][i,j][cond]['fit'][0]['sl']
                            for cond in cue_conds
                            for i in [0,90]
                            for j in [0,90]
                            ]) + '\n')

file_out_th.close()
file_out_sl.close()

colors = dict(cued='b', other='r', neutral='g')

fig = plt.figure()
fig.set_size_inches([15,15])
fig_bar_th = plt.figure()
fig_bar_th.set_size_inches([15,15])
fig_bar_sl = plt.figure()
fig_bar_sl.set_size_inches([15,15])

for ori_idx, ori in enumerate([(0,0),(90,0),(0,90),(90,90)]):
    x = dict(cued=[], other=[], neutral=[])
    y = dict(cued=[], other=[], neutral=[])
    th = dict(cued=[], other=[], neutral=[])
    sl = dict(cued=[], other=[], neutral=[])

    for sub in df.columns:
        for cue_cond in cue_conds: 
            x[cue_cond].append(df[sub][ori][cue_cond]['x'])
            y[cue_cond].append(df[sub][ori][cue_cond]['y'])
            th[cue_cond].append(df[sub][ori][cue_cond]['fit'][0]['th'])
            sl[cue_cond].append(df[sub][ori][cue_cond]['fit'][0]['sl'])

    ax = fig.add_subplot(2,2,ori_idx)
    ax_bar_th = fig_bar_th.add_subplot(2,2,ori_idx)
    ax_bar_sl = fig_bar_sl.add_subplot(2,2,ori_idx)
    ax_bar_sl.set_ylim([0.1,0.8])
    ax.set_title('Center: %s, Surround: %s' %(ori[0] ,ori[1]))
    ax_bar_th.set_title('Center: %s, Surround: %s' %(ori[0] ,ori[1]))
    ax_bar_sl.set_title('Center: %s, Surround: %s' %(ori[0] ,ori[1]))
    ax_bar_th.set_ylim([0.3, 0.8])
    
    for cue_idx, cue_cond in enumerate(cue_conds):
        ax.errorbar(np.mean(x[cue_cond], 0),
                    np.mean(y[cue_cond], 0),
                    yerr=stats.sem(y[cue_cond], 0),
                    ls='None',
                    marker='o',
            color=colors[cue_cond])
        
        x_for_plot = np.linspace(0,1,100)

        psycho = cumgauss(x_for_plot,
                          np.mean(th[cue_cond],0),
                          np.mean(sl[cue_cond],0))

	psycho_lower = []
	psycho_upper = []
	for this_x_for_plot in x_for_plot:
		psycho_lower.append(np.min([cumgauss(this_x_for_plot,
						    np.mean(th[cue_cond]) -
						    stats.sem(th[cue_cond]),
						    np.mean(sl[cue_cond]) +
			                            stats.sem(sl[cue_cond])),
					     cumgauss(this_x_for_plot,
						      np.mean(th[cue_cond]) +
						      stats.sem(th[cue_cond]),
						      np.mean(sl[cue_cond]) -
						     stats.sem(sl[cue_cond]))]))

		psycho_upper.append(np.max([cumgauss(this_x_for_plot,
						    np.mean(th[cue_cond]) -
						    stats.sem(th[cue_cond]),
						    np.mean(sl[cue_cond]) +
			                            stats.sem(sl[cue_cond])),
					     cumgauss(this_x_for_plot,
						      np.mean(th[cue_cond]) +
						      stats.sem(th[cue_cond]),
						      np.mean(sl[cue_cond]) -
						     stats.sem(sl[cue_cond]))]))

    
        ax.plot(x_for_plot, psycho, color=colors[cue_cond])
        ax.set_xlabel('Comparison contrast (%)')
        ax.set_xticks([i for i in np.arange(0,1,0.2)])
        ax.set_xticklabels(['%s'%(i*100) for i in np.arange(0,1,0.2)])
        ax.set_ylabel('Proportion responses "comparison higher"')
        ax.set_yticks([i for i in np.arange(0,1,0.2)])
        ax.set_yticklabels(['%s'%(i*100) for i in np.arange(0,1,0.2)])
        ax.set_ylim([0,1])
        
        
        ax.fill_between(x_for_plot, psycho_lower, psycho_upper,
                        color=colors[cue_cond], alpha=0.2)
	ax.plot([0.3,0.3], [0,100], 'k--')
        
        ax.errorbar(np.mean(th[cue_cond]),
                    0.5,
                    xerr=stats.sem(th[cue_cond]),
            color=colors[cue_cond])

        ax_bar_th.bar(cue_idx,
                   np.mean(th[cue_cond],0),
                   color=colors[cue_cond])

        ax_bar_th.errorbar(cue_idx + 0.4,
                        np.mean(th[cue_cond],0),
                        yerr=stats.sem(th[cue_cond],0),
                        color='k')

        ax_bar_sl.bar(cue_idx,
                   np.mean(sl[cue_cond],0),
                   color=colors[cue_cond])

        ax_bar_sl.errorbar(cue_idx + 0.4,
                        np.mean(sl[cue_cond],0),
                        yerr=stats.sem(sl[cue_cond],0),
                        color='k')

fig.savefig(path_to_files + 'figures/psycho_curves_wo8.png')
fig_bar_th.savefig(path_to_files + 'figures/thresholds_wo8.png')
fig_bar_sl.savefig(path_to_files + 'figures/slopes_wo8.png')


x = {(0,0):dict(cued=[], other=[], neutral=[]),
     (0,90):dict(cued=[], other=[], neutral=[]),
     (90,0):dict(cued=[], other=[], neutral=[]),
     (90,90):dict(cued=[], other=[], neutral=[])}
     
y = {(0,0):dict(cued=[], other=[], neutral=[]),
     (0,90):dict(cued=[], other=[], neutral=[]),
     (90,0):dict(cued=[], other=[], neutral=[]),
     (90,90):dict(cued=[], other=[], neutral=[])}
     
th = {(0,0):dict(cued=[], other=[], neutral=[]),
     (0,90):dict(cued=[], other=[], neutral=[]),
     (90,0):dict(cued=[], other=[], neutral=[]),
     (90,90):dict(cued=[], other=[], neutral=[])}

sl = {(0,0):dict(cued=[], other=[], neutral=[]),
     (0,90):dict(cued=[], other=[], neutral=[]),
     (90,0):dict(cued=[], other=[], neutral=[]),
     (90,90):dict(cued=[], other=[], neutral=[])}

th_ub = {(0,0):dict(cued=[], other=[], neutral=[]),
     (0,90):dict(cued=[], other=[], neutral=[]),
     (90,0):dict(cued=[], other=[], neutral=[]),
     (90,90):dict(cued=[], other=[], neutral=[])}

th_lb = {(0,0):dict(cued=[], other=[], neutral=[]),
     (0,90):dict(cued=[], other=[], neutral=[]),
     (90,0):dict(cued=[], other=[], neutral=[]),
     (90,90):dict(cued=[], other=[], neutral=[])}

sl_ub = {(0,0):dict(cued=[], other=[], neutral=[]),
     (0,90):dict(cued=[], other=[], neutral=[]),
     (90,0):dict(cued=[], other=[], neutral=[]),
     (90,90):dict(cued=[], other=[], neutral=[])}

sl_lb = {(0,0):dict(cued=[], other=[], neutral=[]),
     (0,90):dict(cued=[], other=[], neutral=[]),
     (90,0):dict(cued=[], other=[], neutral=[]),
     (90,90):dict(cued=[], other=[], neutral=[])}


for cond_idx, cue_cond in enumerate(cue_conds):
    for sub in df.columns:
        for ori in df.index:
            x[ori][cue_cond].append(df[sub][ori][cue_cond]['x'])
            y[ori][cue_cond].append(df[sub][ori][cue_cond]['y'])
            th[ori][cue_cond].append(df[sub][ori][cue_cond]['fit'][0]['th'])
            sl[ori][cue_cond].append(df[sub][ori][cue_cond]['fit'][0]['sl'])
            th_ub[ori][cue_cond].append(df[sub][ori][cue_cond]['boot_th_ub'])
            th_lb[ori][cue_cond].append(df[sub][ori][cue_cond]['boot_th_lb'])
            sl_ub[ori][cue_cond].append(df[sub][ori][cue_cond]['boot_sl_ub'])
            sl_lb[ori][cue_cond].append(df[sub][ori][cue_cond]['boot_sl_lb'])
            

for this,fig_name in zip([th, sl],['threshold', 'slope']):
    ss_90_cued = (np.array(this[90,90]['cued'])-np.array(this[90,0]['cued'])/
                 np.array(this[90,90]['cued'])+np.array(this[90,0]['cued']))

    ss_0_cued = (np.array(this[0,0]['cued'])-np.array(this[0,90]['cued'])/
                 np.array(this[0,0]['cued'])+np.array(this[0,90]['cued']))

    ss_90_other = (np.array(this[90,90]['other'])-np.array(this[90,0]['other'])/
                 np.array(this[90,90]['other'])+np.array(this[90,0]['other']))

    ss_0_other = (np.array(this[0,0]['other'])-np.array(this[0,90]['other'])/
                 np.array(this[0,0]['other'])+np.array(this[0,90]['other']))

    ss_90_neut=(np.array(this[90,90]['neutral'])-np.array(this[90,0]['neutral'])/
                np.array(this[90,90]['neutral'])+np.array(this[90,0]['neutral']))

    ss_0_neut=(np.array(this[0,0]['neutral'])-np.array(this[0,90]['neutral'])/
               np.array(this[0,0]['neutral'])+np.array(this[0,90]['neutral']))

    fig = plt.figure()
    fig.set_size_inches([10,8])
    ax = fig.add_subplot(1,1,1)
    xx = np.array([1,2,3,4,5,6])
    ax.bar(xx,
           [np.mean(ss_90_cued),
            np.mean(ss_90_neut),
            np.mean(ss_90_other),
            np.mean(ss_0_cued),
            np.mean(ss_0_neut),
            np.mean(ss_0_other)],
            yerr=[stats.sem(ss_90_cued),
            stats.sem(ss_90_neut),
            stats.sem(ss_90_other),
            stats.sem(ss_0_cued),
            stats.sem(ss_0_neut),
            stats.sem(ss_0_other)],
           )

    ax.set_xticks(xx + 0.4)
    ax.set_xticklabels(['90/cued',
                         '90/neutral',
                         '90/uncued',
                         '0/cued',
                         '0/neutral',
                         '0/uncued'])
    ax.set_ylabel('%s(para) - %s(ortho)/%s(para) + %s(ortho)'%(
        fig_name,fig_name,fig_name,fig_name))
    fig.savefig(path_to_files + 'figures/%s_ss_wo8.png'%fig_name)



fig = plt.figure()
fig.set_size_inches([15,10])
for ori_idx, oris in enumerate([[(0,90),(0,0)],[(90,0),(90,90)]]):
    for cue_idx, cue_cond in enumerate(['cued','neutral','other']):
        ax = fig.add_subplot(2,3, (ori_idx*3) + (cue_idx+1)) 

        plot_x = th[oris[0]][cue_cond]
        plot_y = th[oris[1]][cue_cond]
        err_x = (np.array(th_ub[oris[0]][cue_cond])-
                 np.array(th_lb[oris[1]][cue_cond])).squeeze()

        err_y = (np.array(th_ub[oris[0]][cue_cond])-
                 np.array(th_lb[oris[1]][cue_cond])).squeeze()

            #err_x = sl[oris[0]][cue_cond]
            #err_y = sl[oris[1]][cue_cond]
        
        ax.errorbar(plot_x, plot_y, xerr = err_x, yerr=err_y,
                    linestyle='None', marker='o',color=colors[cue_cond])
        ax.errorbar(np.mean(plot_x), np.mean(plot_y),
                    xerr = stats.sem(plot_x),
                    yerr=stats.sem(plot_y), marker='o', color='k', markersize=10)

        ax.plot([0,1],[0,1],'k--')
        ax.set_xlim([0,1])
        ax.set_ylim([0,1])
        ax.set_title('%s, %s'%(cue_cond,oris[0][0]))
        ax.set_ylabel('Orthogonal')
        ax.set_xlabel('Parallel')
                    
        
fig.savefig(path_to_files + 'figures/scatter_th_wo8.png')

fig = plt.figure()
fig.set_size_inches([15,10])
for ori_idx, oris in enumerate([[(0,90),(0,0)],[(90,0),(90,90)]]):
    for cue_idx, cue_cond in enumerate(['cued','neutral','other']):
        ax = fig.add_subplot(2,3, (ori_idx*3) + (cue_idx+1)) 

        plot_x = sl[oris[0]][cue_cond]
        plot_y = sl[oris[1]][cue_cond]
        err_x = (np.array(sl_ub[oris[0]][cue_cond])-
                 np.array(sl_lb[oris[1]][cue_cond])).squeeze()

        err_y = (np.array(sl_ub[oris[0]][cue_cond])-
                 np.array(sl_lb[oris[1]][cue_cond])).squeeze()

            #err_x = 0# sl[oris[0]][cue_cond]
            #err_y = 0#sl[oris[1]][cue_cond]
        
        ax.errorbar(plot_x, plot_y, xerr = err_x, yerr=err_y,
                    linestyle='None', marker='o',color=colors[cue_cond])
        ax.errorbar(np.mean(plot_x), np.mean(plot_y),
                    xerr = stats.sem(plot_x),
                    yerr=stats.sem(plot_y), marker='o', color='k', markersize=10)

        ax.plot([0,1],[0,1],'k--')
        ax.set_xlim([0,1])
        ax.set_ylim([0,1])
        ax.set_title('%s, %s'%(cue_cond,oris[0][0]))
        ax.set_ylabel('Orthogonal')
        ax.set_xlabel('Parallel')
                    
        
fig.savefig(path_to_files + 'figures/scatter_sl_wo8.png')

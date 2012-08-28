import pandas
import os 
import numpy as np
import tools

n_params_dict = dict(cumgauss=2,
		     cummgauss_w_asym=4,
	             weibull=4)

def get_df(n_subjects,
	   path_to_files='/Users/arokem/Dropbox/att_ss/Analysis/',
	   file4R='/Users/arokem/Dropbox/att_ss/file4R.csv',
	   fit_func='cumgauss',
	   boots=1,
	   exclude=None,
	   verbose=True,
	   cue_conds=['cued', 'other', 'neutral']):

	n_params = n_params_dict[fit_func]
	dirlist = os.listdir(path_to_files)

	sub_id = ['S%02d'%(i+1) for i in range(n_subjects)]

	if exclude is not None:
            # Make sure to exclude from the largest to smallest:
 	    exclude = np.sort(exclude)[::-1]
	    for ex in exclude:
		sub_id = sub_id[:ex-1] + sub_id[ex:]

	if verbose:
		print sub_id

	file_out_R = file(file4R, 'w')
	file_out_R.write('subject,abs_ori,rel_ori,cue')
	for para in range(n_params):
		file_out_R.write(',p%i'%(para+1))
	file_out_R.write('\n')

	df = {}
	surr_k = ' surr_ori'
	center_k = ' center_ori'
	for this_sub in sub_id:
	    if verbose:
		    print("Analyzing %s"%this_sub)
	    df[this_sub] = {(0,0):{}, (0,90):{}, (90,0):{}, (90,90):{}}
	    for this_file in dirlist:
		# Only look at files from this subject:
		if this_file.startswith(this_sub):
		    if verbose:
			    print("File: %s"%this_file)
		    p,l,d = tools.get_data(path_to_files + this_file)
		    # The key differs, depending on the 
		    if p.has_key('cue_reliability'):
			cue_reliability = p['cue_reliability']
		    else:
			cue_reliability = p[' cue_reliability']
		    if isinstance(cue_reliability, float):
			conds = cue_conds[:2]
			for cue in conds:
			    if verbose: 
				    print("Condition: %s"%cue)
			    this=tools.analyze_constant(path_to_files+this_file,
							cue_cond=cue,
							log_scale=False,
							fit_func=fit_func,
							boot=boots,
						        verbose=verbose)

			    df[this_sub][p[center_k],p[surr_k]][cue]=this
			    file_out_R.write('%s,%s,%s,%s'%(this_sub,
					p[center_k],
				np.abs(p[center_k] - p[surr_k]),
					cue))
			    for para in this['fit'][0]:
				    file_out_R.write(',%s'%para)
			    file_out_R.write('\n')

		    else:
			if verbose:
				print("Condition: neutral")

			# The neutral condition takes "other" as input:
			this = tools.analyze_constant(path_to_files + this_file,
						      cue_cond='other',
						      log_scale=False,
						      fit_func=fit_func,
						      boot=boots,
				                      verbose=verbose)
			
			df[this_sub][p[center_k],p[surr_k]]['neutral']=this
			file_out_R.write('%s,%s,%s,neutral'%(this_sub,
					    p[center_k],
				np.abs(p[center_k] - p[surr_k])))
			for para in this['fit'][0]:
				file_out_R.write(',%s'%para)
			file_out_R.write('\n')

	file_out_R.close()
	return pandas.DataFrame(df)

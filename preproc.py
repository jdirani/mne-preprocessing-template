# J.Dirani - 7 February 2018

#always double check all the steps before using this template
#especially for the photodiode and logs rejection (need to be edited)
# edit covariance part accordingly


# ----------File structure-----------#
# ROOT>
#     MRI>
#         subjs
#     MEG>
#         subjs
#     STC>


import mne, eelbrain, os, glob, pickle
import numpy as np
import pandas as pd
%gui qt

#=========Edit here=========#
expt= 'TwoTones' #experiment name as written on the raw.fif
ROOT = '/Users/my_user/data_file/'
os.chdir(ROOT)
subjects_dir = ROOT+'MRI/'
subjects = ['A0176', 'A0192', 'A0216'] #list of subjs
event_id = dict(hi=223, lo=191)
#===========================#

'''==========================================================================='''
'''                           PART 1: Filter, bads, ICA                       '''
'''==========================================================================='''

# ------------------ Check which subj dont have ICA files --------------------- #
#Looks for a ..._ICA-raw.fif file. Post ICA+filtered data must be named accordingly
No_ica=[]
for subj in subjects:
    if os.path.isfile('MEG/%s/%s_%s_ICA-raw.fif'%(subj, subj, expt)):
        print 'ICA and filtering already done for subj=%s'%subj
    else:
        No_ica.append(subj)
print ">> ICA not done for %s (%s)" %(No_ica, len(No_ica))


# ----------------------------------- ICA ------------------------------------ #
# compute and save ICA
for subj in subjects:
    print subj
    if not os.path.isfile('MEG/%s/%s-ica.fif'%(subj,subj)):
        random.seed(42) #something to do with starting at the same spot for all subjects
        print 'importing raw...'
        raw = mne.io.read_raw_fif('MEG/%s/%s_%s-raw.fif' %(subj, subj, expt), preload=True)
        raw.filter(0,40, method='iir')
        ica = mne.preprocessing.ICA(n_components=0.95, method='fastica')
        print 'fitting ica...'
        # reject = dict(mag=2e-12) # Use this in ica.fit if too mnoisy
        ica.fit(raw) #reject=reject
        ica.save('MEG/%s/%s-ica.fif'%(subj,subj))
        del raw, ica

# Plot to make rejections
for subj in subjects:
    print subj
    if not os.path.isfile('MEG/%s/%s_%s_ICA-raw.fif' %(subj,subj, expt)):
        raw = mne.io.read_raw_fif('MEG/%s/%s_%s-raw.fif' %(subj, subj, expt), preload=True)
        raw.filter(0,40, method='iir')
        ica = mne.preprocessing.read_ica('MEG/%s/%s-ica.fif'%(subj,subj))
        ica.plot_sources(raw)
        raw_input('Press enter to continue')
        print 'Saving...'
        raw = ica.apply (raw, exclude=ica.exclude)
        raw.save('MEG/%s/%s_%s_ICA-raw.fif' %(subj,subj, expt))
        print 'Saving...'
        del raw, ica


        

'''==========================================================================='''
'''                             PART 2: get epochs                            '''
'''==========================================================================='''

for subj in subjects:
    print '>>  Getting epochs: subj=%s'%subj
    if os.path.isfile('MEG/%s/epochs' %subj):
        print '>> EPOCHS ALREADY CREATED FOR SUBJ=%s'%subj
    else:
        print "%s: Importing filtered+ICA data" %subj
        raw = mne.io.read_raw_fif('MEG/%s/%s_%s_ICA-raw.fif' %(subj, subj, expt), preload=True)
        #-----------------------------Find events------------------------------#
        print "%s: Finding events..." %subj
        events = mne.find_events(raw,min_duration=0.002)
        picks_meg = mne.pick_types(raw.info, meg=True, eeg=False, eog=True, stim=False)

        #-----------------------Fix photodiode shift---------------------------#
        # #This part looks for the average photodiode delay and aligns events accordingly
        # #For details, see comments in script in NYU Google Drive:
        # #/NYU/Z-Mehods\ library/Meg_data_analysis/Miscphotodiode_average_delay.py
        # print "Fixing photodiode delay..."
        # photodiode = mne.find_events(raw,stim_channel='MISC 010',min_duration=0.005)
        #
        # def find_the_first_real_photodiode():
        #     first_event=events[0][0]
        #     for i in range(len(photodiode)):
        #         shift = photodiode[i][0]-first_event
        #         if abs(shift) < 60:
        #             return i
        #
        # real_diode = find_the_first_real_photodiode()
        # diode_times=[] #first 800 real photodiode times
        # for t in range(real_diode,real_diode+20): #first 20 real photodiode firings.
        #     diode_times.append(photodiode[t][0])
        #
        # diode_shifts=[] #The first 20 photodiode shifts
        # for i in range(len(diode_times)):
        #     shft=diode_times[i]-events[i][0]
        #     diode_shifts.append(shft)
        # #Compute average and SD
        # average_shift=np.average(diode_shifts)
        # std_shift=np.std(diode_shifts)
        # #Shift events accordingly
        # for i in range(len(events)):
        #     events[i][0]+= abs(average_shift)
        #
        # print 'Average photodiode delay = ', average_shift
        # print 'SD photodiode delay = ', std_shift
        # raw_input('Press Enter if values look OK: ')
        #
        # del photodiode, real_diode, diode_times, diode_shifts, average_shift, std_shift

        #----------------------Reject epochs based on logs---------------------#
        # print "Rejecting epochs based on logs"
        # ogfile='MEG/%s/initial_output/%s_log_mask.csv' %(subj,subj)
        # log=pd.read_csv(logfile)
        # log['ep_mask']=np.where(log['mask']==1, True, False)
        #
        epochs = mne.Epochs(raw, events, event_id=event_id, tmin=-0.1, tmax=0.6, baseline=(None,0), picks=picks_meg, decim=5, preload=True)
        #
        # epochs_hits=epochs[log.ep_mask]
        # del log

        #----------------------Manual epochs rejection-------------------------#
        print ">> Epochs rejection for subj=%s" %subj
        if os.path.isfile('MEG/%s/%s_rejfile.pickled' %(subj, subj)):
            print 'Rejections file for %s exists, loading file...' %(subj)
            rejfile = eelbrain.load.unpickle('MEG/%s/%s_rejfile.pickled' %(subj, subj))
            rejs = rejfile['accept'].x
            epochs_rej=epochs[rejs]
            print 'Done.'
        else:
            print 'Rejections file for %s does not exist, opening GUI...' %(subj)
            eelbrain.gui.select_epochs(epochs, vlim=2e-12, mark=['MEG 087','MEG 130'])
            raw_input('NOTE: Save as MEG/subj/subj_rejfile.pickled. \nPress enter when you are done rejecting epochs in the GUI...')
            rejfile = eelbrain.load.unpickle('MEG/%s/%s_rejfile.pickled' %(subj, subj))
            rejs = rejfile['accept'].x
            epochs_rej=epochs[rejs]
        print '%s: epochs_rej created' %subj


        #------------------Save raw.info and epochs to file-------------------#
        print 'Saving epochs to file...'
        info = raw.info
        pickle.dump(info, open('MEG/%s/%s-info.pickled' %(subj,subj), 'wb'))

        if not os.path.isfile('MEG/%s/%s-epo.fif'%(subj,subj)):
            epochs_rej.save('MEG/%s/%s-epo.fif' %(subj,subj))
        del raw
        print 'Done.'



'''==========================================================================='''
'''                             PART 3: Create STCs                           '''
'''==========================================================================='''
for subj in subjects:
    if os.path.exists('STC/%s'%subj):
        print 'STCs ALREADY CREATED FOR SUBJ = %s' %subj
    else:
        print ">> STCs for subj=%s:"%subj
        print 'Importing data...'
        info = pickle.load(open('MEG/%s/%s-info.pickled' %(subj,subj), 'rb'))
        epochs_rej = mne.read_epochs('MEG/%s/%s-epo.fif' %(subj,subj))
        trans = mne.read_trans('MEG/%s/%s-trans.fif' %(subj,subj))
        bem = glob.glob('MRI/%s/bem/*-bem-sol.fif' %subj)[0]


    #---------------------------get evoked------------------------------------#
        print '%s: Creating evoked responses' %subj
        evoked = []
        conditions = event_id.keys()
        for cond in conditions:
            evoked.append(epochs_rej[cond].average())
        print 'Done.'


        #----------------------Source space---------------------------#
        print 'Generating source space...'
        if os.path.isfile('MRI/%s/bem/%s-ico-4-src.fif' %(subj,subj)):
            print 'src for subj = %s already exists, loading file...' %subj
            src = mne.read_source_spaces(fname='MRI/%s/bem/%s-ico-4-src.fif' %(subj,subj))
            print 'Done.'
        else:
            print 'src for subj = %s does not exist, creating file...' %subj
            src = mne.setup_source_space(subject=subj, spacing='ico4', subjects_dir=subjects_dir)
            src.save('MRI/%s/bem/%s-ico-4-src.fif' %(subj,subj))
            print 'Done. File saved.'


        #--------------------Forward solution-------------------------#
        print 'Creating forward solution...'
        if os.path.isfile('MEG/%s/%s-fwd.fif' %(subj, subj)):
            print 'forward soltion for subj=%s exists, loading file.' %subj
            fwd = mne.read_forward_solution('MEG/%s/%s-fwd.fif' %(subj, subj), force_fixed = False)
            print 'Done.'
        else:
            print 'forward soltion for subj=%s does not exist, creating file.' %subj
            fwd = mne.make_forward_solution(info=info, trans=trans, src=src, bem=bem, ignore_ref=True) #?????? DOUBLE CHECK THIS
            mne.write_forward_solution('MEG/%s/%s-fwd.fif' %(subj, subj), fwd)
            print 'Done. File saved.'


        #----------------------Covariance------------------------------#
        print 'Getting covariance'
        if os.path.isfile('MEG/%s/%s-cov.fif' %(subj,subj)):
            print 'cov for subj=%s exists, loading file...' %subj
            cov=mne.read_cov('MEG/%s/%s-cov.fif' %(subj,subj))
            print 'Done.'
        else:
            print 'cov for subj=%s does not exist, creating file...' %subj
            cov = mne.compute_covariance(epochs_rej,tmin=None,tmax=0, method=['shrunk', 'diagonal_fixed', 'empirical'])
            cov.save('MEG/%s/%s-cov.fif' %(subj,subj))
            print 'Done. File saved.'


        #---------------------Inverse operator-------------------------#
        print 'Getting inverse operator'
        inv = mne.minimum_norm.make_inverse_operator(info, fwd, cov, depth=None, loose= None, fixed=False) #fixed=False: Ignoring dipole direction.
        SNR = 3 # SNR = 3 for evoked, 2 for epochs
        lambda2 = 1.0 / 3.0 ** SNR

        #--------------------------STCs--------------------------------#

        print '%s: Creating STCs...'%subj
        os.makedirs('STC/%s' %subj)
        for ev in evoked:
            #ev.crop(0,0.7) if need to crop
            stc = mne.minimum_norm.apply_inverse(ev, inv, lambda2=lambda2, method='dSPM')
            #mophing stcs to the fsaverage:
            vertices_to = mne.grade_to_vertices('fsaverage', grade=4, subjects_dir=subjects_dir) #fsaverage's source space
            stc_morph = mne.morph_data(subject_from=subj, subject_to='fsaverage',stc_from=stc, grade=vertices_to,subjects_dir=subjects_dir)
            stc_morph.save('STC/%s/%s_%s_dSPM' %(subj,subj,ev.comment))
            del stc, stc_morph
        print '>> DONE CREATING STCS FOR SUBJ=%s'%subj
        print '-----------------------------------------\n'

        #deleting variables
        del epochs_rej, evoked, info, trans, bem, src, fwd, cov, inv

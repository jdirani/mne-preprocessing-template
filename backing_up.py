import os
from shutil import copy, copytree
from os.path import join

source_dir = '/Users/julien/input_dir/'
out_dir = 'Users/julien/output_dir/'

subjects = [i for i in os.listdir(source_dir) if 'A0' in i]

for subj in subjects:
    print subj
    subj_out_dir = join(out_dir, subj)
    if not os.path.isdir(subj_out_dir):
        os.mkdir(subj_out_dir)

    trans_fname = join(source_dir, subj, '%s-trans.fif' %subj)
    rejfile_fname = join(source_dir, subj, '%s_rejfile.pickled' %subj)
    epo_fname = join(source_dir, subj, '%s-epo.fif' %subj)
    ica_fname = join(source_dir, subj, '%s-ica.fif' %subj)
    RT_fname = join(source_dir, subj, '%s_RT_logfile.csv' %subj)
    singletrial_logfile_fname = join(source_dir, subj, '%s_logfile_SingleTrialSTC.csv' %subj)
    info_dir = join(source_dir, subj, 'info')
    raw_info = join(source_dir, subj, '%s-info.pickled' %subj)
    raw_fif_cleaned = join(source_dir, subj, '%s_Porthal_ICA-raw.fif' %subj)

    if os.path.isfile(trans_fname):
        copy(trans_fname, subj_out_dir)

    if os.path.isfile(rejfile_fname):
        copy(rejfile_fname, subj_out_dir)

    if os.path.isfile(epo_fname):
        copy(epo_fname, subj_out_dir)

    if os.path.isfile(ica_fname):
        copy(ica_fname, subj_out_dir)

    if os.path.isfile(RT_fname):
        copy(RT_fname, subj_out_dir)

    if os.path.isfile(singletrial_logfile_fname):
        copy(singletrial_logfile_fname, subj_out_dir)

    if os.path.isdir(info_dir) &  (not os.path.isdir(join(subj_out_dir,'info'))):
        copytree(info_dir, join(subj_out_dir,'info'))

    if os.path.isfile(raw_info):
        copy(raw_info, subj_out_dir)

    if os.path.isfile(raw_fif_cleaned):
        copy(raw_fif_cleaned, subj_out_dir)

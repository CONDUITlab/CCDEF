"""
Convert MIMIC III data to CCDEF (hdf5 based)
"""
import numpy as np
import pandas as pd
import psycopg2 
#import sqlite3
import h5py
import json
import wfdb
from ccdef._utils import df_to_sarray

def open_db():
    schema = 'mimiciii'
    con = psycopg2.connect(dbname='mimic', user='queryuser', host='10.100.3.150', password='conduit')
    cur = con.cursor()
    cur.execute('SET search_path to {}'.format(schema))
    
    return (con)

def patient_id_from_file(filename):
    return (filename.split('/')[-1].split('-')[0][1:].strip("0"))

def extract_notes(infile):
    """
    extract_notes(infile)

    Take all notes in the mimic3 db for infile
    
    TODO: Will need to build option to include only labs/notes in the period where there is waveform/numeric data
    but for now we include everything so it is available for context (eg echo reports)

    Parameters
    ----------

    infile: string
        filename of a wfdb file from the MIMIC3 matched dataset
    origin: datetime
        the base datetime for the file

    return: notes
        DataFrame containing notes, times, etc
    """

    # get patient ID
    subj_id = patient_id_from_file(infile)
    
    #get lab_events for this patient
    con = open_db()
    
    query = \
    """
    SELECT i.chartdate, i.charttime, i.description, i.category, i.text
    FROM noteevents i
    WHERE subject_id = {};
    """.format(subj_id)

    notes = pd.read_sql_query(query,con)
    """ change time stamp to seconds from origin """
    
    origin = pd.to_datetime(wfdb.rdheader(infile).base_datetime)
    notes.insert(0, 'time', '')
    for idx, row in notes.iterrows():
        notes['time'].iloc[idx]=int((pd.to_datetime(row['charttime'])-origin).total_seconds())
    del notes['charttime']
    del notes['chartdate']

    return (notes)

def write_notes(notes_df, outfile):
    """
    write_notes(notes_df, infile)

    Write notes from notes_df to infile    

    Parameters
    ----------

    infile: string
        filename of a wfdb file from the MIMIC3 matched dataset

    notes_df: notes
        DataFrame containing notes, times, etc
    """
    
    arr, saType = df_to_sarray(notes_df)
    
    with h5py.File(outfile, 'a') as f:
        clin = f.require_group('/clinical')
        note_ds = f.create_dataset('clinical/notes', maxshape = (None, ), data = arr, dtype = saType,
                                 compression="gzip", compression_opts = 9, shuffle = True)
        
        
def extract_labs(infile):
    """
    extract_labs(infile)

    Take all lab values in the mimic3 db for infile
    
    TODO: Will need to build option to include only labs/notes in the period where there is waveform/numeric data
    but for now we include everything so it is available for context (eg echo reports)

    Parameters
    ----------

    infile: string
        filename of a wfdb file from the MIMIC3 matched dataset
    origin: datetime
        the base datetime for the file

    return: notes
        DataFrame containing notes, times, etc
    """

    # get patient ID
    subj_id = patient_id_from_file(infile)

    #get basetime
    origin = wfdb.rdheader(infile).base_datetime
    
    #get lab_events for this patient
    con = open_db()
    
    query = \
    """
    SELECT e.charttime, e.itemid, e.value, e.valuenum, e.valueuom, e.flag,
        i.label, i.fluid, i.category, i.loinc_code
    FROM labevents e
    INNER JOIN d_labitems i
    ON e.itemid = i.itemid
    WHERE subject_id = {};
    """.format(subj_id)
    labs = pd.read_sql_query(query,con)

    #convert time
    origin = pd.to_datetime(wfdb.rdheader(infile).base_datetime)
    labs.insert(0, 'time', '')

    for idx, row in labs.iterrows():
        labs['time'].iloc[idx]=int((pd.to_datetime(row['charttime'])-origin).total_seconds())
    del labs['charttime']

    return (labs)

def write_labs(labs_df, outfile):

    # TODO: convert flag to category and encode in .flag_info
    arr, saType = df_to_sarray(labs_df)


 #   dt = h5py.special_dtype(vlen=str)
 #   comp_type = np.dtype([('time', dt), ('testid', 'i8'), ('value', dt), ('valuenum', 'f8'), ('flag', dt)])
    # define array for writing to dataset
#    arr_data = np.empty((0,), dtype=comp_type)
#    for idx, row in labs_df.iterrows():
#        arr = np.array([(str(row['charttime']), row['itemid'], row['value'], row['valuenum'], row['flag'])], 
#                  dtype = comp_type)
#        arr_data = np.append(arr_data, arr)
        
        
    #create metadata
    labs_grouped = labs_df.groupby('itemid')['itemid','label','category','fluid','valueuom','loinc_code'].first()
    labs_grouped = labs_grouped.set_index('itemid')
    test_info = labs_grouped.T.to_dict('dict')
    
    with h5py.File(outfile, 'a') as f:
        clin = f.require_group('/clinical')
        lab_ds = f.create_dataset('clinical/labs', maxshape = (None, ), data = arr, dtype=saType,
                                 compression="gzip", compression_opts = 9, shuffle = True)
        lab_ds.attrs['.test_info'] = json.dumps(test_info) 
        
def labs_to_df (dset):
    # extract values from dataset and convert to dataframe
    
    # load metadata
    tests_dict = json.loads(dset.attrs['.test_info'])
    info_df = pd.DataFrame.from_dict(tests_dict, orient='columns').T

    # create column for merge
    info_df['testid'] = info_df.index.astype(int)
    
    #load labs
    labs_df = pd.DataFrame(dset[:])
    
    #merge
    
    df = pd.merge(labs_df, info_df, on = 'testid')
    
    return (df)

def get_admissions(subj_id):
    con = open_db()
    
    query = \
    """
    SELECT *
    FROM admissions
    WHERE subject_id = {};
    """.format(subj_id)

    admits = pd.read_sql_query(query,con) 
    return (admits)

def find_admission (filename):
    '''
    Get admission information from MIMIC III filename (contains subj ID)
    Return demographic information
    '''
    subj_id = 0
    hadm_id = 0
    diagnosis = ''
    expired = ''
    death_time = ''
    ethnicity = ''
    
    subj_id = patient_id_from_file(filename)
    print('searching {}'.format(subj_id))
    
    # get additional demographics
    con = open_db()
    query = \
    """
    SELECT i.subject_id, i.gender, i.dob 
    FROM patients i
    WHERE subject_id = {};
    """.format(subj_id)

    demo = pd.read_sql_query(query,con)
    gender = demo.gender.values[0]
    dob = demo.dob.values[0]
    
    record = wfdb.rdheader(filename)
    sig_start = record.base_datetime
    print('Signal file start {}'.format(sig_start))

    admits = get_admissions(subj_id)
    
    for idx, row in admits.iterrows():
        adm_time = row['admittime']
        dsc_time = row['dischtime']

        print('Admission # {}, in at {} out at {}'.format(row['hadm_id'], adm_time, dsc_time))

        if (sig_start > adm_time) and (sig_start < dsc_time):
            print ('Subject {}, record {}, diagnosis: {}. HADM {} '.format(row['subject_id'], 
                record.record_name, row['diagnosis'], row['hadm_id']))
            hadm_id = row['hadm_id']
            diagnosis = row['diagnosis']
            expired = row['hospital_expire_flag']
            death_time = row['deathtime']
            ethnicity = row['ethnicity']
            age = round( pd.to_timedelta(adm_time-dob)/pd.to_timedelta(365,unit='d'))
            
            
    return(subj_id, hadm_id, age, gender, ethnicity, diagnosis, expired, death_time)
            
def get_diagnoses(hadm_id):
    # get all diagnoses for the admission
    # return as dict including short and long titles
    
    con = open_db()

    query = \
    """
    SELECT h.icd9_code,
        d.icd9_code, d.short_title, d.long_title
    FROM diagnoses_icd h
    INNER JOIN d_icd_diagnoses d
    ON d.icd9_code = h.icd9_code
    WHERE hadm_id = {};
    """.format(hadm_id)

    dx_dict = pd.read_sql_query(query,con).T.to_dict('dict')
    return (dx_dict)

def convert_mimic_matched (filename, samp_end = None, all_labs=True, all_notes=True):
    ''' 
    TODO:
    time filter
    additional demographics
    
    mapping function
    '''
    # all_labs - include labs from outside the time range of the specified signal file
    # all_notes - include labs from outside the time range of the specified signal file

    # samp_end - to limit size of datafile for testing, default = None
    
    # use base file, pull numerics

    if filename[-1] != 'n':
        print('Base is waveform file, add numerics')
    else:
        print('Base is numerics file, change basename to waveform and then process numerics')
        filename = filename[:-1]
    
    # generate output filename
    
    outfile = 'mimic_test.h5'
    
    # read header
    record = wfdb.rdheader(filename)
    
#    meta_head = wfdb_head_meta(filename)
    
    with h5py.File(outfile, 'w') as f:
#        meta = f.require_group('.meta')
#        meta.attrs['data'] = json.dumps(meta_head, indent = 4)
#        meta.attrs['mapping'] = json.dumps('Placeholder', indent = 4)
        
        
        grp_numerics = f.require_group('numerics')
        print('Converting numerics')
        record = wfdb.rdrecord(filename+'n', sampfrom = 0, sampto = samp_end )
        df = pd.DataFrame(data = record.p_signal, columns = record.sig_name)
        ds_num = grp_numerics.create_dataset('vitals', maxshape = (None,), data = df.to_records(index=False),
                                 compression="gzip", compression_opts=9, shuffle = True)
        
        grp_waveforms = f.require_group('/waveforms')
        print('Converting waveforms')
        record = wfdb.rdrecord(filename, sampfrom = 0, sampto = samp_end )
        df = pd.DataFrame(data = record.p_signal, columns = record.sig_name)
        ds_wave = grp_waveforms.create_dataset('hemodynamics', maxshape = (None,), data = df.to_records(index=False),
                                 compression="gzip", compression_opts=9, shuffle = True)
        
        grp_clinical = f.require_group('/clinical')

        #demographics

        print('Locating admission')
        (subj_id, hadm_id, age, gender, ethnicity, diagnosis, expired, death_time) = find_admission(filename)

        demographics = {
            'Age' : age,
            'Ethnicity' : ethnicity,
            'Gender'    : gender,
            'Expired'   : expired,
            'Death_time': death_time
        }
        
        grp_clinical.attrs['demographics'] = json.dumps(demographics, indent = 4)
        grp_clinical.attrs['admit_diagnosis'] = json.dumps(diagnosis)  # add additional codes from dianosis table
        
        #get additional diagnoses - save as dict
        dx_list = get_diagnoses(hadm_id)
        grp_clinical.attrs['diagnoses'] = json.dumps(dx_list, indent = 4)
        
#        reseach = f.require_group('/Research')

        
        #convert numerics
        #convert waveforms
        
    print ('Extracting labs')
    labs = extract_labs(filename)
    write_labs(labs, outfile)
    
    print ('Extracting notes')
    notes = extract_notes(filename))
    write_notes(notes, outfile)      

    #micro
        
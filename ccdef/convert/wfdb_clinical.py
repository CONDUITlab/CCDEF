"""
Convert MIMIC III data to CCDEF (hdf5 based)
"""
import numpy as np
import pandas as pd
#import sqlite3
import h5py
import json
import wfdb
from ccdef._utils import df_to_sarray


def patient_id_from_file(filename):
    return (filename.split('/')[-1].split('-')[0][1:].strip("0"))
        
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
        root = f['/']

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
        
        root.attrs['demographics'] = json.dumps(demographics, indent = 4)
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
    notes = extract_notes(filename)
    write_notes(notes, outfile)      

    #micro
    
    # process clinical - file or list of files
    # read csv file
    # process files in sequence
    # use a class?

def _limit_time(df, start=pd.Timestamp.min, end=pd.Timestamp.max):
    """
    selects rows in DataFrame that have Datetime value between start and end
    if start and end are not specified then the default is all rows

    """

    new_df = df.loc[ (df['Datetime'] >= start) & (df['Datetime'] <= end)]
    
    return new_df

class LabData ():
    """
    """
    
    def __init__ (self, path):
        self.load(path)

    def load (self, path):
        print('Loading MIMIC lab data from {}'.format(path))
        self.data = pd.read_csv(os.path.join(path, 'LABEVENTS.csv'), 
                usecols=['SUBJECT_ID', 'HADM_ID', 'ITEMID', 'CHARTTIME', 'VALUE', 'VALUENUM', 'VALUEUOM', 'FLAG'])
        self.data['HADM_ID'] = self.data['HADM_ID'].fillna(0)
        self.data['HADM_ID'] = self.data['HADM_ID'].astype({'HADM_ID':int})
        
        self.info = pd.read_csv(os.path.join(path, 'D_LABITEMS.csv'), 
                usecols=['ITEMID', 'LABEL', 'FLUID', 'CATEGORY', 'LOINC_CODE'])

    def for_subj (self, subj_id, admissions = 'ALL', start=pd.Timestamp.min, end=pd.Timestamp.max):
        """
        Return labs for specified subject, optionally limited to specific admission and/or start and end times

        Parameters
        ----------

        subj_id: int
            subject_identifier (encoded in the MIMIC3 file name)
        admissions: int or list
            optional flag to limit returned labs to particular admission(s)
            default is not to limit
        start: datetime
        end: datetime

        return: 
            dataframe of lab tests for subject, indexed to datetime derived from CHARTTIME
            
        """
        if admissions == 'ALL':
            pt_labs = self.data[self.data['SUBJECT_ID']==subj_id]
        else:
            pt_labs = self.data[self.data['SUBJECT_ID']==subj_id]
            pt_labs = pt_labs.loc[(pt_labs['HADM_ID'].isin(admissions))]
        
        #apply time limits
        pt_labs.insert(loc=0, column='Datetime', value=pd.to_datetime(pt_labs['CHARTTIME']))
        pt_labs = _limit_time(pt_labs, start, end)
        
        #merge lab info
        pt_labs = pd.merge(pt_labs, self.info, on='ITEMID')
        
        #cleanup columns
        del pt_labs['SUBJECT_ID']
        del pt_labs['CHARTTIME']

        #set index
        pt_labs = pt_labs.set_index(keys='Datetime')
        pt_labs.sort_index(inplace=True)
        
        # then change to float for write..
        # option to generate test info metadata
        
        return pt_labs
    
    @staticmethod
    def write_labs(df, filename, test_metadata=False):
        """
        Parameters
        ----------
        df: DataFrame
            Datetime index
        filename: String
        test_metadata

        """
        with h5py.File(filename, 'a') as f:
            origin = pd.to_datetime(json.loads(f['/'].attrs['.meta'])['time_origin'])
            df['time']=(origin-df.index).total_seconds()
            
            df.columns = df.columns.str.strip().str.lower()
            arr, saType = df_to_sarray(df)
            clin = f.require_group('/clinical')
            lab_ds = clin.create_dataset('labs', maxshape = (None, ), data = arr, dtype=saType,
                                 compression="gzip", compression_opts = 9, shuffle = True)
            lab_ds.attrs['.test_info'] = 'none'



class Notes ():
    """
    """
    
    def __init__ (self, path):
        self.load(path)

    def load(self, path):
        print('Loading MIMIC note data from {}'.format(path))
        self.data = pd.read_csv(os.path.join(path, 'NOTEEVENTS.csv'))
        self.data['HADM_ID'] = self.data['HADM_ID'].fillna(0)
        self.data['HADM_ID'] = self.data['HADM_ID'].astype({'HADM_ID':int})

    def for_subj (self, subj_id, admissions = 'ALL', start=pd.Timestamp.min, end=pd.Timestamp.max):
        """
        Add clinical data to MIMIC files that have been converted from wfdb to hdf5


        Parameters
        ----------

        filenames: string
            filename of a wfdb file from the MIMIC3 matched dataset
        origin: datetime
            the base datetime for the file
        start: datetime
        end: datetime

        return: 
            dataframe of lab tests for subject
            - optionally limited to specified admission
            - optionally limited to datetime between start and end

        """
        if admissions == 'ALL':
            pt_notes = self.data[self.data['SUBJECT_ID']==subj_id]
        else:
            pt_notes = self.data[self.data['SUBJECT_ID']==subj_id]
            pt_notes = pt_notes.loc[(pt_notes['HADM_ID'].isin(admissions))]
        
        #apply time limits
        pt_notes['Datetime']=pd.to_datetime(notes['CHARTTIME'])
        pt_notes = _limit_time(notes, start, end)
                
        #cleanup columns
        del pt_notes['SUBJECT_ID']
        del pt_notes['CHARTTIME']

        #set index
        pt_notes = pt_labs.set_index(keys='Datetime')
        
        # then change to float for write..
        # option to generate test info metadata
        
        return pt_notes
    
    @staticmethod
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

#micro
#chartevents


def add_clinical_to_files(filenames: Union [str, list], labs=True, micro=False, notes=True, demo=True):
    """
    Add clinical data to MIMIC files that have been converted from wfdb to hdf5


    Parameters
    ----------

    filenames: string
        filename of a wfdb file from the MIMIC3 matched dataset
    origin: datetime
        the base datetime for the file
    labs
    micro
    notes
    demo
        demographics

    return: 
        something
    """
    #get file origin


    pass




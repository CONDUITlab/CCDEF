Core CCDEF Groups
*******************

These are the principal groups in a CCDEF HDF5 file. 
The root group is obviously mandatory but valid files can be created with physiologic data (Numerics and/or Waveforms) only or with clinical data only.

The Research and Reference groups are strictly optional and are not parsed by any of the viewer or analysis tools at this time.

Root (/)
========

The root group is the top level of the file, it contains a series of other high level groups with physiologic and clinical data.

Root Group Metadata
-------------------

The .meta attribute contains information about the file. ::

    /.meta
        {
            "title": "...",
            "author": "...",
            "organization": "...",
            "time_origin": "2020-41-17 15:41:22.306880 EST",
            "ccdef_version": 1.0
        }

Demographics
^^^^^^^^^^^^
Demographic information about the patient is stored as an *optional* root group attribute. 

.. py:function:: demographics attribute (/.demographics)

 :param float age: Patient age in years (fractional years allowed)
 :param str gender: patient gender {M,F}
 :param int expired: value: {0,1} 0 indicating that the patient did not die during the period covered by the file
 :param str admit_dx: admission ICD 9 code (note that a full list of diagnostic codes can also be specified in /clinical/diagnosis

The resulting JSON formatted attribute looks like this: ::

    /.demographics
        {
            "age": 40.1,
            "gender": "M",
            "expired": 0
        }

Root Group Datasets
-------------------

mapping
^^^^^^^^

One of the key issues in data sharing is the ability to seamlessly ingest data from multiple sites into the end users' application without having to develop site specific pipelines. 
This is complicated by the fact that collect sites will have various local factors that influence the way they store data, based on equipment, etc. 
The data model is self-describing so it is fairly straight forward for end users to locate and extract the data that they need, but to add an additional level of interoperability we provide a mapping table for common key :ref:`signal names<Standard Signal Names>` that allow a user to directly (or using library functions) search and access the information they require.


+---------+---------------------------+------------+--------+----------+---------+-------------------+
| signal  | dataset                   | local_name | column | category | LOINC   | loinc_name        |
+=========+===========================+============+========+==========+=========+===================+
| HR      | /numerics/vitals/         |    HR      |  1     | numerics | 8867-4  | Heart Rate        | 
+---------+---------------------------+------------+--------+----------+---------+-------------------+
| ABP-S   | /numerics/vitals/         |   ABPSys   |  2     | numerics | 76215-3 | Invasive sys BP   | 
+---------+---------------------------+------------+--------+----------+---------+-------------------+
| ECG-I   | /waveforms/hemodynamics   |    I       |  1     | waveforms|         |                   | 
+---------+---------------------------+------------+--------+----------+---------+-------------------+

Mapping Table Field Descriptions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. py:function:: mapping dataset

    The mapping table describes parameters in terms of LOINC (link) to provide further standardization and clarity as to the nature of the information. 
    The mapping table also provides the group, dataset and column (if the dataset is tabular)

    :param str signal: The CCDEF standard signal name (see :ref:`signal names<Standard Signal Names>`)
    :param str dataset: The name of the dataset containing the signal (can be accessed directly as f['/Group/'+dataset])
    :param str local_name: The original name of the signal in the datafile. This will generally be the dataset name if multiple datasets are used or it will be the column name in a tabular dataset.
    :param int column: The number of the column in *dataset* containing the signal (default is 1 for a single column dataset)
    :param str category: {waveform, numeric}
    :param str LOINC: The LOINC for the signal of interest
    :param str loinc_name: The LOINC short name (if it exists) for the signal


.. note::

    A number of waveform signals do not currently have assigned LOINC identifiers but additions are being proposed to address this.



Future Mapping Possibilities
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Future versions of CCDEF may include additional ontologies such as OMOP in the mapping table. 
This is an area of active development. 


Numerics
========

The numerics group contains signals at a sample rate of less than 50 Hz. 
Generally data in this group will be in a single tabular dataset called *Vitals*

Numerics Datasets
-----------------

These can be tabular or single channel as described in detail :ref:`here<_Dataset_details>`.

Typical parameters include:

- Invasive BP (ABP) 
- Non-invasive BP (NIBP)
- SpO2
- HR


Waveforms
==========

The Waveforms group contains data that is recorded at frequencies typically 100-500 Hz.
There is generally more variabiltiy in the sample rates for different waveform signals, particularly if they are derived from different sources (eg bedside monitor, ventilator, etc).

Waveform Datasets
-----------------

The most common datasets will be cardiorespiratory measurements conisting of:

- ECG leads
- SpO2
- ABP

Once again, these can be tabular or single channel as described in detail :ref:`here<Dataset_details>`.

Clinical
==================

The clinical group contains a variety of information extracted from the EMR and other sources, generally excluding monitor data.

As there are a wide range of EMR data extraction pipelines, it is difficulty to completely standardize this group but we provide some high level guidance.
Perhaps the greatest challenge within the clinical data is mapping concepts such as interventions and clinical observations. 

This is an active area of research and is one of the goals of the OMOP-CDM.



Clinical Timestamps
--------------------

Clinical data tend to be much sparser than physiologic data and therefore timestamps will typically be included in these datasets.
The prefered method is a time column with seconds from the *time_orgin*. 

.. note::

    If no base_datetime is specified in the clinical datasets, the time orgin for the file in the root group metadata will be used *(/.meta)*.

Clinical Datasets
------------------
Suggested Clinical Datasets Include:

- labs
- micro
- notes (EMR notes)
- diagnosis

Imaging if available would be in a separate group */Clinical/Imaging*

.. py:function:: labs dataset

    The labs dataset contains time stamped laboratory data such as chemistry, hematology, etc

    :param int time: seconds elapsed from base_datetime
    :param int test_id: the test identifier (this may link to the .test_info attribute)
    :param str value: the value of the test as a string
    :param test_name: the name of the test
    :type test_name: str ,optional

.. py:function:: micro dataset

    The micro dataset contains time stamped microbiolgy data from a variety of sources (eg blood, urine, CSF, tissue)
    Note that there may be multiple time fields with relevant information as the time from sample collection to result can be clinicaly relevant. 
    Caution is advised however in that these values may not always be entirely accurate as they often result from manual data entry.

    :param int time: seconds elapsed from base_datetime
    :param int test_id: the test identifier (this may link to the .test_info attribute)
    :param str value: the value of the test as a string
    :param test_name: the name of the test
    :type test_name: str ,optional

.. py:function:: notes dataset

    The notes dataset includes clinical notes from the EMR.

    :param int time: seconds elapsed from base_datetime
    :param int test_id: the test identifier (this may link to the .test_info attribute)
    :param str value: the value of the test as a string
    :param test_name: the name of the test
    :type test_name: str ,optional

.. py:function:: diagnosis dataset

    The diagnosis dataset is a list of diagnostic codes applicable to the patient stay described by the file.

    :param str dxcode: diagnostic code
    :param str dxname: diagnosis text (optional)

.. note::

    The default coding scheme is ICD 9 but this will be specified in the meta data for the diagnostic dataset as shown here ::

    /clinical/diagnosis/.coding = "ICD 9"

Clinical Dataset Metadata
^^^^^^^^^^^^^^^^^^^^^^^^^^

Information about tests can be stored in *.test_info*, 

.. py:function:: .test_info metadata attribute

    :param str label: name of the test
    :param str category: type of test (eg chemistry, blood gas)
    :param str fluid: fluid used for test (eg: blood, urine, CSF)
    :param str valueuom: units of measurement for the test
    :param str loinc_code: the loinc for the test (eg '718-8')
    

Files converted from MIMIC III will have a JSON formatted string like this: ::

    /clinical/labs.test_info
        {'50809': {
            'label': 'Glucose',
            'category': 'Blood Gas',
            'fluid': 'Blood',
            'valueuom': 'mg/dL',
            'loinc_code': '2339-0'},
        '50810': {
            'label': 'Hematocrit, Calculated',
            'category': 'Blood Gas',
            'fluid': 'Blood',
            'valueuom': '%',
            'loinc_code': '20570-8'},
        '50811': {
            'label': 'Hemoglobin',
            'category': 'Blood Gas',
            'fluid': 'Blood',
            'valueuom': 'g/dL',
            'loinc_code': '718-7'},
        '50813': {
            'label': 'Lactate',
            'category': 'Blood Gas',
            'fluid': 'Blood',
            'valueuom': 'mmol/L',
            'loinc_code': '32693-4'},
        '50816': {
            'label': 'Oxygen',
            'category': 'Blood Gas',
            'fluid': 'Blood',
            'valueuom': '%',
            'loinc_code': '19994-3'},
        '50817': {
            'label': 'Oxygen Saturation',
            'category': 'Blood Gas',
            'fluid': 'Blood',
            'valueuom': '%',
            'loinc_code': '20564-1'},
        '50818': {
            'label': 'pCO2',
            'category': 'Blood Gas',
            'fluid': 'Blood',
            'valueuom': 'mm Hg',
            'loinc_code': '11557-6'},
        '50819': {
            'label': 'PEEP',
            'category': 'Blood Gas',
            'fluid': 'Blood',
            'valueuom': None,
            'loinc_code': '20077-4'},
        '50820': {
            'label': 'pH',
            'category': 'Blood Gas',
            'fluid': 'Blood',
            'valueuom': 'units',
            'loinc_code': '11558-4'},
        }



Research
========

The research group is an optional group with no specific format. 
It is intended primarily to support files used in trials and can contain trial specific information such as randomization, group assignment, etc.

References
==========

The reference group is also optional and is included for future development.
The main purpose of this group is to include links (refered to as references in HDF5) to regions of interest within files or external links to other files.
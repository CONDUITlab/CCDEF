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

The .metadata attribute contains information about the file including:
- datasource
- file version
- base time

**Example**

Root Group Datasets
-------------------

.Mapping
^^^^^^^^

One of the key issues in data sharing is the ability to seamlessly ingest data from multiple sites into the end users' application without having to develop site specific pipelines. 
This is complicated by the fact that collect sites will have various local factors that influence the way they store data, based on equipment, etc. 
The data model is self-describing so it is fairly straight forward for end users to locate and extract the data that they need, but to add an additional level of interoperability we provide a mapping table for common key parameters that allow a user to directly (or using library functions) search and access the information they require.

The mapping table describes parameters in terms of LOINC (link) to provide further standardization and clarity as to the nature of the information. 
The mapping table also provides the group, dataset and column (if the dataset is tabular)

+---------+---------------------------+------------+--------+----------+---------+-------------------+
| signal  | dataset                   | local_name | column | category | LOINC   | loinc_name        |
+=========+===========================+============+========+==========+=========+===================+
| HR      | /Numerics/Vitals/         |    HR      |  1     | numerics | 8867-4  | Heart Rate        | 
+---------+---------------------------+------------+--------+----------+---------+-------------------+
| ABP-S   | /Numerics/Vitals/         |   ABPSys   |  2     | numerics | 76215-3 | Invasive sys BP   | 
+---------+---------------------------+------------+--------+----------+---------+-------------------+
| ECG-I   | /Waveforms/Hemodynamics   |    I       |  1     | waveforms|         |                   | 
+---------+---------------------------+------------+--------+----------+---------+-------------------+

Mapping Table Fields
^^^^^^^^^^^^^^^^^^^^
:signal:
    The CCDEF standard signal name (see list)

:dataset:
    The dataset containing the signal

:local_name:
    The original name of the signal in the datafile. This will generally be the dataset name if multiple datasets are used or it will be the column name in a tabular dataset.

:column:
    The column number in *dataset* for the signal of interest

:category:
    Waveform or Numeric

:LOINC:
    The LOINC for the signal of interest.
    A number of waveform signals do not currently have assigned LOINC identifiers but additions are being proposed to address this.

:loinc_name: 
    This is the LOINC short name (if it exists) for the signal



example dataframe from MIMIC 

example from API: f.show_map()

Future Mapping Possibilities
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Future versions of CCDEF may include additional ontologies such as OMOP in the mapping table. 
This is an area of active development. 


Numerics
========

The numerics group contains signals at a sample rate of less than 50 Hz. 
Generally data in this group will be in a single tabular dataset called *Vitals*

Typical parameters include:

- Invasive BP (ABP)
- Non-invasive BP
- SpO2
- HR

Waveforms
==========

The Waveforms group contains data that is recorded at frequencies typically 100-500 Hz.

The most common dataset will be hemodynamic measurements conisting of:

- one
- two
- three

Clinical
========

The clinical group contains:


Datasets
--------
Possible Datasets:
- Labs
- Micro
- Notes (EMR notes)
- Diagnosis


Clinical Timestamps
-------------------

Clinical data tend to be much sparser than physiologic data and therefore timestamps will typically be included in these datasets.
The most common format will be an absolute timestamp stored as a string (possibly with an offset for anonymization)

Metadata
--------

Demographics
^^^^^^^^^^^^

This is stored in the .Demographics attribute. It is a JSON formatted string.

**Example:**


Research
========

The research group is an optional group with no specific format. 
It is intended primarily to support files used in trials and can contain trial specific information such as randomization, group assignment, etc.

References
==========

The reference group is also optional and is included for future development.
The main purpose of this group is to include links (refered to as references in HDF5) to regions of interest within files or external links to other files.
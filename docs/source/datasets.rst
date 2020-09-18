.. _Dataset_details:

Monitor/Physiologic Datasets (Waveform and Numerics)
====================================================

Datasets can be single channels or they can be a table of multiple channels. 

Single Channel Format
---------------------

In this case, each signal is stored in a separate dataset in its respective group.
The file structure would be:

 | / (root)
 |      .mapping
 |      /numerics
 |          HR
 |          ABP-S
 |          ABP-D
 |          ABP-M
 |          SPO2
 |
 |      /waveforms
 |          ECG-II
 |          ABP
 |          CVP
 |  
 |      /clinial
 |          Notes
 |          Labs
 |          Micro
 

Tabular Format
--------------

In a tabular dataset, multiple similar signals (generally same sample rate and source) are stored together.
The resulting file structure looks like:

 | / (root)
 |      .mapping
 |      /numerics
 |          vitals
 |
 |      /wwaveforms
 |          hemodynamics
 |  
 |      /clinial
 |          notes
 |          labs
 |          micro

Monitor Dataset Metadata
--------------------------

Metadata for datasets derived from bedside monitors (numerics and waveforms) is stored JSON formatted attribute as shown below. ::

    dataset/.meta
        {
             "columns": {
                 "HR": {
                 "type": "real",
                 "LOINC": "8867-4",
                 "uom": "bpm",
                 "scale": 1,
                 "sample_rate": 0.0166666666667,
                 "fmt": "16",
                 "baseline": 0,
                 "base_datetime": "2116-12-24 12:35:06.147000"
                },
                 "CVP": {
                     "type": "real",
                     "LOINC": "60985-9",
                     "uom": "mmHg",
                     "scale": 1,
                     "sample_rate": 0.0166666666667,
                     "fmt": "16",
                     "baseline": 0,
                     "base_datetime": "2116-12-24 12:35:06.147000"
                },
                 "SpO2": {
                 "type": "real",
                 "LOINC": "",
                 "uom": "%",
                 "scale": 1,
                 "sample_rate": 0.0166666666667,
                 "fmt": "16",
                 "baseline": 0,
                 "base_datetime": "2116-12-24 12:35:06.147000"
                },
            "NBPSys": {
                "type": "real",
                "LOINC": "76534-7",
                "uom": "mmHg",
                "scale": 1,
                "sample_rate": 0.0166666666667,
                "fmt": "16",
                "baseline": 0,
                "base_ddatetime": "2116-12-24 12:35:06.147000"
                },
            }

Dataset Metadata Fields
^^^^^^^^^^^^^^^^^^^^^^^
:type: 
    will be "real" for a data column and "time" for a timestamp column 

:LONIC:
    Loinc code

:uom:
    units of measurement

:scale:
    scale factor for storing raw output from data acquisiting systems as integer values (this will be set to 1 for data stored as floats)

:sample_rate:
    sample rate in Hz

:base_datetime:
    the time origin of the dataset formatted as "YYYY-MM-DD HH:MM:SS.ssss"
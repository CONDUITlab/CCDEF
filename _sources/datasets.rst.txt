.. _Dataset_details:

Physiologic Datasets (Waveform and Numerics)
====================================================

Datasets can be single channels or they can be a table of multiple channels. 

Single Channel Format
---------------------

In this case, each signal is stored in a separate dataset in its respective group.
The file structure would be:

 | / (root)
 |      mapping
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
 |          notes
 |          labs
 |          micro
 |          infusions
 

Tabular Format
--------------

In a tabular dataset, multiple similar signals (generally same sample rate and source) are stored together.
The resulting file structure looks like:

 | / (root)
 |      mapping
 |      /numerics
 |          vitals
 |
 |      /waveforms
 |          hemodynamics
 |  
 |      /clinial
 |          notes
 |          labs
 |          micro
 |          infusions

Monitor Dataset Metadata
--------------------------

Dataset Metadata Fields
^^^^^^^^^^^^^^^^^^^^^^^

.. py:function:: physiologic dataset metadata (eg: /waveforms/ABP/.meta)

    These datasets can be single or multicolumn but the metadata attribute will be similar in both cases.
    Timestamps may be stored as a number of seconds from the origin (base_datetime) or they may be implied.
    In the case of implied timestamps, the timeseries is reconstructed using the sample_rate and the row number.
    Single signal datasets can be further divided into two types:
    
        * with timestamps (compound dtype)
        * with implied timestamps (float dtype)
    
    All datasets should include at at least a .meta attribute containing time orign and sample rate fields.
    If the datasets do not have this information in the .meta attribue then the time_origin will be assumed to be that stored in the metadata for the containing group (eg waveforms or numerics) or in the root group.
    
:sample_rate:
    sample rate in Hz

:time_origin:
    the time origin of the dataset formatted as "YYYY-MM-DD HH:MM:SS.ssss"

Additional information (particularly for tabular datasets) is included in the column field:

.. py:function:: dataset column metadata (eg: /waveforms/ABP/.meta)

    :param str type: column type {time or real}
    :param str LOINC: LOINC identifier for a signal column
    :param str uom: units of measurement
    :param float scale: scale factor [optional] - used to convert raw data stored as int in the dataset to physical units (this will be set to 1 or omitted entirely if the data is already stored as float)
    :param fmt: format [optional] 
    
Sample dataset metadata stored as JSON formatted attribute as shown below. ::

    /group/dataset/.meta
        {
            "time_origin": "2116-12-24 12:35:06.147000",
            "sample_rate": 0.0166666666667,
             "columns": {
                 "HR": {
                 "type": "real",
                 "LOINC": "8867-4",
                 "uom": "bpm",
                 "scale": 1,
                 "fmt": "16",
                 "baseline": 0
                },
                 "CVP": {
                     "type": "real",
                     "LOINC": "60985-9",
                     "uom": "mmHg",
                     "scale": 1,
                     "fmt": "16",
                     "baseline": 0
                },
                 "SpO2": {
                 "type": "real",
                 "LOINC": "",
                 "uom": "%",
                 "scale": 1,
                 "fmt": "16",
                 "baseline": 0
                },
            "NBPSys": {
                "type": "real",
                "LOINC": "76534-7",
                "uom": "mmHg",
                "scale": 1,
                "fmt": "16",
                "baseline": 0
                },
            }
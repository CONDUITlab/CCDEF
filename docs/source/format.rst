Data Format
============

Signal storage
---------------

We have allowed both tabular datasets containing multiple simultaneously recorded signals (eg multiple ECG leads) or single parameter datasets. Becuase the format is self-describing, any of the tools used to read the underlying HDF5 file can accomodate either schema. 

Timestamp storage
------------------

The specification allows for different time column formats depending on the nature of the data and the need to optimize storage space. Once again, these formats are clearly identified and allow for seamless reading of the file.

Timestamps can be:

#. Relative
    * time stored as float number of seconds starting from 0

#. Absolute
    * time stored as a float number of seconds starting from time_origin
    * time_origin stored in the metadata as Datetime formatted string
    * DatetimeIndex reconstructed from time_origin and offsets stored in dataset 

#. Implied
    * no time column in the dataset
    * data points must be at fixed period
    * DatetimeIndex ot Timedelta index reconstructed from time_origin and sample rate


Core groups
------------

CCDEF specifies a high level structure to ensure that data can be consistently located. Once again, the goal is to facilitate automated data acquisition and analysis pipelines as much as possible.

Data are segregated broadly into monitor or physiologic data which are continuously recorded and clinical information such as laboratory tests, microbiology, clinical notes, etc.
Physiologic data are further divided based on acquisition speed into numerics and waveforms with numerics typically being classified as periodic signals with sample rates of 50 Hz and below.

Derived or secondary variables can optionally be stored in ccdef files. These are nested below their source group. More details on secondary variables/datasets are provided :ref:`here<Derived Data>`

.. note:: 

 | The overall structure of a CCDEF file looks like this: 

 | / (**root** group) 
 | .meta (metadata)
 | .demographics

 | / **numerics**
 |
 |      /vitals
 |
 | / **waveforms**
 |
 |       /hemodynamics
 |           /derived
 |           /annotations
 |       /ventilator
 |
 | / **clinical**
 |
 |       /labs
 |       /micro
 |       /notes
 |       /diagnosis
 |
 | / **research**

Further details of the groups structure are provided :ref:`here<Core CCDEF Groups>`



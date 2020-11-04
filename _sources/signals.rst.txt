Standard Signal Names
----------------------

There are many different variable names used for the same physiological parameters. Recognizing that various sites will have signifcant volumes of legacy data as well as acquistion pipelines that do not easily allow for signals to be renamed, CCDEF supports the storage of signals with different names but provides a standardized list of common signals that are mapped to the source data. Where possible a standard ontology is also used to provide further clarity. Currently LOINC is recommended and supported by the standard. There are a number of commonly used waveform parameters in critical care that do not have LOINC code and this is an area that the group is currently working to address.

Numerics
^^^^^^^^^

- HR
- ABP-S
- ABP-M
- ABP-D
- NIBP-S
- NIBP-M
- NIBP-D
- CVP
- RR
- SPO2

Waveforms
^^^^^^^^^^
- ABP
- PLETH
- CVP
- ECG-I
- ECG-II
- ECG-III
- ECG-V

.. note::

    Additional standard signals may be added in future versions of the standard. 
    In particular, we are very interested in acquiring ventilator waveforms and parameters. 
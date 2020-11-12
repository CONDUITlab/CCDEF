Derived Data & Annotations
========================

Secondary variables
--------------------

Derived or secondary variables result from the analysis of the primary data stored in the file (typically the physiologic data in waveforms and numerics).

Examples include:

* heart rate variability
* pulse pressure variability
 
 Derived variables should be stored in the /derived subgroup of the source group, in either a single column or tabular dataset. 

Annotations
-----------

Annotations (human or algorithmically generated) are also nested with their source data, in an /annotations subgroup. 

Metadata
--------

Annotations and derived variable datasets will have the usual .meta attibute which will include specific information about the source dataset(s).

These datasets should also have a .source attribute with an h5 references to the source dataset.





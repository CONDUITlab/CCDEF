Future Development
====================

CCDEF is intended to be an evolving standard. The nature of HDF5 makes it relatively easy to add functionality to the data model without adversely effecting tools and pipelines developed to work with earlier versions.
This provides an excellent pathway for growth but also preserves "backwards compatibility" which is essential as large datasets are accumulated.

Some of the short and medium term goals of the project are outlined below. 

Ontological mapping
--------------------

Future versions of CCDEF will likely include additional common ontology mapping such as OMOP-CDM. 
This will help standardize terms for clinical concepts such as procedures and investigations other than lab tests described by LOINC.

Genomics
---------

Schemas for genomic data using HDF5 such as BIOHDF have been proposed. 
As sequencing technologies improve, the ability to combine clincal/physiological data with genomic information will also increase.

Imaging
--------

Conversion tools from DICOM to HDF5 have been developed. The new MINC format (Medical Imaging NetCDF) is based on HDF5. We plan to develop guidelines for importing or linking imaging data with the clinical/physiological data already described in CCDEF. 

File linking
-------------

HDF5 supports inter-file linking (referencing). Future CCDEF versions will explicitly address preferred usage for this feature. This will most likely be in the setting of extremely large datasets or data containing large amounts of imaging and/or genomic data which may only be occasionally analysed with the clinical data.

Data Federation
----------------

A major goal of the project is to develop tools for sharing information between multiple sites. 



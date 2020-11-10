Introduction
====================

Across our collective clinical research activities, the authors have observed an unmet need for standardized, widely available data models and tooling to enable review, analysis, and learning from large, high-density patient datasets in critical care medicine. 
To that end, we are sharing here a proposed data model and are simultaneously publishing a set of open-source tools for data conversion, review, analysis and annotation using this standard.

The Critical Care Data Exchange Format (CCDEF) is a data model and file encoding standard for storing, analyzing, and exchanging physiologic and clinical data collected over the course of a patient stay. The data model is designed to be lightweight & flexible while still being sufficiently standardized to allow for seamless data exchange. The file encoding standard is designed for efficient storage and performant interaction with multimodal data. It is based on Hierarchical Data Format version 5 (HDF5), an open source file format which is widely supported across operating systems & programming languages and supports advanced features like data-streaming and compression out of the box.

HDF5
----

HDF5 is an open-source file format which encodes numerical data efficiently and therefore is suitable for large datasets but also allows for heterogeneous data such as variable-length strings to be stored. 
HDF5 supports advanced features including data-streaming and compression. For streaming support, chunked datasets are used, and gzip compression is used for portability.

HDF5 is built around groups, datasets, and attributes. 
Datasets hold tabular data and may be stored in an arbitrary hierarchy of groups, like folders on a file system. 
Both groups and datasets may have attributes attached to them, and attributes are key/value pairs of variable-length strings. 

In the sense that groups and datasets have attributes, HDF has been characterized as a self-describing data format as the any supplemental information required to contextualize or interpret the data stored in the datasets is provided in the attributes. 

HDF5 is widely supported by the broader data science community and there are a wide range of tools available for reading and manipuating generic HDF5 files which are also useful for handling ccdef files. Some of these tools are listed :ref:`here<Tools>`.


Design Philosophy
-----------------

HDF5 permits a great deal of flexibility, and the aim of the CCDEF was to strike a balance between allowing users the flexibility to maintain local data acquisition pipelines as much as possible while also enabling the main objective of seamless data sharing. 

Our intention is to provide a wide range of tools for easy analysis of CCDEF formated physiologic and clinical data but at the same time provide a format that can be read natively with existing HDF5 libraries for tools such as MATLAB, python, C, etc.







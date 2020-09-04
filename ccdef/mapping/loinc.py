# -*- coding: utf-8 -*-
# @Author: Alex Hamilton - https://github.com/alexhamiltonRN
# @Date: 2020-08-27
# @Desc: class for for mapping local chart events and signals to LOINC

import io
import json
from dataclasses import dataclass

import numpy as np
import pandas as pd
import requests

print(
    "\n"
    "***** CCDEF LoincMapper *****\n"
    "This material contains content from LOINC (http://loinc.org).\n"
    "LOINC is copyright © 1995-2020, Regenstrief Institute, Inc.\n"
    "and the Logical Observation Identifiers Names and Codes (LOINC)\n"
    "Committee and is available at no cost under the license at\n"
    "http://loinc.org/license. LOINC® is a registered United States\n"
    "trademark of Regenstrief Institute, Inc."
    "\n"
)


@dataclass
class Mapping:
    category: list
    local: list
    ccdef: str
    loinc: str
    loinc_sn: str


class LoincMapper:
    """
    Methods to map local entities to LOINC codes and CCDEF. Allows for lookup 
    using data from a local table via a local_mapping_table (csv path (str)) or an 
    external table (external_mapping_table (str)) pre-specified and hosted by 
    CCDEF organization.  
    
    see CCDEF.org and associated github repo for available external mappings.
    
    params:
        local_mapping_table: str (path)
        external_mapping_table: str
    returns:
        Mapping(
            category(list),
            local(list),
            ccdef(str),
            loinc(str),
            loinc_sn:(str)
        )

    Examples:
    
    ## Use a local mapping
    ```
    csv_path = "path_to_local_csv"
    mapper = LoincMapper(local_mapping_table=csv_path)
    mapper.local_label("NBPSys")
    mapper.loinc_code("76214-6")
    mapper.ccdef_label("CVP")
    ```
    
    ## Use a pre-specified mapping
    ```
    mapper = LoincMapper(external_mapping_table="MIMICIII")
    mapper.local_label('ABP SYS')
    mapper.loinc_code('76214-6')
    mapper.ccdef_label("CVP")
    ```
    """

    def __init__(self, **kwargs):

        self._mapping_table = None
        self._categories = None
        self._local_labels = None
        self._ccdef_labels = None
        self._loinc_codes = None
        self._loinc_sns = None

        # Check named kwargs. Expectation is that user provides value
        # for named parameter local_mapping_table or external_mapping_table
        # (not both)

        if len(kwargs.keys()) > 1:
            raise Exception(
                "Pass ONLY local_mapping_table (path (str)) OR valid "
                "external_mapping_table (str) using named argument"
            )
        else:
            if "local_mapping_table" in kwargs.keys():
                mapping_table = self._load_mapping_table(kwargs["local_mapping_table"])
                self._check_mapping_table_schema(mapping_table)
                self._mapping_table = mapping_table

            elif "external_mapping_table" in kwargs.keys():
                self._mapping_table = self._download_mapping_table(
                    kwargs["external_mapping_table"]
                )
            else:
                raise Exception(
                    "Pass value for argument local_mapping_table (path (str)) OR "
                    "external_mapping_table (str)"
                )

        self._initialize_arrays()

    @staticmethod
    def _load_mapping_table(csv_path):
        mapping_table = pd.read_csv(csv_path)
        return mapping_table

    @staticmethod
    def _check_mapping_table_schema(mapping_table):
        """
        Check that local csv mapping file contains local_label, loinc_code,
        loinc_shortname, category, and ccdef_label cols. Raises an exception 
        if this requirement is not met.
        """

        req_cols = np.sort(
            np.array(
                [
                    "category",
                    "local_label",
                    "ccdef_label",
                    "loinc_code",
                    "loinc_shortname",
                ]
            )
        )

        mapping_table_cols = np.sort(np.array(mapping_table.columns))
        comparison = req_cols == mapping_table_cols

        if not comparison.all():
            raise Exception(
                "Check schema of local_mapping_table (csv). "
                "Example: Must contain cols category (str), "
                "local_label (str), ccdef_label (str), "
                "loinc_code (str), and loinc_shortname (str)"
            )

    @staticmethod
    def _download_mapping_table(mapping_table_name):
        print("Downloading list of available mappings from CCDEF.org")
        url = (
            "https://raw.githubusercontent.com/CONDUITlab/ccdef/master/"
            "ccdef/mapping/mappings/external_mappings.json"
        )
        available_external_mappings = json.loads(requests.get(url).text)

        print("Verifying requested mapping exists")
        if mapping_table_name in available_external_mappings.keys():
            print(f"Passed. Downloading mapping table for {mapping_table_name}")
            with requests.Session() as session:
                download = session.get(
                    available_external_mappings[mapping_table_name]
                ).content
                mapping_table = pd.read_csv(io.StringIO(download.decode("utf-8")))
            return mapping_table
        else:
            raise Exception(
                "Pass valid table identifier (str) for "
                "external_mapping_table parameter"
            )

    def _initialize_arrays(self):
        """
        Internal method to extract mapping table cols as numpy 
        arrays and store as instance variables on class. 
        """
        self._categories = self._mapping_table["category"].to_numpy()
        self._local_labels = self._mapping_table["local_label"].to_numpy()
        self._ccdef_labels = self._mapping_table["ccdef_label"].to_numpy()
        self._loinc_codes = self._mapping_table["loinc_code"].to_numpy()
        self._loinc_sns = self._mapping_table["loinc_shortname"].to_numpy()

    def _lookup(self, ref_col, value):
        if ref_col == "local":
            sel_rows = self._local_labels == value
        elif ref_col == "loinc":
            sel_rows = self._loinc_codes == value
        else:
            sel_rows = self._ccdef_labels == value

        # check if passed value is invalid for subsetting arrays
        if np.all(sel_rows == False):
            return Mapping(
                category=["None"],
                local=["None"],
                ccdef="None",
                loinc="None",
                loinc_sn="None",
            )

        categories = self._categories[sel_rows]
        local_labels = self._local_labels[sel_rows]

        # Check if loinc_code and ccdef_label length is > 1
        # if so, print return values and raise exception to
        # notify user that there is a problem in the mapping table.

        ccdef_label = np.unique(self._ccdef_labels[sel_rows])
        loinc_code = np.unique(self._loinc_codes[sel_rows])
        loinc_sn = np.unique(self._loinc_sns[sel_rows])

        if len(loinc_code) > 1 or len(ccdef_label) > 1 or len(loinc_sn) > 1:
            print(f"Mapping returns ccdef_label(s): {ccdef_label.tolist()}")
            print(f"Mapping returns loinc code(s): {loinc_code.tolist()}")
            print(f"Mapping return loinc shortname(s): {loinc_sn.tolist()}")

            raise Exception(
                "Error in mapping table. Multiple return values "
                "for ccdef label, loinc code and/or loinc shortname. "
                "Single values expected."
            )

        return Mapping(
            category=[
                "None" if str(category) == str(np.nan) else str(category)
                for category in categories
            ],
            local=[
                "None" if str(local_label) == str(np.nan) else str(local_label)
                for local_label in local_labels
            ],
            ccdef=str("None" if str(ccdef_label[0]) == str(np.nan) else ccdef_label[0]),
            loinc=str("None" if str(loinc_code[0]) == str(np.nan) else loinc_code[0]),
            loinc_sn=str("None" if str(loinc_sn[0]) == str(np.nan) else loinc_sn[0]),
        )

    def local_label(self, value):
        mapped_values = self._lookup("local", value)
        return mapped_values

    def loinc_code(self, value):
        mapped_values = self._lookup("loinc", value)
        return mapped_values

    def ccdef_label(self, value):
        mapped_values = self._lookup("ccdef", value)
        return mapped_values


def main():

    # Example that downloads from remote
    remote_mapper = LoincMapper(external_mapping_table="MIMICIII")
    print(remote_mapper.local_label("NBPSys"))  # MIMIC label (local to BIH)
    print(
        remote_mapper.local_label("PAP Sys")
    )  # local_label with no loinc/ccdef mapping
    print(remote_mapper.ccdef_label("BPM"))  # Invalid ccdef_label
    print(remote_mapper.loinc_code("75994-4"))  # loinc entry without ccdef
    test = remote_mapper.local_label("NBPSys")
    print("done")


if __name__ == "__main__":
    main()

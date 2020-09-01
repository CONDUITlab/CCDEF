# -*- coding: utf-8 -*-
# @Author: Alex Hamilton - https://github.com/alexhamiltonRN
# @Date: 2020-08-27
# @Desc: class for for mapping local chart events and signals to LOINC

import json
from itertools import product

import numpy as np
import pandas as pd
import requests
from dataclasses import dataclass

# FIXME include loinc license in this code...
#   https://loinc.org/kb/license/

@dataclass
class Mapping:
    category: list
    local: list
    loinc: str
    ccdef: str

class LoincMapper:
    """
    Methods to match signal names to LOINC codes. Allows for lookup of either
    a waveform or numeric signal via a local mapping (path) or an external mapping
    pre-specified and hosted by CCDEF organization.  
    
    see CCDEF.org and associated github repo for available external mappings.
    
    params:
        local_mapping: path
        external_mapping: str
    returns:
        loinc_obj.numeric(list)
        loinc_obj.waveform(list)

    Examples:
    
    ## Use a local mapping
    ```
    loinc = LOINC(local_mapping={"numeric":[[[...],[...]]], "waveform"[[[...],[...]]]})
    loinc_code_for_numeric = loinc.numeric("numeric signal name")
    loinc_code_for_waveform = loinc.waveform("waveform signal name)
    ```
    
    ## Use a pre-specified mapping
    ```
    loinc = LOINC(external_mapping="MIMICIII")
    loinc_code_for_numeric = loinc.numeric('ABP SYS')
    loinc_code_for_waveform = loinc.waveform('ART')
    ```
    Note: use loinc_numeric_reverse("LOINC_CODE") or loinc_waveform_reverse("LOINC_CODE")
    to retrieve the signal name in specified mapping.
    """

    def __init__(self, **kwargs):

        self.encoding_table = None
        self.local_labels = None
        self.loinc_codes = None
        self.ccdef_labels = None

        # Check named kwargs. Expectation is that user provides value
        # for named parameter local_encoding_csv or external_encoding
        # (not both)

        if len(kwargs.keys()) > 1:
            raise Exception(
                "Pass only local_encoding_csv (path) OR valid external encoding (str)"
                "using named argument"
            )
        else:
            if "local_encoding_csv" in kwargs.keys():
                encoding_table = self.load_encoding_table(kwargs["local_encoding_csv"])
                self.check_encoding_table_schema(encoding_table)
                self.encoding_table = encoding_table

            elif "external_encoding" in kwargs.keys():
                self.encoding_table = self.download_encoding_table(
                    kwargs["external_encoding"]
                )
            else:
                raise Exception(
                    "Pass value for argument local_encoding_csv (Path) OR "
                    "external_encoding (str)"
                )

        self._initialize_arrays()

    @staticmethod
    def load_encoding_table(csv_path):
        encoding_table = pd.read_csv(csv_path)
        return encoding_table

    @staticmethod
    def check_encoding_table_schema(encoding_table):
        """
        Check that local csv mapping file contains local_label, loinc_code,
        loinc_shortname, category, and ccdef_label cols. Raises an exception 
        if this requirement is not met.
        """

        req_cols = np.sort(np.array(
            ["local_label", "loinc_code", "loinc_shortname", "category", "ccdef_label"]
        ))

        encoding_table_cols = np.sort(np.array(encoding_table.columns))
        comparison = req_cols == encoding_table_cols

        if not comparison.all():
            raise Exception(
                "Check schema of local encoding table (csv). "
                "Example: Must contain cols local_label (str), "
                "loinc_code (str), loinc_shortname (str), "
                "category (str), and ccdef_label (str)"
            )

    @staticmethod
    def download_encoding_table(encoding_table_name):
        print("Getting list of available mappings from CCDEF.org")
        url = (
            "https://raw.githubusercontent.com/CONDUITlab/CCDEF/master/"
            "loinc/mappings/external_mappings.json"
        )
        available_external_mappings = json.loads(requests.get(url).text)
        if encoding_table_name in available_external_mappings.keys():
            # FIXME this needs to download a csv file
            print(f"Downloading mapping for {encoding_table_name}")
            encoding_table = requests.get(
                available_external_mappings[encoding_table_name]
            ).text
            return encoding_table
        else:
            raise Exception(
                "Pass valid identifier (str) for external_encoding parameter"
            )

    def _initialize_arrays(self):
        # extract category,abbreviation, and loinc code cols
        """
        Internal method to extract encoding table cols as numpy 
        arrays and store as instance variables on class. 
        """
        self.categories = self.encoding_table["category"].to_numpy()
        self.local_labels = self.encoding_table["local_label"].to_numpy()
        self.loinc_codes = self.encoding_table["loinc_code"].to_numpy()
        self.ccdef_labels = self.encoding_table["ccdef_label"].to_numpy()

    def _lookup(self, ref_col, value):
        if ref_col == "local_label":
            sel_rows = self.local_labels == value
        elif ref_col == "loinc_code":
            sel_rows = self.loinc_codes == value
        else:
            sel_rows = self.ccdef_labels == value

        categories = np.unique(self.categories[sel_rows]).tolist()
        local_labels = np.unique(self.local_labels[sel_rows]).tolist()
        loinc_code = np.unique(self.loinc_codes[sel_rows])[0]
        ccdef_label = np.unique(self.ccdef_labels[sel_rows])[0]
        
        return Mapping(
            category=[str(category) for category in categories],
            local=[str(local_label) for local_label in local_labels],
            loinc=str(loinc_code),
            ccdef=str(ccdef_label),
        )

    def local_label(self, value):
        mapped_values = self._lookup("local_label", value)
        return mapped_values

    def loinc_code(self, value):
        mapped_values = self._lookup("loinc_code", value)
        return mapped_values

    def ccdef_label(self, value):
        mapped_values = self._lookup("ccdef_label", value)
        return mapped_values


def main():
    
    mapper = LoincMapper(local_encoding_csv="MIMICIII.csv")
    print(mapper.local_label("NBPSys"))
    print(mapper.loinc_code("76214-6"))
    print(mapper.ccdef_label("CVP"))
    print(mapper.local_label("CVP"))
    
    # example -- no loinc code or ccdef
    print(mapper.local_label("PAP SYS"))
    
    # example lookup a loinc that doesn't exist
    print(mapper.loinc_code("54666-0"))
    
    print("done")
if __name__ == "__main__":
    main()

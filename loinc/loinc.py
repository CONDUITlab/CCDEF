# -*- coding: utf-8 -*-
# @Author: Alex Hamilton - https://github.com/alexhamiltonRN
# @Date: 2020-08-27
# @Desc: class for for mapping local chart events and signals to loinc

import json
from itertools import product

import numpy as np
import requests


class LoincMapper:
    """
    Methods to match signal names to LOINC codes. Allows for lookup of either
    a waveform or numeric signal via a local mapping (dict) or an external mapping
    pre-specified and hosted by CCDEF organization.  
    
    see CCDEF.org and associated github repo for available external mappings.
    
    params:
        local_mapping: dict
        external_mapping: str
    returns:
        loinc_obj.numeric(list)
        loinc_obj.waveform(list)

    Examples:
    
    # use a local mapping
    loinc = LOINC(local_mapping={"numeric":[[[...],[...]]], "waveform"[[[...],[...]]]})
    loinc_code_for_numeric = loinc.numeric("numeric signal name")
    loinc_code_for_waveform = loinc.waveform("waveform signal name)

    # use a pre-specified mapping
    loinc = LOINC(external_mapping="MIMICIII")
    loinc_code_for_numeric = loinc.numeric('ABP SYS')
    loinc_code_for_waveform = loinc.waveform('ART')

    Note: use loinc_numeric_reverse("LOINC_CODE") or loinc_waveform_reverse("LOINC_CODE")
    to retrieve the signal name in specified mapping.
    """

    def __init__(self, **kwargs):

        self.mimic_num = None
        self.loinc_num = None
        self.mimic_wf = None
        self.loinc_wf = None

        # Check named kwargs to set self.numeric_mappings and self.waveform_mappings
        # Expectation is that user provides value for named parameter local_mapping
        # or external_mapping (not both)

        kwargs_set = {"local_mapping", "external_mapping"}

        if set(kwargs.keys()).issubset(kwargs_set):
            if "local_mapping" in kwargs.keys() and "external_mapping" in kwargs.keys():
                raise Exception(
                    "Pass only local_mapping (dict) OR valid external_mapping (str) \
                    using appropriate named arg"
                )

            elif "local_mapping" in kwargs.keys():
                self.check_schema(kwargs["local_mapping"])

                self.numeric_mappings = kwargs["local_mapping"]["numeric"]
                self.waveform_mappings = kwargs["local_mapping"]["waveform"]

            elif "external_mapping" in kwargs.keys():

                available_external_mappings = json.loads(
                    requests.get(
                        "https://raw.githubusercontent.com/CONDUITlab/CCDEF/master/loinc/mappings/external_mappings.json"
                    ).text
                )

                if kwargs["external_mapping"] in available_external_mappings.keys():
                    print(f"Downloading mapping from: {kwargs['external_mapping']}")
                    response = json.loads(
                        requests.get(
                            available_external_mappings[kwargs["external_mapping"]]
                        ).text
                    )
                    self.numeric_mappings = response["numeric"]
                    self.waveform_mappings = response["waveform"]
                else:
                    raise Exception(
                        "Pass valid identifier (str) for external_mapping param"
                    )
        else:
            raise Exception(
                "Pass local_mapping (dict) OR valid external_mapping (str) \
                using appropriate named arg"
            )

        self.initialize_lookup_tables_()

    @staticmethod
    def check_schema(mapping_dict):
        """
        Ugly/rough check that supplied mapping dict matches expected schema. 
        Each value pair should be a list of lists where item[0] and item[1] 
        are also lists. Ex: "numeric":[[["HR", "PULSE"], ["8867-4"]]]
        """
        is_correct_schema = False
        for _, value in mapping_dict.items():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, list):
                        if isinstance(item[0], list) and isinstance(item[1], list):
                            is_correct_schema = True
        if not is_correct_schema:
            raise Exception(
                "Check schema of local mapping dict. "
                "Example: 'numeric':[[['HR', 'PULSE'], ['8867-4']]]"
            )

    @staticmethod
    def process_return(mapped_values):
        """
        Return results (numpy array) as list. 
        """
        if len(mapped_values) != 0:
            return list(mapped_values)
        else:
            return ["no_mapping"]

    def initialize_lookup_tables_(self):
        """
        Internal method to generate label-loinc pair (cartesian product) for 
        items in adjacent label-code lists in mapping_dict. Zips (list of tuple pairs) 
        and casts as 1D arrays to facilitate subset (boolean masking) and return 
        of mapped values in method calls below. 
        """

        num_products = []
        wf_products = []

        for mapping in self.numeric_mappings:
            num_product = list(product(mapping[0], mapping[1]))
            num_products.extend(num_product)

        for mapping in self.waveform_mappings:
            wf_product = list(product(mapping[0], mapping[1]))
            wf_products.extend(wf_product)

        numerics = list(zip(*num_products))
        waveforms = list(zip(*wf_products))

        self.mimic_num, self.loinc_num = np.array(numerics[0]), np.array(numerics[1])
        self.mimic_wf, self.loinc_wf = np.array(waveforms[0]), np.array(waveforms[1])

    @staticmethod
    def process_return(mapped_values):
        if len(mapped_values) == 1:
            return mapped_values[0]
        else:
            if len(mapped_values) != 0:
                return list(mapped_values)
            else:
                return "no_mapping"

    def numeric(self, value):
        mapped_values = np.unique(self.loinc_num[self.mimic_num == value])
        return self.process_return(mapped_values)

    def numeric_reverse(self, value):
        mapped_values = np.unique(self.mimic_num[self.loinc_num == value])
        return self.process_return(mapped_values)

    def waveform(self, value):
        mapped_values = np.unique(self.loinc_wf[self.mimic_wf == value])
        return self.process_return(mapped_values)

    def waveform_reverse(self, value):
        mapped_values = np.unique(self.mimic_wf[self.loinc_wf == value])
        return self.process_return(mapped_values)


def main():
    # Local Example...
    khsc = {
        "numeric": [[["HR"], ["8867-4"]], [["ABP-S"], ["76215-3"]]],
        "waveform": [[["PLETH"], ["76523-0"]]],
    }

    local_loinc = LoincMapper(local_mapping=local_map)
    print(f"LOINC code(s) for KHSC HR numeric: {local_loinc.numeric('HR')}")
    print(f"KHSC label for 76215-3: {local_loinc.numeric_reverse('76215-3')}")
    print(f"LOINC code(s) for KHSC PLETH waveform: {local_loinc.waveform('PLETH')}")
    print(f"KHSC label for 76523-0: {local_loinc.waveform_reverse('76523-0')}")

    # External Example...
    MIMICIII_loinc = LoincMapper(external_mapping="MIMICIII")
    print(f"LOINC code(s) for M3 ABP SYS numeric: {MIMICIII_loinc.numeric('ABP SYS')}")
    print(f"MIMIC label for 76213-8: {MIMICIII_loinc.numeric_reverse('76213-8')}")
    print(f"LOINC code(s) for M3 ART waveform: {MIMICIII_loinc.waveform('ART')}")
    print(f"MIMIC label for 76284-9: {MIMICIII_loinc.waveform_reverse('76284-9')}")


if __name__ == "__main__":
    main()

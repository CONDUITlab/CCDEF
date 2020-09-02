# kwargs_set = {"local_mapping_csv, local_mapping_dict", "external_mapping"}
        # if set(kwargs.keys()).issubset(kwargs_set):
        #     if (
        #         "local_mapping_csv" in kwargs.keys()
        #         and "local_mapping_dict"
        #         and "external_mapping" in kwargs.keys()
        #     ):
        #         raise Exception(
        #             "Pass only local_mapping_csv (path), local_mapping_dict (dict)"
        #             "OR valid external_mapping (str) using appropriate named arg"
        #         )

        #     elif "local_mapping_csv" in kwargs.keys():
        #         df = self.load_csv_as_df
        #         self.check_df_schema(df)

        #         pass
            
        #     elif "local_mapping_dict" in kwargs.keys():
        #         self.check_schema(kwargs["local_mapping"])
        #         self.numeric_mappings = kwargs["local_mapping"]["numeric"]
        #         self.waveform_mappings = kwargs["local_mapping"]["waveform"]

        #     elif "external_mapping" in kwargs.keys():

        #         print("Getting list of available mappings.")
        #         url = (
        #             "https://raw.githubusercontent.com/CONDUITlab/CCDEF/master/"
        #             "loinc/mappings/external_mappings.json"
        #         )

        #         available_external_mappings = json.loads(requests.get(url).text)

        #         if kwargs["external_mapping"] in available_external_mappings.keys():
        #             print(f"Downloading mapping for {kwargs['external_mapping']}")
        #             response = json.loads(
        #                 requests.get(
        #                     available_external_mappings[kwargs["external_mapping"]]
        #                 ).text
        #             )
        #             self.numeric_mappings = response["numeric"]
        #             self.waveform_mappings = response["waveform"]
        #         else:
        #             raise Exception(
        #                 "Pass valid identifier (str) for external_mapping param"
        #             )
        # else:
        #     raise Exception(
        #         "Pass local_mapping (dict) OR valid external_mapping (str) "
        #         "using appropriate named arg"
        #     )

        # self.initialize_lookup_tables_()

        # @staticmethod
    # def check_json_schema(mapping_dict):
    #     """
    #     Ugly/rough check that supplied mapping dict matches expected schema. 
    #     Each value pair should be a list of lists where item[0] and item[1] 
    #     are also lists. Ex: "numeric":[[["HR", "PULSE"], ["8867-4"]]]
    #     """
    #     is_correct_schema = False
    #     for _, value in mapping_dict.items():
    #         if isinstance(value, list):
    #             for item in value:
    #                 if isinstance(item, list):
    #                     if isinstance(item[0], list) and isinstance(item[1], list):
    #                         is_correct_schema = True
    #     if not is_correct_schema:
    #         raise Exception(
    #             "Check schema of local mapping dict. "
    #             "Example: 'numeric':[[['HR', 'PULSE'], ['8867-4']]]"
    #         )


     # @staticmethod
    # def process_return(mapped_values):
    #     """
    #     Return results (numpy array) as list. 
    #     """
    #     if len(mapped_values) != 0:
    #         return list(mapped_values)
    #     else:
    #         return ["no_mapping"]



    # Local Example...
    # local_map = {
    #     "numeric": [[["HR"], ["8867-4"]], [["ABP-S"], ["76215-3"]]],
    #     "waveform": [[["PLETH"], ["76523-0"]]],
    # }



    # local_loinc = LoincMapper(local_mapping=local_map)
    # print(f"LOINC code(s) for local HR numeric: {local_loinc.numeric('HR')}")
    # print(f"local label for 76215-3: {local_loinc.numeric_reverse('76215-3')}")
    # print(f"LOINC code(s) for local PLETH waveform: {local_loinc.waveform('PLETH')}")
    # print(f"local label for 76523-0: {local_loinc.waveform_reverse('76523-0')}")

    # # External Example...
    # MIMICIII_loinc = LoincMapper(external_mapping="MIMICIII")
    # print(f"LOINC code(s) for M3 ABP SYS numeric: {MIMICIII_loinc.numeric('ABP SYS')}")
    # print(f"MIMIC label for 76213-8: {MIMICIII_loinc.numeric_reverse('76213-8')}")
    # print(f"LOINC code(s) for M3 ART waveform: {MIMICIII_loinc.waveform('ART')}")
    # print(f"MIMIC label for 76284-9: {MIMICIII_loinc.waveform_reverse('76284-9')}")


    # def initialize_lookup_tables_with_dict_(self):
    #     """
    #     Internal method to generate label-loinc pair (cartesian product) for 
    #     items in adjacent label-code lists in mapping_dict. Zips (list of tuple pairs) 
    #     and casts as 1D arrays to facilitate subset (boolean masking) and return 
    #     of mapped values in method calls below. 
    #     """

    #     num_products = []
    #     wf_products = []

    #     for mapping in self.numeric_mappings:
    #         num_product = list(product(mapping[0], mapping[1]))
    #         num_products.extend(num_product)

    #     for mapping in self.waveform_mappings:
    #         wf_product = list(product(mapping[0], mapping[1]))
    #         wf_products.extend(wf_product)

    #     numerics = list(zip(*num_products))
    #     waveforms = list(zip(*wf_products))

    #     self.label_num, self.loinc_num = np.array(numerics[0]), np.array(numerics[1])
    #     self.label_wf, self.loinc_wf = np.array(waveforms[0]), np.array(waveforms[1])

    # def numeric(self, value):
    #     mapped_values = np.unique(self.loinc_num[self.label_num == value])
    #     return self.process_return(mapped_values)

    # def numeric_reverse(self, value):
    #     mapped_values = np.unique(self.label_num[self.loinc_num == value])
    #     return self.process_return(mapped_values)

    # def waveform(self, value):
    #     mapped_values = np.unique(self.loinc_wf[self.label_wf == value])
    #     return self.process_return(mapped_values)

    # def waveform_reverse(self, value):
    #     mapped_values = np.unique(self.label_wf[self.loinc_wf == value])
    #     return self.process_return(mapped_values)
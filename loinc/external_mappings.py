# -*- coding: utf-8 -*-
# @Author: Alex Hamilton - https://github.com/alexhamiltonRN
# @Date: 2020-08-27
# @Desc: Regenerate with python (pull requests welcome)

import json

MIMICIII = {
    "numeric": [
        [["HR", "PULSE"], ["8867-4"]],
        [["RESP"], ["76174-2"]],
        [["%SpO2", "dSpO2", "SpO2", "SpO2 L", "SpO2 R"], ["76522-2"]],
        [["NBPSys", "NBP Sys", "NBP SYS"], ["76534-7"]],
        [["NBPDias", "NBP Dias", "NBP DIAS"], ["76535-4"]],
        [["NBPMean", "NBP Mean", "NBP MEAN", "NBP"], ["76536-2"]],
        [["ABP SYS", "ABP Sys", "ABPSys", "ART Sys"], ["76215-3"]],
        [["ABP DIAS", "ABP Dias", "ABPDias"], ["76213-8"]],
        [["ABP MEAN", "ABP Mean", "ABPMean", "ART Mean", "ABP"], ["76214-6"]],
        [["CVP"], ["60985-9"]],
        [["PAP SYS", "PAP Sys", "PAPSys"], ["8440-0", "8441-8", "8442-6"]],
        [["PAP DIAS", "PAP Dias", "PAPDias"], ["8385-7", "8368-5", "8387-3"]],
        [["PAP MEAN", "PAP Mean", "PAPMean"], ["8414-5", "8415-2", "8416-0"]],
        [["PAWP"], ["75994-4"]],
        [["AOBP Sys"], ["TBD"]],
        [["AOBP Dias"], ["TBD"]],
        [["AOBP Mean"], ["TBD"]]
    ],
    "waveform": [
        [["ART"], ["76212-0"]],
        [["PAP"], ["76284-9"]],
        [["CVP"], ["60985-9"]],
    ]
}

KHSC = {
    "numeric": [],
    "waveform": []
}

with open("./mappings/MIMICIII.json", "w") as write_file:
    json.dump(MIMICIII, write_file)

with open("./mappings/khsc.json", "w") as write_file:
    json.dump(KHSC, write_file)
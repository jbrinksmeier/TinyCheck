#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from classes.zeekengine import ZeekEngine
from classes.suricataengine import SuricataEngine
from multiprocessing import Process, Manager
import sys
import re
import json
import os

"""
    This file is called by the frontend but the analysis
    can be done in standalone by just submitting the directory
    containing a capture.pcap file.
"""

if __name__ == "__main__":
    if len(sys.argv) == 2:
        capture_directory = sys.argv[1]
        if os.path.isdir(capture_directory):

            # Alerts bucket.
            manager = Manager()
            alerts = manager.dict()

            def zeekengine(alerts):
                zeek = ZeekEngine(capture_directory)
                zeek.start_zeek()
                alerts["zeek"] = zeek.get_alerts()

            def snortengine(alerts):
                suricata = SuricataEngine(capture_directory)
                suricata.start_suricata()
                alerts["suricata"] = suricata.get_alerts()

            # Start the engines.
            p1 = Process(target=zeekengine, args=(alerts,))
            p2 = Process(target=snortengine, args=(alerts,))
            p1.start()
            p2.start()

            # Wait to their end.
            p1.join()
            p2.join()

            # Some formating and alerts.json writing.
            with open(os.path.join(capture_directory, "alerts.json"), "w") as f:
                report = {"high": [], "moderate": [], "low": []}
                for alert in (alerts["zeek"] + alerts["suricata"]):
                    if alert["level"] == "High":
                        report["high"].append(alert)
                    if alert["level"] == "Moderate":
                        report["moderate"].append(alert)
                    if alert["level"] == "Low":
                        report["low"].append(alert)
                f.write(json.dumps(report))
        else:
            print("The directory doesn't exist.")
    else:
        print("Please specify a capture directory in argument.")

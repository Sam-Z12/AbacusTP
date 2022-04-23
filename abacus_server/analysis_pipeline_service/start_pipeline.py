import time
import os
from os import path
import importlib

from abacus_server.analysis_pipeline_service import data_decision_manager, data_source_manager, data_analysis_manager
from abacus_server.crypto_service.events_interface import CryptoServiceEventsManager

"""GET file paths for each analysis pipeline(data_sources, data_analyses, data_decisions))"""
#############################################################################################
PARENT_DIR: str = path.dirname(__file__)
DATA_SOURCE_FILEPATH = f"{PARENT_DIR}/data_sources"
DATA_ANALYSES_FILEPATH = f"{PARENT_DIR}/data_analyses"
DATA_DECISION_FILEPATH = f"{PARENT_DIR}/data_decisions"


"""Parse each data_source, data_analysis and data_desicion file and get a reference 
    to an object that represents the contents of the file. Pass the objects to their respective managers"""
######################################################################################################


def grab_data_sources(source_files: list):
    """Args:
        dir_path: str -> path to the directory containing data source files"""
    data_source_objects = []
    try:
        for file in source_files:
            if file.endswith("_source.py"):
                base_file_name = file[:-3]
                import_mod_name = f"abacus_server.analysis_pipeline_service.data_sources.{base_file_name}"
                module = importlib.import_module(import_mod_name)
                data_source_class = module.DataSource()
                data_source_objects.append(data_source_class)
        return data_source_objects
    except Exception as e:
        print(f"ERROR {e} could not parse data_sources directory")


def grab_data_analyses(analysis_files: list):
    data_analysis_objects = []
    try:
        for file in analysis_files:
            if file.endswith("_analysis.py"):
                base_file_name = file[:-3]
                import_mod_name = f"abacus_server.analysis_pipeline_service.data_analyses.{base_file_name}"
                module = importlib.import_module(import_mod_name)
                data_analysis_class = module.DataAnalysis()
                data_analysis_objects.append(data_analysis_class)
        return data_analysis_objects
    except Exception as e:
        print("ERROR {e} could not parse data_analyses directory")


def grab_data_decisions(decision_files: list):
    data_decision_objects = []
    try:
        for file in decision_files:
            if file.endswith("_decision.py"):
                base_file_name = file[:-3]
                import_mod_name = f"abacus_server.analysis_pipeline_service.data_decisions.{base_file_name}"
                module = importlib.import_module(import_mod_name)
                data_decision_class = module.DataDecision()
                data_decision_objects.append(data_decision_class)
        print(f"DECISIONS {data_decision_objects}")
        return data_decision_objects
    except Exception as e:
        print(f"ERROR {e} could not parse data_decision directory")


def start_pipeline():
    """INIT required interfaces to each service. Must be called in a __name__ == '__main__:'"""
    ###################################################################################
    csem = CryptoServiceEventsManager()

    ds = data_source_manager.DataSourceManager()
    da = data_analysis_manager.DataAnalysisManager()
    dd = data_decision_manager.DataDecisionManager()

    decision_files = os.listdir(DATA_DECISION_FILEPATH)
    initial_data_decisions = grab_data_decisions(decision_files=decision_files)
    dd.add_many_decisions(initial_data_decisions)

    analysis_files = os.listdir(DATA_ANALYSES_FILEPATH)
    initial_data_analyses = grab_data_analyses(analysis_files=analysis_files)
    da.append_multiple_data_analyses(initial_data_analyses)

    source_files = os.listdir(DATA_SOURCE_FILEPATH)
    initial_data_sources = grab_data_sources(source_files=source_files)
    ds.append_multiple_data_sources(initial_data_sources)


if __name__ == "__main__":
    """INIT required interfaces to each service."""
    ###################################################################################
    csem = CryptoServiceEventsManager()

    ds = data_source_manager.DataSourceManager()
    da = data_analysis_manager.DataAnalysisManager()
    dd = data_decision_manager.DataDecisionManager()

    decision_files = os.listdir(DATA_DECISION_FILEPATH)
    initial_data_decisions = grab_data_decisions(decision_files=decision_files)
    dd.add_many_decisions(initial_data_decisions)

    analysis_files = os.listdir(DATA_ANALYSES_FILEPATH)
    initial_data_analyses = grab_data_analyses(analysis_files=analysis_files)
    #print(f"ANALYSIS: {initial_data_analyses}")
    da.append_multiple_data_analyses(initial_data_analyses)

    source_files = os.listdir(DATA_SOURCE_FILEPATH)
    initial_data_sources = grab_data_sources(source_files=source_files)
    ds.append_multiple_data_sources(initial_data_sources)

    time.sleep(10)
    ds.terminate()
    csem.runner.stop()
    da.terminate()
    dd.terminate()

"""
Tests for core.case_study.MetaOct2021CaseStudy
Verifies the explanatory post-mortem modeling of Meta's October 4, 2021 incident topology.
"""

import pytest
from core.case_study import MetaOct2021CaseStudy

def test_meta_post_mortem_model_analysis():
    case_study = MetaOct2021CaseStudy()
    res = case_study.run_post_mortem_analysis()

    assert res["totalNodesInGraph"] == 11
    assert res["incidentOriginNode"] == "Backbone BGP Router Config"
    assert res["topScoringNode"] == "Backbone BGP Router Config"
    assert res["originRanksFirst"] is True
    assert res["cascadeResult"]["blastRadiusPercentage"] == 100.0
    assert res["cascadeResult"]["totalFailedNodes"] == 11
    assert "methodologyNote" in res
    assert "post-mortem" in res["caseStudyName"].lower()

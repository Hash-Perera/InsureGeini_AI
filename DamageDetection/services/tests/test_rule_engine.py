from services.utils.BussinessRulesEngine import evaluate_rules

def test_repair_dent_minor():
    input_data = {
        "part": "door",
        "severity": "minor",
        "damageType": ["dent"],
        "obd_code": False
    }
    result = evaluate_rules(input_data)
    assert result["decision"] == "Repair"

def test_replace_dent_moderate_with_obd():
    input_data = {
        "part": "door",
        "severity": "moderate",
        "damageType": ["dent"],
        "obd_code": True
    }
    result = evaluate_rules(input_data)
    assert result["decision"] == "Replace"

def test_repair_dent_moderate_without_obd():
    input_data = {
        "part": "door",
        "severity": "moderate",
        "damageType": ["dent"],
        "obd_code": False
    }
    result = evaluate_rules(input_data)
    assert result["decision"] == "Repair"

def test_replace_crack():
    input_data = {
        "part": "mirror",
        "severity": "any",
        "damageType": ["crack"],
        "obd_code": False
    }
    result = evaluate_rules(input_data)
    assert result["decision"] == "Replace"

def test_null_decision_when_type_unknown():
    input_data = {
        "part": "roof",
        "severity": "any",
        "damageType": ["No Type Detected"],
        "obd_code": False
    }
    result = evaluate_rules(input_data)
    assert result["decision"] == "Null"

def test_replace_dent_severe():
    input_data = {
        "part": "bumper",
        "severity": "severe",
        "damageType": ["dent"],
        "obd_code": False
    }
    result = evaluate_rules(input_data)
    assert result["decision"] == "Replace"

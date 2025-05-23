# ai_model_pipeline/utils/rule_engine.py

from business_rules.engine import run_all
from business_rules.variables import BaseVariables, string_rule_variable, boolean_rule_variable
from business_rules.actions import BaseActions, rule_action

# Store decisions dynamically for each part
rule_decisions = {}

# -------------------------------
# Variables (Input Conditions)
# -------------------------------
class DamageVariables(BaseVariables):
    def __init__(self, part_data):
        self.part_data = part_data

    @string_rule_variable
    def damage_type(self):
        return self.part_data.get("damage_type", "")

    @string_rule_variable
    def severity(self):
        return self.part_data.get("severity", "")

    @boolean_rule_variable
    def obd_code(self):
        return self.part_data.get("obd_code", False)


# -------------------------------
# Actions (What to do per rule)
# -------------------------------
class DamageActions(BaseActions):
    def __init__(self, part_name):
        self.part_name = part_name

    @rule_action()
    def repair(self):
        rule_decisions[self.part_name] = {
            "decision": "Repair", "reason": "Rule matched: repair"
        }

    @rule_action()
    def replace(self):
        rule_decisions[self.part_name] = {
            "decision": "Replace", "reason": "Rule matched: replace"
        }

    @rule_action()
    def null_decision(self):
        rule_decisions[self.part_name] = {
            "decision": "Null", "reason": "No Damage Type detected."
        }

# -------------------------------
# Business Rules
# -------------------------------
business_rules = [
    {
        "conditions": {
            "all": [
                {"name": "damage_type", "operator": "equal_to", "value": "dent"},
                {"name": "severity", "operator": "equal_to", "value": "minor"}
            ]
        },
        "actions": [{"name": "repair"}]
    },
    {
        "conditions": {
            "all": [
                {"name": "damage_type", "operator": "equal_to", "value": "dent"},
                {"name": "severity", "operator": "equal_to", "value": "moderate"},
                {"name": "obd_code", "operator": "is_true", "value": True}
            ]
        },
        "actions": [{"name": "replace"}]
    },
    {
        "conditions": {
            "all": [
                {"name": "damage_type", "operator": "equal_to", "value": "dent"},
                {"name": "severity", "operator": "equal_to", "value": "moderate"},
                {"name": "obd_code", "operator": "is_false", "value": False}
            ]
        },
        "actions": [{"name": "repair"}]
    },
    {
        "conditions": {
            "all": [
                {"name": "damage_type", "operator": "equal_to", "value": "scratch"}
            ]
        },
        "actions": [{"name": "repair"}]
    },
    {
        "conditions": {
            "any": [
                {"name": "damage_type", "operator": "equal_to", "value": "crack"},
                {"name": "damage_type", "operator": "equal_to", "value": "glass shatter"},
                {"name": "damage_type", "operator": "equal_to", "value": "lamp broken"}
            ]
        },
        "actions": [{"name": "replace"}]
    },
    {
        "conditions": {
            "all": [
                {"name": "damage_type", "operator": "equal_to", "value": "dent"},
                {"name": "severity", "operator": "equal_to", "value": "severe"}
            ]
        },
        "actions": [{"name": "replace"}]
    },
    {
        "conditions": {
            "all": [
                {"name": "damage_type", "operator": "equal_to", "value": "No Type Detected"}
            ]
        },
        "actions": [{"name": "null_decision"}]
    }
]


# -------------------------------
# Rule Evaluation Entry Point
# -------------------------------
def evaluate_rules(damaged_parts):
    global rule_decisions
    rule_decisions = {}

    part_name = damaged_parts["part"]
    severity = damaged_parts["severity"]
    damage_types = damaged_parts["damageType"]
    obd_code = damaged_parts.get("obd_code", False)

    for damage_type in damage_types:
        part_data = {
            "damage_type": damage_type,
            "severity": severity,
            "obd_code": obd_code
        }

        run_all(
            rule_list=business_rules,
            defined_variables=DamageVariables(part_data),
            defined_actions=DamageActions(part_name),
            stop_on_first_trigger=True
        )

    if part_name in rule_decisions:
        damaged_parts["decision"] = rule_decisions[part_name]["decision"]
        damaged_parts["reason"] = rule_decisions[part_name]["reason"]

    return damaged_parts

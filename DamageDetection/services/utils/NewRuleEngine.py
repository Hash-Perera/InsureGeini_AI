# ai_model_pipeline/utils/rule_engine.py
from experta import *

# Store decisions dynamically for each part
rule_decisions = {}

class Damage(Fact):
    """Fact: Represents a damaged part"""
    pass

class InsuranceClaimEngine(KnowledgeEngine):

    def __init__(self):
        super().__init__()
        self.rule_decisions = {}

    @Rule(Damage(damage_type='dent', severity='minor'))
    def rule_1(self):
        part = self.facts[1]['part']
        self.rule_decisions[part] = {"decision": "Repair", "reason": "Low severity dent."}

    @Rule(Damage(damage_type='dent', severity='moderate', obd_code=True))
    def rule_2(self):
        part = self.facts[1]['part']
        self.rule_decisions[part] = {"decision": "Replace", "reason": "OBD detected issue with moderate dent."}

    @Rule(
    Damage(damage_type='dent', severity='moderate'),
    OR(Damage(obd_code=False), Damage(obd_code=None))
    )
    def rule_3(self):
        part = self.facts[1]['part']
        self.rule_decisions[part] = {"decision": "Repair", "reason": "Moderate dent but no OBD issue."}

    @Rule(Damage(damage_type='scratch'))
    def rule_4(self):
        part = self.facts[1]['part']
        self.rule_decisions[part] = {"decision": "Repair", "reason": "Scratch detected."}

    @Rule(OR(Damage(damage_type='crack'), Damage(damage_type='glass shatter'), Damage(damage_type='lamp broken')))
    def rule_5(self):
        part = self.facts[1]['part']
        self.rule_decisions[part] = {"decision": "Replace", "reason": "Major damage detected."}

    @Rule(Damage(damage_type='dent', severity='severe'))
    def rule_6(self):
        part = self.facts[1]['part']
        self.rule_decisions[part] = {"decision": "Replace", "reason": "High severity dent."}

    @Rule(Damage(damage_type='No Type Detected'))
    def rule_7(self):
        part = self.facts[1]['part']
        self.rule_decisions[part] = {"decision": "Null", "reason": "No Damage Type detected."}
        
def evaluate_rules(damaged_parts):
    """
    Evaluates the given damaged parts against predefined rules
    and returns the decision.
    """

    global rule_decisions
    rule_decisions = {}  # Reset decisions storage

    part_name = damaged_parts["part"]
    severity = damaged_parts["severity"]
    damage_types = damaged_parts["damageType"]  # List of damages
    obd_code = damaged_parts.get("obd_code", None)  # Handle future OBD sensor data

    engine = InsuranceClaimEngine()
    engine.reset()

    # Evaluate each damage type separately
    for damage_type in damage_types:
        case_data = {"part": part_name, "damage_type": damage_type, "severity": severity}
        if obd_code is not None:
            case_data["obd_code"] = obd_code
        else:
            case_data["obd_code"] = None

        # print(case_data)
        # Declare facts in the knowledge engine
        engine.declare(Damage(**case_data))

        engine.run()

    # Retrieve decision
    if part_name in engine.rule_decisions:
        damaged_parts["decision"] = engine.rule_decisions[part_name]["decision"]
        damaged_parts["reason"] = engine.rule_decisions[part_name]["reason"]
        # print(damaged_parts)
    
    return damaged_parts

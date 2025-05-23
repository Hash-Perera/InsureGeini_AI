# ai_model_pipeline/utils/rule_engine.py
# from durable.lang import *

# # Store decisions dynamically for each part
# rule_decisions = {}

# with ruleset('repair_or_replace'):

#     @when_all((m.damage_type == 'dent') & (m.severity == 'minor'))
#     def rule_1(c):
#         rule_decisions[c.m.part] = {"decision": "Repair", "reason": "Low severity dent."}

#     @when_all((m.damage_type == 'dent') & (m.severity == 'moderate') & (m.obd_code == True))
#     def rule_2(c):
#         rule_decisions[c.m.part] = {"decision": "Replace", "reason": "OBD detected issue with moderate dent."}

#     @when_all((m.damage_type == 'dent') & (m.severity == 'moderate') & ((m.obd_code == False) | (m.obd_code == None)))
#     def rule_3(c):
#         rule_decisions[c.m.part] = {"decision": "Repair", "reason": "Moderate dent but no OBD issue."}

#     @when_all(m.damage_type == 'scratch')
#     def rule_4(c):
#         rule_decisions[c.m.part] = {"decision": "Repair", "reason": "Scratch detected."}

#     @when_all((m.damage_type == 'crack') | (m.damage_type == 'glass shatter') | (m.damage_type == 'lamp broken'))
#     def rule_5(c):
#         rule_decisions[c.m.part] = {"decision": "Replace", "reason": "Major damage detected."}

#     @when_all((m.damage_type == 'dent') & (m.severity == 'severe'))
#     def rule_6(c):
#         rule_decisions[c.m.part] = {"decision": "Replace", "reason": "High severity dent."}

# def evaluate_rules(damaged_parts):
    
#     global rule_decisions
#     rule_decisions = {}  # Reset decisions storage

#     part_name = damaged_parts["part"]
#     severity = damaged_parts["severity"]
#     damage_types = damaged_parts["damageType"]  # List of damages
#     obd_code = damaged_parts.get("obd_code", None)  # Handle future OBD sensor data

#         # Evaluate each damage type separately
#     for damage_type in damage_types:
#         case_data = {'part': part_name, 'damage_type': damage_type, 'severity': severity}
#         if obd_code is not None:
#             case_data['obd_code'] = obd_code
#         else:
#             case_data['obd_code'] = None

#         # print(case_data)

#         # Pass case to the rule engine
#         post('repair_or_replace', case_data)

#         for part in rule_decisions:
#             decision = rule_decisions.get(part).get("decision")
#             reason = rule_decisions.get(part).get("reason")
#             damaged_parts["decision"] = decision
#             damaged_parts["reason"] = reason


    # for part in damaged_parts:
    #     part_name = part["part"]
    #     severity = part["severity"]
    #     damage_types = part["damageType"]  # List of damages
    #     obd_code = part.get("obd_code", None)  # Handle future OBD sensor data

    #     # Evaluate each damage type separately
    #     for damage_type in damage_types:
    #         case_data = {'part': part_name, 'damage_type': damage_type, 'severity': severity}
    #         if obd_code is not None:
    #             case_data['obd_code'] = obd_code
    #         else:
    #             case_data['obd_code'] = None

    #         # print(case_data)

    #         # Pass case to the rule engine
    #         post('repair_or_replace', case_data)

    

    # Return the final decisions
    #return [{"part": part, "decision": rule_decisions.get(part, {"decision": "Unknown", "reason": "No matching rule found"})} for part in rule_decisions]

    # return damaged_parts
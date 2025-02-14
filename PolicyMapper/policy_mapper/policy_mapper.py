import json
import os

class PolicyMapper:
    """Compares the generated damage report with extracted insurance policy rules."""

    def __init__(self, policy_file="policies.json"):
        self.policy_file = policy_file
        self.policies = self.load_policies()

    def load_policies(self):
        """Loads extracted insurance policies from JSON."""
        if not os.path.exists(self.policy_file):
            print(f"⚠️ No policy file found: {self.policy_file}. Skipping policy check.")
            return {}

        try:
            with open(self.policy_file, 'r') as file:
                policies = json.load(file)

                # Convert list of policies to dictionary for faster lookup
                if isinstance(policies, list):
                    return {policy["policy_number"]: policy for policy in policies}
                return policies

        except Exception as e:
            print(f"❌ Error loading policy file: {e}")
            return {}

    def evaluate_claim(self, report_data):
        """Compares a claim with the insurance policy to determine acceptance."""

        # Ensure `insurance_policy` key exists in report_data
        if "insurance_policy" not in report_data or not report_data["insurance_policy"]:
            print("⚠️ No insurance policy found in report data. Setting default.")
            report_data["insurance_policy"] = {"policy_number": "Unknown"}
            return {"status": "Rejected", "reason": "Missing insurance policy details"}

        policy_number = report_data["insurance_policy"].get("policy_number")

        if not policy_number or policy_number not in self.policies:
            return {"status": "Rejected", "reason": f"Invalid or missing policy number: {policy_number}"}

        policy = self.policies[policy_number]

        # Check if damage type is covered
        if report_data["damage_cause"] not in policy["covered_damage_types"]:
            return {"status": "Rejected", "reason": f"Damage type '{report_data['damage_cause']}' is not covered"}

        # Check exclusions
        for exclusion in policy["exclusions"]:
            if exclusion.lower() in report_data["incident_description"].lower():
                return {"status": "Rejected", "reason": f"Claim falls under exclusion: {exclusion}"}

        # Check coverage amount
        estimated_cost = report_data.get("estimated_repair_cost", 0)
        if estimated_cost > policy["max_coverage_amount"]:
            return {"status": "Rejected", "reason": "Repair cost exceeds policy coverage limit"}

        return {"status": "Accepted", "reason": "Claim meets all policy conditions"}

# Example Usage
if __name__ == "__main__":
    sample_claim = {
        "insurance_policy": {"policy_number": "ABC123"},
        "damage_cause": "Accidents",
        "incident_description": "The car was hit while parked at a red light.",
        "estimated_repair_cost": 8000
    }

    policy_mapper = PolicyMapper()
    decision = policy_mapper.evaluate_claim(sample_claim)
    print("🚀 Claim Decision:", decision)

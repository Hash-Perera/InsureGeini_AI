import json
import os
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate

class PolicyMapper:
    """Evaluates the generated damage report critically against extracted insurance policy rules using an LLM."""

    def __init__(self, policy_file="policies.json", model="llama3.2"):
        self.policy_file = policy_file
        self.policies = self.load_policies()
        self.llm = OllamaLLM(model=model)  # Using LLM for claim evaluation

    def load_policies(self):
        """Loads extracted insurance policies from JSON."""
        if not os.path.exists(self.policy_file):
            print(f"⚠️ No policy file found: {self.policy_file}. Skipping policy check.")
            return []

        try:
            with open(self.policy_file, 'r') as file:
                policies = json.load(file)
                return policies if isinstance(policies, list) else []
        except Exception as e:
            print(f"❌ Error loading policy file: {e}")
            return []

    def evaluate_claim(self, report_data):
        """Critically evaluates claim information against extracted policies using LLM."""

        # Ensure `insurance_policy` exists in report_data
        if "insurance_policy" not in report_data or not report_data["insurance_policy"]:
            report_data["insurance_policy"] = {"policy_number": "Unknown"}

        # Prepare structured policy evaluation prompt
        prompt_template = PromptTemplate(
            input_variables=["claim_data", "policies"],
            template="""
            You are an expert in insurance claims. Analyze the following **insurance claim report** 
            and compare it with the **insurance policies** provided. Your task is to determine if the claim should be 
            **accepted or rejected**, providing a **detailed reason**.

            **Claim Details:**
            {claim_data}

            **Extracted Insurance Policies:**
            {policies}

            Consider the following factors:
            - If no exact policy number matches, compare coverage details critically.
            - Ensure the **damage cause is covered** under at least one policy.
            - Ensure the claim does **not fall under exclusions**.
            - Ensure the **repair cost is within coverage limits**.
            - Provide a **detailed reason** for the claim decision.

            **Return a JSON response in the following format:**
            ```json
            {{
                "status": "Accepted" or "Rejected",
                "reason": "Detailed explanation of why the claim was accepted or rejected."
            }}
            ```

            Ensure strict JSON formatting with no extra text.
            """
        )

        # Format claim details and policies
        formatted_prompt = prompt_template.format(
            claim_data=json.dumps(report_data, indent=4),
            policies=json.dumps(self.policies, indent=4)
        )

        # Invoke the LLM for claim evaluation
        response = self.llm.invoke(formatted_prompt)

        # Parse the LLM response
        try:
            decision = json.loads(response.strip())
            if "status" in decision and "reason" in decision:
                return decision
            else:
                print("Error: LLM response missing required fields.")
                return {"status": "Rejected", "reason": "LLM failed to provide a structured explanation."}
        except json.JSONDecodeError:
            print("Error: Failed to parse LLM response.")
            return {"status": "Rejected", "reason": "Error processing claim evaluation."}

# Example Usage
if __name__ == "__main__":
    sample_claim = {
        "insurance_policy": {"policy_number": "UNKNOWN123"},
        "damage_cause": "Collision",
        "incident_description": "The car was hit while parked at a red light.",
        "estimated_repair_cost": 8000
    }

    policy_mapper = PolicyMapper()
    decision = policy_mapper.evaluate_claim(sample_claim)
    print("🚀 Claim Decision:", decision)

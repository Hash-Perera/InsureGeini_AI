import json
import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

rag_details = {
  "policies": [
    {
      "section": "Damage to or Loss of Vehicle",
      "coverage": [
        "Indemnity for loss of or damage to motor vehicle and its accessories and spare parts.",
        "Excludes accidental external means, fire, explosion, lightning, theft, and malicious acts.",
        "Does not cover consequential loss, depreciation, wear and tear, mechanical breakdown, or electrical failure."
      ],
      "amount_details": {
        "excess_amount": "Rs 1000 for cars",
        "specific_limits": [
          "Damage to tyres, tubes, rubber items, engine parts, wire harness and sensors: Liability not exceeding 50% of the loss or replacement cost.",
          "Damage to windscreen/windows on buses, motor coaches, omnibuses: Exceeding 10% of the cost."
        ]
      }
    },
    {
      "section": "Liability to Third Parties",
      "coverage": [
        "Legal liability for death, bodily injury, or property damage caused to third parties.",
        "Includes legal costs and expenses for defense and claims."
      ],
      "amount_details": {
        "private_cars": {
          "death_injury": "Unlimited",
          "property_damage": "Rs 10 million per event"
        }
      }
    },
    {
      "section": "Medical Expenses (Private Cars Only)",
      "coverage": [
        "Medical expenses for bodily injury to the insured or occupants (excluding paid driver or attendants)."
      ],
      "amount_details": {
        "limit": "Rs. 1500 per accident"
      }
    },
    {
      "section": "No Claim Bonus",
      "coverage": [
        "Bonus is awarded for claim-free years, applied at policy renewal."
      ],
      "amount_details": {
        "maximum_bonus": "70% after 12 consecutive claim-free years",
        "bonus_scale": [
          "1 year: 10%",
          "2 years: 15%",
          "3 years: 20%",
          "4 years: 25%",
          "5 years: 30%",
          "6 years: 35%",
          "7 years: 40%",
          "8 years: 45%",
          "9 years: 50%",
          "10 years: 55%",
          "11 years: 60%",
          "12 years: 65%",
          "13 years: 70%"
        ]
      }
    },
    {
      "section": "Battery and Inverter Damage (Electric Vehicles)",
      "coverage": [
        "Covers damage to the battery and/or inverter if the vehicle sustains other damage at the same time."
      ],
      "amount_details": {
        "limit": "10% of the insured value or market value of the vehicle, whichever is less"
      }
    },
    {
      "section": "Towing Charges",
      "coverage": [
        "Covers towing charges for vehicles to the nearest repair facility."
      ],
      "amount_details": {
        "limit": "Rs. 1000 for cars"
      }
    },
    {
      "section": "Strike, Riot and Civil Commotion Endorsement",
      "coverage": [
        "Covers losses caused by strikes, riots, and civil commotion."
      ],
      "amount_details": {
        "exclusions": [
          "Damage caused by terrorism",
          "Losses connected to military or government actions"
        ]
      }
    },
    {
      "section": "Air Bag Extension",
      "coverage": [
        "Covers the cost of new airbag replacement in case of damage to the vehicle."
      ],
      "amount_details": {
        "limit": "As per the schedule of the policy, covering airbag replacement costs."
      }
    },
    {
      "section": "Comprehensive Insurance",
      "coverage": [
        "Covers all damages to the vehicle except for the following: ",
        "Wear and tear",
        "Mechanical breakdown",
        "Electrical failure",
        "Consequential loss",
        "Depreciation",
        "Wear and tear",
        "Damage to tyres, tubes",
        
      ],
      "amount_details": {
        "limit": "Full coverage for the vehicle"
      }
    }
  ]
}


def evaluate_claim_using_llma(claim_data, damage_detection_data, vehicle_data) -> dict:
    """
    Evaluates insurance claims for each damaged part and returns a detailed JSON object for each part.

    Args:
        claim_data (dict): Claim-specific details (e.g., insuranceId, damagedAreas, location, weather).
        damage_detection_data (list): List of damage entries for each damaged part.
        vehicle_data (dict): Vehicle-specific details (e.g., vehicleModel, insurancePolicy, VIN).
        rag_details (dict): Insurance policy coverage details.

    Returns:
        dict: A detailed JSON object containing evaluations for each damaged part, including their IDs.
    """
    vehicle_model = vehicle_data.get('vehicleModel', 'Unknown Model')
    vehicle_color = vehicle_data.get('vehicleColor', 'Unknown Color')
    insurance_policy = vehicle_data.get('insurancePolicy', 'Unknown Policy')
    vin_number = vehicle_data.get('vinNumber', 'Unknown VIN')
    number_plate = vehicle_data.get('vehicleNumberPlate', 'Unknown Plate')
    damaged_areas = claim_data.get('damagedAreas', [])
    location = claim_data.get('location', {})
    weather = claim_data.get('weather', 'Unknown Weather')

    detailed_results = []

    for damage in damage_detection_data:
        damage_id = damage.get('_id', 'Unknown ID')
        part_damaged = damage.get('part', 'Unknown Part')
        damage_type = ', '.join(damage.get('damageType', []))
        severity = damage.get('severity', 'Unknown Severity')
        decision = damage.get('decision', 'Unknown Decision')
        reason = damage.get('reason', 'Unknown Reason')
        cost = damage.get('cost', 0.0)
        obd_code = damage.get('obd_code', False)
        internal_damage = damage.get('internal', 'No internal damage reported')
        flag = damage.get('flag', 'No flags')
        fraud_verification = claim_data.get('fraud_verification', {})
        print("FRAUD VERIFICATION" ,fraud_verification)
        
        #fraud_result = all(value.lower() == 'true' for value in fraud_verification.values())
        fraud_result = all(fraud_verification.values())
        
        
        print("FRAUD VERIFICATION", fraud_result)

        prompt = f"""
        You are an insurance claims evaluator. Given the claim details, policy coverage, and vehicle details below, determine whether the claim should be approved or rejected. Provide the reasoning for your decision. 
        Ensure that the decision is always valid, either "approved" or "rejected". Do not leave any decision ambiguous. Consider the severity of the damage, the policy exclusions, and the claim amount. Consider if fraud result is false reject the claim giving the reason "Fraud detected. One or more verifications failed." .

        CLAIM DETAILS:
        - Claim ID: {claim_data.get('insuranceId', 'Unknown')}
        - Damaged Areas: {', '.join(damaged_areas)}
        - Location: Latitude {location.get('latitude', 'Unknown')}, Longitude {location.get('longitude', 'Unknown')}
        - Weather: {weather}
        - Part Damaged: {part_damaged}
        - Damage Type: {damage_type}
        - Severity: {severity}
        - Decision: {decision}
        - Reason: {reason}
        - Cost: {cost}
        - OBD Code: {obd_code}
        - Internal Damage: {internal_damage}
        - Flag: {flag}
        
        VEHICLE DETAILS:
        - Vehicle Model: {vehicle_model}
        - Vehicle Color: {vehicle_color}
        - VIN Number: {vin_number}
        - Insurance Policy: {insurance_policy}
        - Vehicle Number Plate: {number_plate}

        INSURANCE POLICY COVERAGE:
        {json.dumps(rag_details, indent=2)}
    
        Based on the above information, return a JSON response with the following fields":
        - "status": "approved" or "rejected" (must always be valid)
        - "decision": "Repair" or "Replace"
        - "reason": A valid, reasoned explanation for your decision "
        - "cost": The claim cost"
        - "approved": Boolean indicating"
        """

        response = client.chat.completions.create(
            model="DeepSeek-R1-Distill-Llama-70b",
            messages=[
                {"role": "system", "content": "You are an expert insurance evaluator."},
                {"role": "user", "name": "insurance_agent", "content": prompt}
            ],
            temperature=0.5,
            top_p=1,
            stream=True,
            stop=None,
        )

        output = ""
        for chunk in response:
            output += chunk.choices[0].delta.content or ""

        output = output.split("```json")[1].split("```")[0]

        try:
            result = json.loads(output)
            if 'status' not in result or 'decision' not in result or 'reason' not in result:
                raise ValueError("Missing required fields in the response.")
            if fraud_result == False:
                print("Fraud detected. One or more verifications failed.")
                result['status'] = "rejected"
                result['decision'] = "rejected"
                result['reason'] = "Fraud detected. One or more verifications failed."
                result['cost'] = 0
                result['approved'] = False
        except (json.JSONDecodeError, ValueError):
            result = {
                "status": "rejected",
                "decision": decision,
                "reason": "The claim does not meet the coverage requirements or falls under exclusions such as wear and tear, mechanical failure, or damage not covered by the policy.",
                "cost": cost,
                "approved": False
            }
            

        if 'approved' not in result:
            result['approved'] = result['status'] == "approved"

        detailed_result = {
            "damage_id": str(damage_id),
            "part_damaged": part_damaged,
            "damage_type": damage_type,
            "severity": severity,
            "decision": decision,
            "reason": reason,
            "cost": cost,
            "obd_code": obd_code,
            "internal_damage": internal_damage,
            "flag": flag,
            "evaluation": result
        }

        detailed_results.append(detailed_result)

    total_cost = sum(damage.get('cost', 0.0) for damage in damage_detection_data)
    # Calculate the total approved costs
    approved_costs = sum(result['cost'] for result in detailed_results if result['evaluation']['approved'])
    #overall_status = "approved" if all(result['evaluation']['approved'] for result in detailed_results) else "rejected"
    overall_status = "Rejected" if all(not result['evaluation']['approved'] for result in detailed_results) else "Approved"
    reason = "All verifications passed." if fraud_result else "Fraud detected. One or more verifications failed."

    return {
        "overall_status": overall_status,
        "total_cost": total_cost,
        "damage_evaluations": detailed_results,
        "approved_costs": approved_costs,
        "reason": reason
    }


claim_data = {
    "_id": "67a1cacfeace4f9501a8c964",
    "insuranceId": "insuregeni-126735",
    "nicNo": "1957603405",
    "drivingLicenseNo": "244556651246",
    "damagedAreas": ["Front", "Right Side"],
    "location": {"latitude": 6.739595, "longitude": 80.094355},
    "userId": "6748472eae0fb7cdbf7190fa",
    "status": "Fraud Detection Completed",
    "insuranceFront": "https://example.com/insurance/front.png",
    "insuranceBack": "https://example.com/insurance/back.png",
    "nicFront": "https://example.com/nic/front.png",
    "nicBack": "https://example.com/nic/back.png",
    "drivingLicenseFront": "https://example.com/license/front.png",
    "drivingLicenseBack": "https://example.com/license/back.png",
    "driverFace": "https://example.com/driver/face.png",
    "frontLicencePlate": "https://example.com/plate/front.png",
    "backLicencePlate": "https://example.com/plate/back.png",
    "damageImages": [
        "https://example.com/damage/0.png",
        "https://example.com/damage/1.png",
        "https://example.com/damage/2.png"
    ],
    "createdAt": "2025-02-04T08:07:43.107Z",
    "vehicleId": "67d0532009cadf38a9976547",
    "vehicleFront": "https://example.com/vehicle/front.png",
    "imageLocation": {"latitude": 6.78839124153081, "longitude": 79.98140053856469},
    "locationAddress": "WV97+629 Colombo, Sri Lanka",
    "weather": "Clouds, scattered clouds",
    "audio": "https://example.com/audio.mp3",
    "audio_to_text": "I was driving when another car hit me from the side.",
    "fraud_verification": {
    "model_verified": "true",
    "face_verified": "true",
    "license_verified": "true",
    "insurance_verified": "true",
    "number_plates_verified": "true",
    "prev_damage_verified": "true",
    "vin_number_verified": "true",
    "color_verified": "true",
    "location_verified": "true",
    "fraud_verified": "true"
  }
}

damage_detection_data = [
    {
        "_id": "67d7227b232a3d73d4eafc0b",
        "claimId": "67a1cacfeace4f9501a8c964",
        "part": "damaged-door",
        "damageType": ["dent"],
        "severity": "moderate",
        "obd_code": False,
        "decision": "Repair",
        "reason": "Moderate dent but no OBD issue.",
        "image_url": "https://example.com/damage/door.jpg",
        "cost": 6000.0
    },
    {
        "_id": "67d7227b232a3d73d4eafc0c",
        "claimId": "67a1cacfeace4f9501a8c964",
        "part": "damaged-bumper",
        "damageType": ["scratch"],
        "severity": "minor",
        "obd_code": False,
        "decision": "Repair",
        "reason": "Minor scratch, no structural damage.",
        "image_url": "https://example.com/damage/bumper.jpg",
        "cost": 3000.0
    },
    {
        "_id": "67d82c9ec15120fe800ffc40",
        "claimId": "67a1cacfeace4f9501a8c964",
        "part": "damaged-windshield",
        "damageType": ["crack"],
        "severity": "severe",
        "obd_code": True,
        "internal": "Sensors damaged",
        "decision": "Replace",
        "reason": "Severe crack with OBD sensor damage.",
        "image_url": "https://example.com/damage/windshield.jpg",
        "cost": 15000.0,
        "flag": "Verify sensor replacement cost"
    }
]

vehicle_data = {
    "_id": "67d0532009cadf38a9976547",
    "userId": "6748472eae0fb7cdbf7190fa",
    "insuranceCard": {
        "front": "https://example.com/insurance/front.png",
        "back": "https://example.com/insurance/back.png"
    },
    "vehicleModel": "Toyota Corolla",
    "vehiclePhotos": {
        "front": "https://example.com/vehicle/front.png",
        "back": "https://example.com/vehicle/back.png",
        "left": "https://example.com/vehicle/left.png",
        "right": "https://example.com/vehicle/right.png"
    },
    "engineNo": "103004-b78",
    "chassisNo": "3624672323-09",
    "vinNumber": "345610",
    "vehicleColor": "ash",
    "vehicleNumberPlate": "KM7537",
    "numberPlateImages": {
        "front": "https://example.com/plate/front.png",
        "back": "https://example.com/plate/back.png"
    },
    "insurancePolicy": "Comprehensive Insurance"
}

#Example usage
#result = evaluate_claim_using_llma(claim_data, damage_detection_data, vehicle_data)
#print(json.dumps(result, indent=4))
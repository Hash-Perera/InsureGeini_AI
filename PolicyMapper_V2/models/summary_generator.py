import os
from groq import Groq

def generate_summary(user_data: dict, vehicle_data: dict, damage_detection_data: list[dict], claim_data: dict, transcribed_text: str) -> str:
    # Prepare the accident description from the provided data
    description = f"""
    User Details:
    - Name: {user_data.get('name')}
    - Email: {user_data.get('email')}
    - Mobile: {user_data.get('mobileNumber')}
    - Address: {user_data.get('address')}
    - Insurance ID: {user_data.get('insuranceId')}
    
    Vehicle Details:
    - Model: {vehicle_data.get('vehicleModel')}
    - Color: {vehicle_data.get('vehicleColor')}
    - Number Plate: {vehicle_data.get('vehicleNumberPlate')}
    - Engine No: {vehicle_data.get('engineNo')}
    - Chassis No: {vehicle_data.get('chassisNo')}
    - Insurance Policy: {vehicle_data.get('insurancePolicy')}
    
    Claim Details:
    - Insurance ID: {claim_data.get('insuranceId')}
    - Damage Areas: {', '.join(claim_data.get('damagedAreas', []))}
    - Location: {claim_data.get('locationAddress')}
    - Weather: {claim_data.get('weather')}
    - Claim Status: {claim_data.get('status')}
    
    Damage Detection:
    - Total Parts Damaged: {len(damage_detection_data)}
    - Details:
    
    Accident Description:
    - Description by the policy holder: {transcribed_text} 
    """
    
    # Add damage details
    for damage in damage_detection_data:
        description += f"\n      Part: {damage.get('part')}, Damage Type: {', '.join(damage.get('damageType', []))}, " \
                       f"Severity: {damage.get('severity')}" 
                       
                       

    # Create Groq client and call the Groq LLM model
    client = Groq(
        api_key=os.getenv("GROQ_API_KEY")
    )
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages = [
            {"role": "system", "content": "You are a professional report generator. Generate a clear and concise summary of the accident report in plain text format. Focus on key facts and avoid using any markdown formatting. Include relevant details about the vehicle, damage, and circumstances while maintaining a professional tone. Keep the summary factual and easy to read. The summary should be in the format of a report. Don't depend on the description by the policy holder to generate the summary. The summary should be based on the facts and the damage detection data."},
            {"role": "user", "name": "insurance_agent", "content": description}
        ],
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )
    
    output = response.choices[0].message.content
    return output

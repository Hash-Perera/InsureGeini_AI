from datetime import datetime

def collect_data(user_data: dict, vehicle_data: dict, damage_detection_data: dict, claim_data: dict):
    
   # Extracting damage parts information
    damage_parts = []
    for damage in damage_detection_data:
        damage_parts.append({
            "part": damage['part'],
            "cost": f"${damage['cost']}",
            "severity": damage['severity'].capitalize()
        })
    
    # Extracting photos
    photos = claim_data.get('damageImages', [])
    
    # Constructing the data dictionary
    data = {
        "vehicle_number_plate": vehicle_data.get('vehicleNumberPlate', 'N/A'),
        "vehicle_vin": vehicle_data.get('vinNumber', 'N/A'),
        "vehicle_make_model": vehicle_data.get('vehicleModel', 'N/A'),
        "report_date": datetime.now().strftime("%d.%m.%Y"),
        "fleet_manager": user_data.get('name', 'N/A'),
        "driver_name": user_data.get('name', 'N/A'),  # Assuming the user is the driver
        "driver_phone": user_data.get('mobileNumber', 'N/A'),
        "incident_date": claim_data.get('createdAt', datetime.now()).strftime("%d.%m.%Y - %H:%M"),
        "incident_location": claim_data.get('locationAddress', 'N/A'),
        "weather": claim_data.get('weather', 'N/A'),
        "damage_cause": "Rear-ended at a red light",  # Replace with actual cause if available
        "damage_parts": damage_parts,
        "incident_description": "A distracted driver failed to brake in time at a red light and collided with the rear of the insured vehicle. The impact resulted in a broken front bumper, minor dents on the hood, and a cracked left headlight.",
        "photos": photos,
        "incident_summary": "The vehicle sustained moderate damage. Repair costs are estimated at approximately $2,550. No injuries were reported, and both parties exchanged insurance information."
    }
    
    return data



   



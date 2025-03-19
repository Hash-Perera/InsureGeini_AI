from datetime import datetime
from multipledispatch import dispatch
from urllib.parse import urlparse
import os
import requests


@dispatch(dict, dict, list, dict, str)
def collect_data(user_data: dict, vehicle_data: dict, damage_detection_data: list[dict], claim_data: dict, incident_summary: str) -> dict:
    
   # Extracting damage parts information
    damage_parts = []
    for damage in damage_detection_data:
        damage_parts.append({
            "part": damage['part'],
            "cost": f"${damage['cost']}",
            "severity": damage['severity'].capitalize()
        })
    
    # Extracting photos
    photos = []
    for damage in damage_detection_data:
        if 'image_url' in damage:
            image_url = damage['image_url']
            local_path = f".{(claim_data.get('userId'))}/temp/images/{os.path.basename(urlparse(image_url).path)}"

            # Try to download the image
            try:
                response = requests.get(image_url, stream=True)
                if response.status_code == 200:
                    # Create the local directory if it doesn't exist
                    os.makedirs(os.path.dirname(local_path), exist_ok=True)

                    # Save the image to the local path
                    with open(local_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    photos.append(local_path)
                    print(f"Downloaded image: {image_url}")
                else:
                    print(f"Failed to download image from URL: {image_url}, Status code: {response.status_code}")
            except Exception as e:
                print(f"Error downloading image from URL {image_url}: {e}")

    print(f"Photos: {photos}")
    
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
        "incident_description": claim_data.get('audio_to_text', 'N/A'),
        "photos": photos,
        "incident_summary": incident_summary
    }
    
    return data


@dispatch(dict, dict, dict, str)
def collect_data(user_data: dict, vehicle_data: dict, policy_data: dict, incident_summary: str) -> dict:
    # Extracting damage parts information
    damage_parts = []
    total_estimation = 0
    approved_amount = 0

    for damage in policy_data['damage_evaluations']:
        damage_parts.append({
            "part": damage['part_damaged'],
            "cost": f"${damage['cost']}",
            "severity": damage['severity'].capitalize(),
            "decision": damage['evaluation']['decision'],
            "reason": damage['evaluation']['reason'],
            "status": damage['evaluation']['status']
        })
        total_estimation += damage['cost']
        if damage['evaluation']['approved']:
            approved_amount += damage['cost']

    # Extracting photos (assuming vehicle photos are used)
    photos = [
        vehicle_data['vehiclePhotos']['front'],
        vehicle_data['vehiclePhotos']['back'],
        vehicle_data['vehiclePhotos']['left'],
        vehicle_data['vehiclePhotos']['right']
    ]
    
    print("damage parts", damage_parts)

    # Constructing the data dictionary
    data = {
        "vehicle_number_plate": vehicle_data.get('vehicleNumberPlate', 'N/A'),
        "vehicle_vin": vehicle_data.get('vinNumber', 'N/A'),
        "vehicle_make_model": vehicle_data.get('vehicleModel', 'N/A'),
        "report_date": datetime.now().strftime("%d.%m.%Y"),
        "fleet_manager": user_data.get('name', 'N/A'),
        "driver_name": user_data.get('name', 'N/A'),  # Assuming the user is the driver
        "driver_phone": user_data.get('mobileNumber', 'N/A'),
        "incident_date": datetime.now().strftime("%d.%m.%Y - %H:%M"),  # Replace with actual incident date if available
        "incident_location": "N/A",  # Replace with actual location if available
        "weather": "N/A",  # Replace with actual weather if available
        "damage_cause": "Rear-ended at a red light",  # Replace with actual cause if available
        "damage_parts": damage_parts,
        "incident_description": incident_summary,  # Replace with actual description if available
        "photos": photos,
        "total_estimation": f"${total_estimation}",
        "approved_amount": f"${approved_amount}",
        "status_summary": policy_data['overall_status'].capitalize(),
       # "decision_with_reason": f"{policy_data['overall_status'].capitalize()} - {damage_parts[0]['reason']}"  # Example decision summary
    }

    return data
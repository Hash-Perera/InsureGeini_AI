from transformers import pipeline
import yaml

summarizer = pipeline("summarization")

def _generate_summary(text, max_length):
    """
    Generates a summary of the given text using a pre-trained summarization model.
    Args:
        text (str): The text to be summarized.
    Returns:
        str: The summarized text. If an error occurs during summarization, the original text is returned.
    Raises:
        Exception: If an error occurs during the summarization process, it is caught and printed.
    """

    try:
        summary = summarizer(text, max_length=max_length, min_length=50, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        print(f"Error summarizing: {e}")
        return text

def populate_report(data, transcript, transcript_length):
    """
    Populate a report dictionary with provided data.
    Args:
        data (dict): A dictionary containing the following keys:
            - registration_number (str): The registration number of the vehicle.
            - vin (str): The vehicle identification number.
            - year_make_model (str): The year, make, and model of the vehicle.
            - report_date_time (str): The date and time of the report.
            - fleet_manager_name (str): The name of the fleet manager.
            - driver_name (str): The name of the driver.
            - driver_license_photo (str): The photo of the driver's license.
            - driver_phone (str): The phone number of the driver.
            - incident_date_time (str): The date and time of the incident.
            - incident_location (dict): A dictionary containing the address of the incident location.
            - weather_condition (str): The weather condition during the incident.
            - damage_severity (str): The severity of the damage.
            - damage_cause (str): The cause of the damage.
            - witnesses (list): A list of witnesses.
            - comments (str): Additional comments.
            - driver_signature (str): The signature of the driver.
            - fleet_manager_signature (str): The signature of the fleet manager.
    Returns:
        dict: A dictionary containing the populated report.
    """

    report = {
        "registration_number": data["registration_number"],
        "vin": data["vin"],
        "year_make_model": data["year_make_model"],
        "report_date_time": data["report_date_time"],
        "fleet_manager_name": data["fleet_manager_name"],
        "audit": {
            "general_information": {
                "driver_name": data["driver_name"],
                "photo_driver_license": data["driver_license_photo"],
                "driver_phone": data["driver_phone"]
            },
            "damage_details": {
                "incident_date_time": data["incident_date_time"],
                "incident_location": data["incident_location"],
                "weather_condition": data["weather_condition"],
                "damage_severity": data["damage_severity"],
                "damage_cause": data["damage_cause"],
                "incident_description": _generate_summary(f"The incident occurred at {data['incident_location']['address']} during {data['weather_condition']} weather. The damage is {data['damage_severity']} due to {data['damage_cause']}. Other information: {transcript}", transcript_length),
                "photos_vehicle_damage": [],
                "photo_sketch": "",
                "photos_surrounding": []
            },
            "other_party_involved": {},
            "witnesses": data["witnesses"]
        },
        "summary": {
            "comments": data["comments"]
        },
        "acknowledgment": {
            "driver_signature": data["driver_signature"],
            "fleet_manager_signature": data["fleet_manager_signature"]
        },
        "media_summary": []
    }
    return report


def save_report_to_yaml(report, filename="vehicle_incident_report.yaml"):
    """
    Save a report to a YAML file.
    Args:
        report (dict): The report data to be saved.
        filename (str, optional): The name of the YAML file to save the report to. Defaults to "vehicle_incident_report.yaml".
    Returns:
        None
    """

    with open(filename, 'w') as file:
        yaml.dump(report, file, default_flow_style=False)
        print(f"Report saved as {filename}")



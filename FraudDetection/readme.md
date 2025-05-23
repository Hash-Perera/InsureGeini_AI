#Create Python virtual environment to manage packages for specific project
python -m venv virtual

#Activate virtual environment powershell command
.\virtual\Scripts\Activate

#Deactivate virtual environment powershell command
deactivate

NOTE: Always acitvate the virtual environment before run the app and install dependancies.

Generate requirements.txt
pip freeze > requirements.txt

Update requirement.txt
pip install --upgrade -r requirements.txt

Install dependancies from requirement.txt
pip install -r requirements.txt

Run the main
uvicorn main:app --reload

Fraud Detection
Version 1.0.0

=========== Create ECS First Deployement =============

removed tensorfloor_intel package

1. docker build -t fraud_detection .
2. docker run --env-file .env -p 8002:8002 fraud_detection

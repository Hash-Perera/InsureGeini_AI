#from utils.RuleEngine import evaluate_rules
from services.utils.BussinessRulesEngine import evaluate_rules
from services.database import db
from bson import ObjectId

async def estimate_claim(unified_vector,claimId):
    #Temporary datastore for part prices
    part_prices = {
        "Runningboard-Damage": 100,
        "damage-front-windscreen": 300,
        "damaged-door": 90000,
        "damaged-fender": 300,
        "damaged-front-bumper": 200,
        "damaged-head-light": 150,
        "damaged-hood": 400,
        "damaged-rear-bumper": 150,
        "damaged-rear-window": 300,
        "damaged-roof": 350,
        "damaged-side-window": 250,
        "damaged-tail-light": 150,
        "damaged-trunk": 350,
        "damaged-windscreen": 300,
        "quaterpanel-dent": 200,
    }

    repair_time = {
        "minor": 6,
        "moderate": 12,
        "scratch": 20,
    }

    part_times = {
        "Runningboard-Damage": 4,
        "damage-front-windscreen": 1,
        "damaged-door": 6,
        "damaged-fender": 4,
        "damaged-front-bumper": 3,
        "damaged-head-light": 2,
        "damaged-hood": 5,
        "damaged-rear-bumper": 3,
        "damaged-rear-window": 4,
        "damaged-roof": 4,
        "damaged-side-window": 4,
        "damaged-tail-light": 2,
        "damaged-trunk": 4,
        "damaged-windscreen": 4,
        "quaterpanel-dent": 6,
    }

    labour_cost = 500
    total_cost=0

    for damage in unified_vector:
        # descision = evaluate_rules(damage)
        descision = evaluate_rules(damage)
        

        if descision["decision"] == "Replace":
            #get part price from database
            #get part time from database
            #get vehicle model from database
            
            try:

                vehicleIdDoc = await db.claims.find_one({"_id": ObjectId(claimId)},{"vehicleId":1, "_id": 0})

                if not vehicleIdDoc:
                    raise ValueError(f"Claim ID '{claimId}' not found.")

                vehicleId = vehicleIdDoc["vehicleId"]

                vehicle = await db.vehicles.find_one({"_id": vehicleId},{"vehicleModel":1, "_id": 0})

                if not vehicle:
                    raise ValueError(f"Vehicle with ID '{vehicleId}' not found.")
                
                model = vehicle["vehicleModel"]

                doc = await db.part_prices.find_one({"part": damage["part"], "model": model},{"_id": 0, "price": 1, "time": 1})

                if not doc:
                    raise ValueError(f"No price info for part '{damage['part']}' and model '{model}'.")
                
                price=doc["price"]
                time=doc["time"]
                
                #get labor cost from database
                damage["severity"] = "severe"
                replacement_cost = price + (labour_cost * time)
                damage["cost"] = replacement_cost

            except Exception as db_error:
                print("Error fetching data from database:", db_error)
                # If the part price is not found in the database, use the temporary datastore
                damage["cost"] = 0
                damage["decision"] = "Null"
                damage["reason"] = f"DB lookup failed for replacement: {str(db_error)}"
                print(f"[DB ERROR] Failed for part '{damage.get('part')}'. Reason: {db_error}")

        else:
            for type in damage["damageType"]:   
                
                if type == "dent":
                    
                    if damage["severity"] == "minor":
                        repair_cost = labour_cost * repair_time.get("minor",0)
                    else:
                        repair_cost = labour_cost * repair_time.get("moderate",0)
                    
                    damage["cost"] = repair_cost
                else:
                    repair_cost = labour_cost * repair_time.get("scratch",0)
                    damage["cost"] = repair_cost
                
            
        total_cost = total_cost + damage.get("cost", 0)

    return total_cost
#from utils.RuleEngine import evaluate_rules
from services.utils.NewRuleEngine import evaluate_rules

def estimate_claim(unified_vector):
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
            #get labor cost from database
            damage["severity"] = "severe"
            replacement_cost = part_prices.get(damage["part"],0) + (labour_cost * part_times.get(damage["part"],0))
            damage["cost"] = replacement_cost
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
                
            
        total_cost = total_cost + damage["cost"]

    return total_cost
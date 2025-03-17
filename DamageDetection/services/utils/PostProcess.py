#Add post processing combine the results in to an single vector

from collections import defaultdict

class PostProcess:
    
    def compute_intersection(self,part_box,type_box):
        x1,y1,x2,y2 = part_box
        x1_t,y1_t,x2_t,y2_t = type_box

        x_left = max(x1, x1_t)
        y_top = max(y1, y1_t)
        x_right = min(x2, x2_t)
        y_bottom = min(y2, y2_t)

        intersection_area = max(0, x_right - x_left) * max(0, y_bottom - y_top)

        type_box_area = (x2_t - x1_t) * (y2_t - y1_t)  # Width × Height

        precentage_overlap = intersection_area / type_box_area
        
        return precentage_overlap
    
    def match_damage_to_part(self,damaged_parts, damage_types, i_threshold=0.7):
        
        #matches = defaultdict(list)  # Dictionary to store matched results
        matched_parts = []  # List to store matched parts
        count = 0
        # Loop through each detected damaged part
        for part_id, (part_box, part_label) in enumerate(damaged_parts):

            matched_damages = []
            matchfound = False

            #count += 1
            # Loop through each detected damage type
            for damage_id, (damage_box, damage_label) in enumerate(damage_types):
                intersection = self.compute_intersection(part_box, damage_box)  # Compute Intersection precentage between part and damage type

                if intersection >= i_threshold:
                    #matches[str(count)+" "+part_label].append(damage_label)
                    matched_damages.append(damage_label)
                    matchfound = True

            if not matchfound:
                matched_damages.append("No Type Detected")

            
            matched_parts.append({
                "id": part_id+1,
                "part": part_label,
                "damageType": matched_damages,
            })

        return matched_parts
    
    def create_vector(self,partSeverity,damageParts):
        
        if len(damageParts) != len(partSeverity):
            print("Error: Length of part severity and damage parts do not match.")
            return None
        
        for i,part in enumerate(damageParts):
            if i< len(partSeverity):
                part_name,severity = partSeverity[i]
                if part["part"] == part_name:
                    part["severity"] = severity
                
        return damageParts
    
    #To be changed or removed
    def create_unified_vector(self,external_vector):
        unified_vector = external_vector
        for damage in unified_vector:
            damage['obd_code'] = False

        return unified_vector
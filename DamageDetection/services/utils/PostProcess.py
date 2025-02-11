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
        
        matches = defaultdict(list)  # Dictionary to store matched results
        count = 0
        # Loop through each detected damaged part
        for part_id, (part_box, part_label) in enumerate(damaged_parts):

            matchfound = False

            count += 1
            # Loop through each detected damage type
            for damage_id, (damage_box, damage_label) in enumerate(damage_types):
                intersection = self.compute_intersection(part_box, damage_box)  # Compute Intersection precentage between part and damage type

                if intersection >= i_threshold:
                    matches[str(count)+" "+part_label].append(damage_label)
                    matchfound = True

            if not matchfound:
                matches[str(count)+" "+part_label].append("No Type Detected")

        return matches
    
    def create_vector(self,partSeverity,damageType):
        merged_data = []
        for part,severity in partSeverity:
            merged_data.append({"part":part, "damageType":damageType.get(part,[]), "severity":severity, })

        return merged_data
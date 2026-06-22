def classify_department(description):
    """
    Simple keyword-based classification for department assignment.
    """
    desc_lower = description.lower()
    if 'road' in desc_lower or 'pothole' in desc_lower or 'street' in desc_lower:
        return 'PWD'
    elif 'garbage' in desc_lower or 'waste' in desc_lower or 'overflow' in desc_lower:
        return 'Municipality'
    elif 'water' in desc_lower or 'leak' in desc_lower or 'shortage' in desc_lower:
        return 'Water Department'
    elif 'light' in desc_lower or 'electric' in desc_lower or 'power' in desc_lower:
        return 'Electricity'
    else:
        return 'Municipality'  # default
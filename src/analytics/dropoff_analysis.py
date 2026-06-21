"""Analyze drop-offs between funnel stages"""

def compute_dropoff(start, end):
    if start:
        return (start - end) / start
    return None

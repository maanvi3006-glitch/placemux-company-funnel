"""Compute conversion metrics like CTR, CVR"""

def ctr(clicks, impressions):
    return clicks / impressions if impressions else None

"""
Request Utilities
Helper functions for extracting request information
"""
from fastapi import Request


def get_client_ip(request: Request) -> str:
    """
    Get client IP address from request
    Handles proxy headers (X-Forwarded-For, X-Real-IP)
    """
    # Check for forwarded IP (when behind proxy/load balancer)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs, take the first one
        ip = forwarded_for.split(",")[0].strip()
        return ip
    
    # Check for real IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Fallback to direct client IP
    if request.client:
        return request.client.host
    
    return "unknown"


def get_user_agent(request: Request) -> str:
    """
    Get user agent (browser/device info) from request
    """
    return request.headers.get("User-Agent", "unknown")


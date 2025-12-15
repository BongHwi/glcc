"""
KR Tracker Adapter

This module interfaces with the delivery-tracker service for Korean carriers.
The delivery-tracker runs as a separate GraphQL service (port 4000).

Note: delivery-tracker service must be running for this adapter to work.
You can start it with: docker compose up -d (from the submodule directory)
"""

import requests
import json
from typing import Optional, Dict, Any

# GraphQL endpoint for delivery-tracker service
TRACKER_ENDPOINT = "http://localhost:4000/graphql"

def track_kr(carrier: str, tracking_number: str) -> Dict[str, Any]:
    """
    Track package using Korean delivery tracker service

    Args:
        carrier: Carrier ID (e.g., 'kr.cj', 'kr.hanjin', 'kr.epost')
        tracking_number: Tracking number

    Returns:
        Dictionary with tracking information

    Example:
        >>> result = track_kr('kr.cj', '1234567890')
        >>> print(result['status'])
    """

    # GraphQL query for tracking
    query = """
    query Track($carrierId: ID!, $trackingNumber: String!) {
        track(carrierId: $carrierId, trackingNumber: $trackingNumber) {
            from {
                name
                time
            }
            to {
                name
                time
            }
            state {
                id
                text
            }
            progresses {
                time
                location {
                    name
                }
                status {
                    id
                    text
                }
                description
            }
            carrier {
                id
                name
            }
        }
    }
    """

    variables = {
        "carrierId": carrier,
        "trackingNumber": tracking_number
    }

    try:
        response = requests.post(
            TRACKER_ENDPOINT,
            json={"query": query, "variables": variables},
            timeout=10
        )
        response.raise_for_status()

        data = response.json()

        if "errors" in data:
            return {
                "success": False,
                "error": data["errors"][0]["message"],
                "carrier": carrier,
                "tracking_number": tracking_number
            }

        track_data = data.get("data", {}).get("track", {})

        return {
            "success": True,
            "carrier": carrier,
            "tracking_number": tracking_number,
            "status": track_data.get("state", {}).get("text", "Unknown"),
            "from": track_data.get("from", {}),
            "to": track_data.get("to", {}),
            "progresses": track_data.get("progresses", []),
            "raw_data": track_data
        }

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": f"Failed to connect to tracker service: {str(e)}",
            "carrier": carrier,
            "tracking_number": tracking_number,
            "note": "Make sure delivery-tracker service is running on port 4000"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "carrier": carrier,
            "tracking_number": tracking_number
        }

def get_supported_carriers() -> Dict[str, Any]:
    """
    Get list of supported Korean carriers

    Returns:
        Dictionary with list of supported carriers
    """

    query = """
    query {
        carriers {
            id
            name
            displayName
        }
    }
    """

    try:
        response = requests.post(
            TRACKER_ENDPOINT,
            json={"query": query},
            timeout=10
        )
        response.raise_for_status()

        data = response.json()
        carriers = data.get("data", {}).get("carriers", [])

        # Filter only Korean carriers
        kr_carriers = [c for c in carriers if c.get("id", "").startswith("kr.")]

        return {
            "success": True,
            "carriers": kr_carriers,
            "count": len(kr_carriers)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

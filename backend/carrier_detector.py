"""
Carrier Detection Module

Automatically detects carrier from tracking number patterns.
Uses regex-based pattern matching with priority ordering.
"""

import re
from typing import Dict, List, Optional, Any


# Carrier pattern registry (ordered by priority, highest first)
CARRIER_PATTERNS: List[Dict[str, Any]] = [
    # High priority - Suffix patterns (most specific)
    {
        "carrier": "global.jppost",
        "name": "Japan Post",
        "priority": 10,
        "patterns": [
            {
                "type": "suffix",
                "regex": r"^[A-Z]{2}\d{9}JP$",
                "description": "Ends with JP (e.g., EN123456789JP)"
            }
        ]
    },

    # High priority - Specific prefixes
    {
        "carrier": "global.ups",
        "name": "UPS",
        "priority": 9,
        "patterns": [
            {
                "type": "prefix",
                "regex": r"^1Z[A-Z0-9]{16}$",
                "description": "Starts with 1Z, 18 chars total"
            }
        ]
    },
    {
        "carrier": "global.chinapost",
        "name": "China Post",
        "priority": 9,
        "patterns": [
            {
                "type": "prefix",
                "regex": r"^(RB|RC|RA|CP|LZ|LM|LO|EA|EB|EC|ED|EE|EF|EG|EH|EI|EJ|EK|EL|EM|ZC)[A-Z0-9]{9,}(CN)?$",
                "description": "Starts with specific China Post prefixes"
            }
        ]
    },

    # Medium priority - Length-based patterns
    {
        "carrier": "global.fedex",
        "name": "FedEx",
        "priority": 6,
        "patterns": [
            {
                "type": "length",
                "regex": r"^\d{12}$",
                "description": "12 digits"
            },
            {
                "type": "length",
                "regex": r"^\d{15}$",
                "description": "15 digits"
            }
        ]
    },
    {
        "carrier": "global.dhl",
        "name": "DHL",
        "priority": 5,
        "patterns": [
            {
                "type": "length",
                "regex": r"^\d{10,11}$",
                "description": "10-11 digits"
            }
        ]
    },
    {
        "carrier": "global.sagawa",
        "name": "Sagawa Express",
        "priority": 4,
        "patterns": [
            {
                "type": "length",
                "regex": r"^\d{10,12}$",
                "description": "10-12 digits"
            }
        ]
    },

    # Korean carriers - Low priority (generic patterns)
    {
        "carrier": "kr.cj",
        "name": "CJ Logistics",
        "priority": 3,
        "patterns": [
            {
                "type": "length",
                "regex": r"^\d{10,13}$",
                "description": "10-13 digits (Korean domestic)"
            }
        ]
    },
    {
        "carrier": "kr.hanjin",
        "name": "Hanjin",
        "priority": 3,
        "patterns": [
            {
                "type": "length",
                "regex": r"^\d{10,13}$",
                "description": "10-13 digits (Korean domestic)"
            }
        ]
    },
    {
        "carrier": "kr.epost",
        "name": "Korea Post",
        "priority": 3,
        "patterns": [
            {
                "type": "length",
                "regex": r"^\d{10,13}$",
                "description": "10-13 digits (Korean domestic)"
            }
        ]
    },
    {
        "carrier": "kr.lotte",
        "name": "Lotte",
        "priority": 3,
        "patterns": [
            {
                "type": "length",
                "regex": r"^\d{10,13}$",
                "description": "10-13 digits (Korean domestic)"
            }
        ]
    },
    {
        "carrier": "kr.kdexp",
        "name": "KD Express",
        "priority": 3,
        "patterns": [
            {
                "type": "length",
                "regex": r"^\d{10,13}$",
                "description": "10-13 digits (Korean domestic)"
            }
        ]
    },
    {
        "carrier": "kr.cjlogistics",
        "name": "CJ Logistics (Alternative)",
        "priority": 3,
        "patterns": [
            {
                "type": "length",
                "regex": r"^\d{10,13}$",
                "description": "10-13 digits (Korean domestic)"
            }
        ]
    }
]


def normalize_tracking_number(tracking_number: str) -> str:
    """
    Normalize tracking number for pattern matching

    Args:
        tracking_number: Raw tracking number input

    Returns:
        Normalized tracking number (uppercase, no spaces/hyphens)
    """
    if not tracking_number:
        return ""

    # Remove spaces and hyphens, convert to uppercase
    return tracking_number.strip().upper().replace(" ", "").replace("-", "")


def detect_carrier(tracking_number: str) -> Dict[str, Any]:
    """
    Detect carrier from tracking number pattern

    Args:
        tracking_number: Tracking number to analyze

    Returns:
        Dictionary with detection results:
        {
            "carrier": "global.jppost" or None,
            "confidence": "high" | "medium" | "low" | "none",
            "pattern_matched": "Ends with JP (e.g., EN123456789JP)",
            "tracking_number": "EN123456789JP"
        }
    """
    normalized = normalize_tracking_number(tracking_number)

    # Validation: minimum length
    if len(normalized) < 5:
        return {
            "carrier": None,
            "confidence": "none",
            "pattern_matched": None,
            "tracking_number": tracking_number,
            "error": "Tracking number too short (minimum 5 characters)"
        }

    # Sort patterns by priority (highest first)
    sorted_patterns = sorted(CARRIER_PATTERNS, key=lambda x: x["priority"], reverse=True)

    # Try to match patterns
    for carrier_info in sorted_patterns:
        for pattern in carrier_info["patterns"]:
            if re.match(pattern["regex"], normalized):
                # Found a match - determine confidence
                confidence = _determine_confidence(
                    carrier_info["priority"],
                    pattern["type"]
                )

                return {
                    "carrier": carrier_info["carrier"],
                    "confidence": confidence,
                    "pattern_matched": pattern["description"],
                    "tracking_number": tracking_number
                }

    # No match found
    return {
        "carrier": None,
        "confidence": "none",
        "pattern_matched": None,
        "tracking_number": tracking_number
    }


def _determine_confidence(priority: int, pattern_type: str) -> str:
    """
    Determine confidence level based on priority and pattern type

    Args:
        priority: Pattern priority (1-10)
        pattern_type: Type of pattern ("suffix", "prefix", "length")

    Returns:
        Confidence level: "high", "medium", or "low"
    """
    # High confidence: Priority >= 9 with specific patterns
    if priority >= 9 and pattern_type in ["suffix", "prefix"]:
        return "high"

    # Medium confidence: Priority >= 5 or prefix patterns
    if priority >= 5 or pattern_type == "prefix":
        return "medium"

    # Low confidence: Generic length-based patterns
    return "low"


def get_supported_carriers_with_patterns() -> Dict[str, Any]:
    """
    Get list of all carriers with their patterns

    Returns:
        Dictionary with carriers list and count
    """
    carriers_list = []

    # Remove duplicates by carrier ID
    seen_carriers = set()

    for carrier_info in CARRIER_PATTERNS:
        if carrier_info["carrier"] not in seen_carriers:
            carriers_list.append({
                "id": carrier_info["carrier"],
                "name": carrier_info["name"],
                "patterns": [p["description"] for p in carrier_info["patterns"]],
                "priority": carrier_info["priority"]
            })
            seen_carriers.add(carrier_info["carrier"])

    return {
        "carriers": sorted(carriers_list, key=lambda x: x["priority"], reverse=True),
        "count": len(carriers_list)
    }


def add_carrier_pattern(carrier_id: str, name: str, priority: int,
                       regex: str, pattern_type: str, description: str) -> None:
    """
    Dynamically add a new carrier pattern to the registry

    Args:
        carrier_id: Carrier identifier (e.g., "global.newcarrier")
        name: Human-readable carrier name
        priority: Pattern priority (1-10, higher = more specific)
        regex: Regular expression for matching
        pattern_type: Type of pattern ("suffix", "prefix", "length")
        description: Human-readable description of the pattern
    """
    CARRIER_PATTERNS.append({
        "carrier": carrier_id,
        "name": name,
        "priority": priority,
        "patterns": [
            {
                "type": pattern_type,
                "regex": regex,
                "description": description
            }
        ]
    })

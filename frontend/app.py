"""
GLCC Frontend Dashboard

Streamlit-based UI for managing package tracking
"""

import streamlit as st
import requests
import os
from datetime import datetime
import json

# Backend API URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(
    page_title="GLCC - Global Logistics Command Center",
    page_icon="📦",
    layout="wide"
)

def get_packages():
    """Fetch all packages from API"""
    try:
        response = requests.get(f"{BACKEND_URL}/packages")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch packages: {e}")
        return []

def add_package(tracking_number, carrier, alias, notify_enabled):
    """Add new package"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/packages",
            json={
                "tracking_number": tracking_number,
                "carrier": carrier,
                "alias": alias,
                "notify_enabled": notify_enabled
            }
        )
        response.raise_for_status()
        return True, "Package added successfully!"
    except Exception as e:
        return False, f"Failed to add package: {e}"

def refresh_all():
    """Refresh all packages"""
    try:
        response = requests.post(f"{BACKEND_URL}/packages/refresh")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to refresh packages: {e}")
        return None

def track_package(package_id):
    """Track specific package"""
    try:
        response = requests.post(f"{BACKEND_URL}/packages/{package_id}/track")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to track package: {e}")
        return None

def delete_package(package_id):
    """Delete package"""
    try:
        response = requests.delete(f"{BACKEND_URL}/packages/{package_id}")
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Failed to delete package: {e}")
        return False

def get_scheduler_status():
    """Get scheduler status"""
    try:
        response = requests.get(f"{BACKEND_URL}/scheduler/status")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return None

def detect_carrier_from_tracking(tracking_number):
    """Auto-detect carrier from tracking number"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/carriers/detect",
            json={"tracking_number": tracking_number}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return None

# Title
st.title("📦 GLCC - Global Logistics Command Center")
st.markdown("Self-hosted platform for tracking deliveries worldwide")

# Sidebar
with st.sidebar:
    st.header("System Status")

    # Health check
    try:
        health = requests.get(f"{BACKEND_URL}/health").json()
        st.success(f"Backend: {health.get('status', 'unknown')}")
    except:
        st.error("Backend: offline")

    # Scheduler status
    scheduler = get_scheduler_status()
    if scheduler:
        st.info(f"Scheduler: {'running' if scheduler.get('running') else 'stopped'}")
        if scheduler.get('jobs'):
            for job in scheduler['jobs']:
                if job.get('next_run_time'):
                    st.caption(f"Next run: {job['next_run_time']}")

    st.divider()

    # Refresh button
    if st.button("🔄 Refresh All Packages", use_container_width=True):
        with st.spinner("Refreshing all packages..."):
            result = refresh_all()
            if result:
                st.success(f"✅ Success: {result.get('success', 0)}/{result.get('total', 0)}")
                if result.get('failed', 0) > 0:
                    st.warning(f"⚠️ Failed: {result.get('failed', 0)}")
                st.rerun()

# Main content
tab1, tab2 = st.tabs(["📋 Package List", "➕ Add Package"])

# Tab 1: Package List
with tab1:
    packages = get_packages()

    if not packages:
        st.info("No packages found. Add your first package in the 'Add Package' tab!")
    else:
        st.subheader(f"Total Packages: {len(packages)}")

        # Filters
        col1, col2 = st.columns(2)
        with col1:
            filter_carrier = st.selectbox(
                "Filter by Carrier",
                ["All"] + list(set([p['carrier'] for p in packages]))
            )
        with col2:
            filter_active = st.checkbox("Active only", value=True)

        # Filter packages
        filtered_packages = packages
        if filter_carrier != "All":
            filtered_packages = [p for p in filtered_packages if p['carrier'] == filter_carrier]
        if filter_active:
            filtered_packages = [p for p in filtered_packages if p['is_active']]

        # Display packages
        for package in filtered_packages:
            with st.expander(
                f"📦 {package.get('alias', package['tracking_number'])} - {package.get('status', 'Unknown')}",
                expanded=False
            ):
                col1, col2, col3 = st.columns([2, 2, 1])

                with col1:
                    st.write("**Tracking Number:**", package['tracking_number'])
                    st.write("**Carrier:**", package['carrier'])
                    st.write("**Status:**", package.get('status', 'Unknown'))

                with col2:
                    st.write("**Alias:**", package.get('alias', 'N/A'))
                    st.write("**Last Updated:**", package.get('last_updated', 'N/A'))
                    st.write("**Active:**", "✅" if package['is_active'] else "❌")

                with col3:
                    if st.button("🔍 Track", key=f"track_{package['id']}"):
                        with st.spinner("Tracking..."):
                            result = track_package(package['id'])
                            if result:
                                st.json(result)
                                st.rerun()

                    if st.button("🗑️ Delete", key=f"delete_{package['id']}"):
                        if delete_package(package['id']):
                            st.success("Package deleted!")
                            st.rerun()

                # Show tracking data if available
                if package.get('tracking_data'):
                    st.divider()
                    st.caption("📄 Raw Tracking Data")
                    try:
                        data = json.loads(package['tracking_data'])
                        st.json(data)
                    except:
                        st.text(package['tracking_data'])

# Tab 2: Add Package
with tab2:
    st.subheader("Add New Package")

    # Initialize session state for auto-detection
    if 'detected_carrier' not in st.session_state:
        st.session_state.detected_carrier = None
    if 'detection_message' not in st.session_state:
        st.session_state.detection_message = None

    # Auto-detect section (outside form for reactivity)
    tracking_number_input = st.text_input(
        "Tracking Number *",
        placeholder="Enter tracking number (e.g., EN387436585JP)",
        key="tracking_input"
    )

    col_detect1, col_detect2 = st.columns([1, 3])
    with col_detect1:
        if st.button("🔍 Auto-detect Carrier", disabled=not tracking_number_input or len(tracking_number_input) < 5):
            with st.spinner("Detecting carrier..."):
                detection = detect_carrier_from_tracking(tracking_number_input)
                if detection and detection.get('carrier'):
                    st.session_state.detected_carrier = detection['carrier']
                    st.session_state.detection_message = f"✅ Detected: {detection['carrier']} ({detection.get('confidence', 'unknown')} confidence)"
                else:
                    st.session_state.detected_carrier = None
                    st.session_state.detection_message = "⚠️ Could not auto-detect carrier. Please select manually."

    with col_detect2:
        if st.session_state.detection_message:
            if "✅" in st.session_state.detection_message:
                st.success(st.session_state.detection_message)
            else:
                st.warning(st.session_state.detection_message)

    # Form for package details
    with st.form("add_package_form"):
        col1, col2 = st.columns(2)

        with col1:
            # Carrier list (updated with new carriers)
            carrier_list = [
                "kr.cj",
                "kr.hanjin",
                "kr.epost",
                "kr.lotte",
                "kr.kdexp",
                "kr.cjlogistics",
                "global.ups",
                "global.fedex",
                "global.dhl",
                "global.chinapost",
                "global.jppost",
                "global.sagawa"
            ]

            # Pre-select detected carrier if available
            default_index = 0
            if st.session_state.detected_carrier and st.session_state.detected_carrier in carrier_list:
                default_index = carrier_list.index(st.session_state.detected_carrier)

            carrier = st.selectbox(
                "Carrier *",
                carrier_list,
                index=default_index
            )

        with col2:
            alias = st.text_input(
                "Package Name (Optional)",
                placeholder="My Package"
            )

            notify_enabled = st.checkbox("Enable Notifications", value=True)

        st.caption("💡 Tip: Use 'Auto-detect Carrier' button above to automatically identify the carrier")
        st.caption("Korean carriers (kr.*) require delivery-tracker service running on port 4000")

        submitted = st.form_submit_button("➕ Add Package", use_container_width=True)

        if submitted:
            if not tracking_number_input or not carrier:
                st.error("Please fill in all required fields")
            else:
                with st.spinner("Adding package..."):
                    success, message = add_package(
                        tracking_number_input,
                        carrier,
                        alias if alias else None,
                        notify_enabled
                    )
                    if success:
                        st.success(message)
                        # Clear session state
                        st.session_state.detected_carrier = None
                        st.session_state.detection_message = None
                        st.rerun()
                    else:
                        st.error(message)

# Footer
st.divider()
st.caption("GLCC - Global Logistics Command Center | Powered by FastAPI + Streamlit")

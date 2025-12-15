import streamlit as st
import requests
import json
import uuid
import os
from datetime import datetime
import re

# Configuration
BASE_URL = "http://127.0.0.1:8000"
APP_NAME = "agent"
VIZ_DIR = os.path.join(os.path.dirname(__file__), "viz_outputs")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = f"s_{uuid.uuid4().hex[:8]}"
if "user_id" not in st.session_state:
    st.session_state.user_id = f"u_{uuid.uuid4().hex[:8]}"
if "session_created" not in st.session_state:
    st.session_state.session_created = False

def create_session(user_id, session_id):
    """Create a new session with the agent API"""
    try:
        url = f"{BASE_URL}/apps/{APP_NAME}/users/{user_id}/sessions/{session_id}"
        response = requests.post(url, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Failed to create session: {str(e)}")
        return False

# Page config
st.set_page_config(
    page_title="Olist Data Analyzer",
    page_icon="📊",
    layout="wide"
)

# Header
st.title("📊 Olist E-commerce Data Analyzer")
st.markdown("Ask questions about the Olist e-commerce database and get instant insights!")

# Sidebar with session info
with st.sidebar:
    st.header("Session Info")
    st.text(f"Session ID: {st.session_state.session_id}")
    st.text(f"User ID: {st.session_state.user_id}")
    
    if st.button("🔄 New Session"):
        st.session_state.session_id = f"s_{uuid.uuid4().hex[:8]}"
        st.session_state.messages = []
        st.session_state.session_created = False
        st.rerun()
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.header("Example Questions")
    st.markdown("""
    **📊 Data Analysis:**
    - What are the top 5 product categories by sales?
    - Show me average delivery time by state
    - Which sellers have the highest revenue?
    
    **📈 Visualizations:**
    - Create a bar chart of monthly sales trends
    - Visualize the distribution of review scores
    - Show a heatmap of orders by state and month
    - Plot revenue trends over time
    - Create a funnel of order status progression
    - Show geographic distribution of customers
    """)

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        content = message["content"]
        
        # Extract and display visualizations from message content
        viz_pattern = r'\[VIZ:([a-zA-Z0-9_]+\.png)\]'
        viz_matches = re.findall(viz_pattern, content)
        
        if viz_matches:
            # Remove [VIZ:filename] tags from text and display text
            text_content = re.sub(viz_pattern, '', content)
            if text_content.strip():
                st.markdown(text_content)
            
            # Display all images from this message
            for filename in viz_matches:
                filepath = os.path.join(VIZ_DIR, filename)
                if os.path.exists(filepath):
                    st.image(filepath, use_container_width=True)
                else:
                    st.warning(f"Visualization not found: {filename}")
        else:
            # No images, just display text
            st.markdown(content)

# Chat input
if prompt := st.chat_input("Ask me anything about the Olist database..."):
    # Create session if not already created
    if not st.session_state.session_created:
        with st.spinner("Creating session..."):
            if create_session(st.session_state.user_id, st.session_state.session_id):
                st.session_state.session_created = True
            else:
                st.error("Failed to create session. Please try again.")
                st.stop()
    
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Prepare request payload
    payload = {
        "appName": APP_NAME,
        "userId": st.session_state.user_id,
        "sessionId": st.session_state.session_id,
        "newMessage": {
            "role": "user",
            "parts": [{"text": prompt}]
        }
      
    }
    
    # Send request and get response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            with st.spinner("Thinking..."):
                # Make non-streaming request
                run_url = f"{BASE_URL}/run"
                response = requests.post(
                    run_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=120
                )
                response.raise_for_status()
                
                # Parse JSON response (array format)
                response_data = response.json()
                
                # Handle array response
                if isinstance(response_data, list):
                    for item in response_data:
                        if isinstance(item, dict) and 'content' in item:
                            content = item['content']
                            if isinstance(content, dict) and 'parts' in content:
                                for part in content['parts']:
                                    if 'text' in part:
                                        full_response += part['text']
                # Handle single object response
                elif isinstance(response_data, dict):
                    if 'content' in response_data:
                        content = response_data['content']
                        if isinstance(content, dict) and 'parts' in content:
                            for part in content['parts']:
                                if 'text' in part:
                                    full_response += part['text']
                        elif isinstance(content, str):
                            full_response = content
                
                # Extract and display visualization images from the response
                # Look for [VIZ:filename] pattern
                viz_pattern = r'\[VIZ:([a-zA-Z0-9_]+\.png)\]'
                viz_matches = re.findall(viz_pattern, full_response)
                
                if viz_matches:
                    # Remove [VIZ:filename] tags from text response
                    text_response = re.sub(viz_pattern, '', full_response)
                    message_placeholder.markdown(text_response)
                    
                    # Display images
                    for idx, filename in enumerate(viz_matches):
                        try:
                            filepath = os.path.join(VIZ_DIR, filename)
                            if os.path.exists(filepath):
                                st.image(filepath, use_container_width=True)
                            else:
                                st.error(f"Visualization file not found: {filename}")
                        except Exception as img_err:
                            st.error(f"Failed to display visualization {idx+1}: {str(img_err)}")
                else:
                    # No images, just display text
                    message_placeholder.markdown(full_response)
                
        except requests.exceptions.RequestException as e:
            error_msg = f"❌ Error connecting to agent: {str(e)}"
            message_placeholder.error(error_msg)
            full_response = error_msg
        except json.JSONDecodeError as e:
            error_msg = f"❌ Error parsing response: {str(e)}"
            message_placeholder.error(error_msg)
            full_response = error_msg
        except Exception as e:
            error_msg = f"❌ Unexpected error: {str(e)}"
            message_placeholder.error(error_msg)
            full_response = error_msg
    
    # Add assistant response to chat history
    if full_response:
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# Footer
st.divider()
st.caption("Powered by Google ADK Agent with MCP Tools")

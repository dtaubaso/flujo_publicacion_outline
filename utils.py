import streamlit as st

def authenticate_workspace():
    """Autenticación restringida a Google Workspace"""
    
    oauth_config = {
        "client_id": st.secrets["auth"]["client_id"],
        "client_secret": st.secrets["auth"]["client_secret"],
        "hosted_domain": st.secrets["auth"]["hosted_domain"],  # Esto restringe a tu empresa

    }
    
    if not st.login(provider="google", oauth_config=oauth_config):
        st.info("🔐 Inicia sesión con tu cuenta corporativa")
        st.stop()
    
    return st.context.user
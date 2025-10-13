import streamlit as st
import logging
import requests
from functools import wraps
from typing import Callable, Any

def handle_errors(func: Callable) -> Callable:
    """Decorator for handling errors gracefully in Streamlit"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.RequestException as e:
            st.error(f"🌐 Network Error: {str(e)}")
            st.info("Please check your internet connection and try again.")
            return None
        except ValueError as e:
            st.error(f"📊 Data Error: {str(e)}")
            st.info("There seems to be an issue with the profile data.")
            return None
        except Exception as e:
            st.error(f"⚠️ Unexpected Error: {str(e)}")
            st.info("Something went wrong. Please try again or contact support.")
            logging.error(f"Unexpected error in {func.__name__}: {e}")
            return None
    
    return wrapper
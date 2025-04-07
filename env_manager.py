# env_manager.py
import os
from dotenv import dotenv_values, set_key, unset_key

ENV_PATH = ".env"

def get_env_variables():
    return dotenv_values(ENV_PATH)

def set_env_variable(key, value):
    set_key(ENV_PATH, key, value)

def delete_env_variable(key):
    unset_key(ENV_PATH, key)
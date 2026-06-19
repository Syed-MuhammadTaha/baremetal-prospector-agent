# main.py
import os
from agent.engine import run_agent


if __name__ == "__main__":
    target = "Brainbox Automations"
    query = f"Research {target}. Find their official website, scrape it, and save a cold email dossier."
    
    run_agent(query)
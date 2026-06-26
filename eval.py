import concurrent.futures
import time
from agent.engine import run_agent
from agent.llm_as_judge import evaluate_email

TARGETS = [
    "Vercel - Frontend Cloud SaaS",
    "Nike - Massive Enterprise Retail",
    "Gymshark - E-commerce brand"
]

def evaluate_prospect(company: str):
    """Runs the agent, extracts the email, and grades it."""
    query = f"Research {company} and draft a highly personalized cold email pitching Sable's services."
    start_time = time.time()
    
    try:
        # 1. Run the Agent
        result = run_agent(query, max_steps=8)
        elapsed = time.time() - start_time
        metrics = result["metrics"]
        
        # 2. Extract the Final Email
        final_message = result["messages"][-1]["content"]
        # We assume the email was either in the Final Answer or the save_dossier tool call.
        # Let's extract the text after "Final Answer:"
        email_draft = final_message.split("Final Answer:")[-1].strip()
        
        # 3. Call the Judge
        scorecard = evaluate_email(email_draft)
        
        return {
            "company": company,
            "status": "PASS" if scorecard["passed"] else "FAIL",
            "score": scorecard["score"],
            "feedback": scorecard["feedback"],
            "iterations": metrics["iterations"],
            "time_sec": round(elapsed, 2)
        }
        
    except Exception as e:
        return {
            "company": company,
            "status": "ERROR",
            "score": 0,
            "feedback": str(e),
            "iterations": 0,
            "time_sec": round(time.time() - start_time, 2)
        }

def run_evals():
    print("🚀 STARTING SIMULTANEOUS EVALUATION HARNESS")
    print(f"🎯 Targets: {len(TARGETS)}\n")
    
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_company = {executor.submit(evaluate_prospect, comp): comp for comp in TARGETS}
        for future in concurrent.futures.as_completed(future_to_company):
            res = future.result()
            results.append(res)
            print(f"✅ Finished: {res['company']} | Score: {res['score']}/10")

    print("\n" + "="*95)
    print(f"{'COMPANY':<35} | {'STATUS':<7} | {'SCORE':<5} | {'LOOPS':<5} | {'FEEDBACK'}")
    print("="*95)
    for r in results:
        # Truncate feedback for the table
        fb = r['feedback'][:40] + "..." if len(r['feedback']) > 40 else r['feedback']
        print(f"{r['company'][:35]:<35} | {r['status']:<7} | {r['score']:<5} | {r['iterations']:<5} | {fb}")
    print("="*95)

if __name__ == "__main__":
    run_evals()
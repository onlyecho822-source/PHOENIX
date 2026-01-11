#!/usr/bin/env python3
"""
Agent Coordinator - Leadership Layer
Coordinates all autonomous agents and reports to humans
"""

import subprocess
import json
import time
from datetime import datetime

class AgentCoordinator:
    def __init__(self):
        self.agents = {
            "api_testing": {"script": "/tmp/free-apis-verified/test_all_apis_recursive.py", "status": "running"},
            "passive_income": {"script": "/tmp/passive-income-recon.py", "status": "ready"},
            "frankenstein": {"script": "/tmp/frankenstein_activate.py", "status": "ready"}
        }
        self.cycle = 0
    
    def check_agent_status(self, agent_name):
        """Check if agent process is running"""
        script = self.agents[agent_name]["script"]
        try:
            result = subprocess.run(f"pgrep -f {script}", shell=True, capture_output=True)
            return "running" if result.returncode == 0 else "stopped"
        except:
            return "unknown"
    
    def start_agent(self, agent_name):
        """Start an agent"""
        script = self.agents[agent_name]["script"]
        try:
            subprocess.Popen(f"nohup python3 {script} > /tmp/{agent_name}.log 2>&1 &", shell=True)
            return True
        except:
            return False
    
    def collect_results(self):
        """Collect results from all agents"""
        results = {}
        
        # API Testing
        try:
            with open("/tmp/free-apis-verified/complete_verification.json") as f:
                results["api_testing"] = json.load(f)
        except:
            results["api_testing"] = {"status": "in_progress"}
        
        # Passive Income
        try:
            with open("/tmp/passive_income_opportunities.json") as f:
                results["passive_income"] = json.load(f)
        except:
            results["passive_income"] = {"status": "pending"}
        
        # Frankenstein
        try:
            with open("/tmp/frankenstein_report.json") as f:
                results["frankenstein"] = json.load(f)
        except:
            results["frankenstein"] = {"status": "pending"}
        
        return results
    
    def make_decisions(self, results):
        """Agent makes autonomous decisions"""
        decisions = []
        
        # Decision 1: Run passive income scan every 6 hours
        if self.cycle % 6 == 0:
            decisions.append(("start_agent", "passive_income"))
        
        # Decision 2: Run Frankenstein every hour
        if self.cycle % 1 == 0:
            decisions.append(("start_agent", "frankenstein"))
        
        # Decision 3: Check if API testing needs restart
        api_status = self.check_agent_status("api_testing")
        if api_status == "stopped":
            decisions.append(("start_agent", "api_testing"))
        
        return decisions
    
    def execute_decisions(self, decisions):
        """Execute autonomous decisions"""
        for action, target in decisions:
            if action == "start_agent":
                success = self.start_agent(target)
                print(f"  → {action}: {target} - {'✓' if success else '✗'}")
    
    def send_leadership_report(self, results, decisions):
        """Send leadership report to humans"""
        report = f"""AGENT COORDINATOR - Leadership Report
Cycle: {self.cycle}
Time: {datetime.utcnow().isoformat()}

AGENT STATUS:
- API Testing: {self.check_agent_status('api_testing')}
- Passive Income: {self.check_agent_status('passive_income')}
- Frankenstein: {self.check_agent_status('frankenstein')}

DECISIONS MADE:
{chr(10).join(f'- {action}: {target}' for action, target in decisions)}

RESULTS SUMMARY:
- APIs Tested: {results.get('api_testing', {}).get('total_tested', 'N/A')}
- Income Opportunities: {len(results.get('passive_income', {}).get('opportunities', {}))}
- Pump/Dumps Detected: {results.get('frankenstein', {}).get('targets_detected', 'N/A')}

Next cycle in 1 hour.
"""
        
        # Email report
        subprocess.run([
            "manus-mcp-cli", "tool", "call", "gmail_send_messages",
            "--server", "gmail",
            "--input", json.dumps({
                "messages": [{
                    "to": ["npoinsette@gmail.com", "king.thedros@gmail.com"],
                    "subject": f"Agent Leadership Report - Cycle {self.cycle}",
                    "content": report
                }]
            })
        ], capture_output=True)
    
    def run(self):
        """Run coordinator loop"""
        print("Agent Coordinator starting...")
        print("Agents have leadership - making autonomous decisions\n")
        
        while True:
            self.cycle += 1
            print(f"\n{'='*70}")
            print(f"CYCLE {self.cycle} - {datetime.utcnow().isoformat()}")
            print(f"{'='*70}\n")
            
            # Collect data
            results = self.collect_results()
            
            # Make decisions
            decisions = self.make_decisions(results)
            print(f"Decisions: {len(decisions)}")
            
            # Execute
            self.execute_decisions(decisions)
            
            # Report to humans
            self.send_leadership_report(results, decisions)
            
            # Sleep 1 hour
            time.sleep(3600)

if __name__ == "__main__":
    coordinator = AgentCoordinator()
    coordinator.run()

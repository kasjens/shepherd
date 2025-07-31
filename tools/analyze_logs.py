#!/usr/bin/env python3
"""
Shepherd Log Analysis Tool
Helps analyze application logs for troubleshooting and debugging
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
import argparse
from collections import defaultdict, Counter
import re


class LogAnalyzer:
    def __init__(self, logs_dir="logs"):
        self.logs_dir = Path(logs_dir)
        self.structured_log = self.logs_dir / "shepherd_structured.log"
        self.main_log = self.logs_dir / "shepherd.log"
        self.error_log = self.logs_dir / "shepherd_errors.log"
    
    def analyze_errors(self, hours=24):
        """Analyze errors from the last N hours"""
        print(f"\n=== ERROR ANALYSIS (Last {hours} hours) ===")
        
        if not self.error_log.exists():
            print("No error log found")
            return
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        errors = []
        
        with open(self.error_log, 'r') as f:
            for line in f:
                try:
                    # Extract timestamp from log line
                    timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                    if timestamp_match:
                        timestamp = datetime.strptime(timestamp_match.group(1), '%Y-%m-%d %H:%M:%S')
                        if timestamp > cutoff_time:
                            errors.append((timestamp, line.strip()))
                except:
                    continue
        
        if not errors:
            print("No errors found in the specified time period")
            return
        
        print(f"Found {len(errors)} errors:")
        for timestamp, error in errors[-10:]:  # Show last 10 errors
            print(f"\n[{timestamp}] {error}")
    
    def analyze_workflows(self, limit=10):
        """Analyze recent workflow executions"""
        print(f"\n=== WORKFLOW ANALYSIS (Last {limit} workflows) ===")
        
        if not self.structured_log.exists():
            print("No structured log found")
            return
        
        workflows = {}
        
        with open(self.structured_log, 'r') as f:
            for line in f:
                try:
                    log_entry = json.loads(line)
                    
                    if 'extra' in log_entry and 'workflow_id' in log_entry.get('extra', {}):
                        workflow_id = log_entry['extra']['workflow_id']
                        
                        if workflow_id not in workflows:
                            workflows[workflow_id] = {
                                'id': workflow_id,
                                'start_time': None,
                                'end_time': None,
                                'pattern': None,
                                'status': None,
                                'errors': [],
                                'duration': None
                            }
                        
                        workflow = workflows[workflow_id]
                        
                        if 'started' in log_entry['message']:
                            workflow['start_time'] = log_entry['timestamp']
                            workflow['pattern'] = log_entry['extra'].get('pattern')
                        elif 'completed' in log_entry['message']:
                            workflow['end_time'] = log_entry['timestamp']
                            workflow['status'] = log_entry['extra'].get('status')
                            workflow['duration'] = log_entry['extra'].get('execution_time')
                            if log_entry['extra'].get('errors'):
                                workflow['errors'] = log_entry['extra']['errors']
                
                except json.JSONDecodeError:
                    continue
        
        # Sort by start time and show recent workflows
        recent_workflows = sorted(
            [w for w in workflows.values() if w['start_time']], 
            key=lambda x: x['start_time'], 
            reverse=True
        )[:limit]
        
        if not recent_workflows:
            print("No workflow data found")
            return
        
        for workflow in recent_workflows:
            print(f"\nWorkflow: {workflow['id'][:8]}...")
            print(f"  Pattern: {workflow['pattern']}")
            print(f"  Status: {workflow['status']}")
            print(f"  Duration: {workflow['duration']:.2f}s" if workflow['duration'] else "  Duration: Unknown")
            if workflow['errors']:
                print(f"  Errors: {len(workflow['errors'])}")
    
    def analyze_agents(self, limit=20):
        """Analyze agent performance"""
        print(f"\n=== AGENT ANALYSIS (Last {limit} actions) ===")
        
        if not self.structured_log.exists():
            print("No structured log found")
            return
        
        agent_stats = defaultdict(lambda: {'success': 0, 'failed': 0, 'total_time': 0.0, 'actions': []})
        
        with open(self.structured_log, 'r') as f:
            for line in f:
                try:
                    log_entry = json.loads(line)
                    
                    if (log_entry.get('logger') == 'shepherd.agent' and 
                        'extra' in log_entry and 
                        log_entry['extra'].get('agent_name')):
                        
                        agent_name = log_entry['extra']['agent_name']
                        status = log_entry['extra'].get('status')
                        duration = log_entry['extra'].get('duration', 0)
                        
                        agent_stats[agent_name]['actions'].append({
                            'timestamp': log_entry['timestamp'],
                            'action': log_entry['extra'].get('action'),
                            'status': status,
                            'duration': duration
                        })
                        
                        if status == 'completed':
                            agent_stats[agent_name]['success'] += 1
                        elif status == 'failed':
                            agent_stats[agent_name]['failed'] += 1
                        
                        agent_stats[agent_name]['total_time'] += duration
                
                except json.JSONDecodeError:
                    continue
        
        if not agent_stats:
            print("No agent data found")
            return
        
        for agent_name, stats in agent_stats.items():
            total_actions = stats['success'] + stats['failed']
            success_rate = (stats['success'] / total_actions * 100) if total_actions > 0 else 0
            avg_time = stats['total_time'] / total_actions if total_actions > 0 else 0
            
            print(f"\nAgent: {agent_name}")
            print(f"  Actions: {total_actions} (Success: {stats['success']}, Failed: {stats['failed']})")
            print(f"  Success Rate: {success_rate:.1f}%")
            print(f"  Avg Duration: {avg_time:.2f}s")
    
    def analyze_performance(self):
        """Analyze overall system performance"""
        print("\n=== PERFORMANCE ANALYSIS ===")
        
        if not self.structured_log.exists():
            print("No structured log found")
            return
        
        patterns_used = Counter()
        complexity_scores = []
        execution_times = []
        
        with open(self.structured_log, 'r') as f:
            for line in f:
                try:
                    log_entry = json.loads(line)
                    
                    if 'extra' in log_entry:
                        extra = log_entry['extra']
                        
                        if 'pattern' in extra:
                            patterns_used[extra['pattern']] += 1
                        
                        if 'complexity' in extra:
                            complexity_scores.append(extra['complexity'])
                        
                        if 'execution_time' in extra:
                            execution_times.append(extra['execution_time'])
                
                except json.JSONDecodeError:
                    continue
        
        if patterns_used:
            print("\nWorkflow Patterns Used:")
            for pattern, count in patterns_used.most_common():
                print(f"  {pattern}: {count}")
        
        if complexity_scores:
            avg_complexity = sum(complexity_scores) / len(complexity_scores)
            print(f"\nAverage Complexity Score: {avg_complexity:.2f}")
        
        if execution_times:
            avg_execution = sum(execution_times) / len(execution_times)
            max_execution = max(execution_times)
            min_execution = min(execution_times)
            print(f"\nExecution Times:")
            print(f"  Average: {avg_execution:.2f}s")
            print(f"  Min: {min_execution:.2f}s")
            print(f"  Max: {max_execution:.2f}s")
    
    def tail_logs(self, lines=50):
        """Show recent log entries"""
        print(f"\n=== RECENT LOG ENTRIES (Last {lines} lines) ===")
        
        if not self.main_log.exists():
            print("No main log found")
            return
        
        with open(self.main_log, 'r') as f:
            log_lines = f.readlines()
            for line in log_lines[-lines:]:
                print(line.rstrip())
    
    def search_logs(self, pattern, context=2):
        """Search for pattern in logs with context"""
        print(f"\n=== SEARCH RESULTS: '{pattern}' ===")
        
        if not self.main_log.exists():
            print("No main log found")
            return
        
        with open(self.main_log, 'r') as f:
            lines = f.readlines()
            
        matches = []
        for i, line in enumerate(lines):
            if re.search(pattern, line, re.IGNORECASE):
                start = max(0, i - context)
                end = min(len(lines), i + context + 1)
                matches.append((i, start, end))
        
        if not matches:
            print("No matches found")
            return
        
        print(f"Found {len(matches)} matches:")
        for match_line, start, end in matches[:10]:  # Show first 10 matches
            print(f"\n--- Match at line {match_line + 1} ---")
            for j in range(start, end):
                prefix = ">>> " if j == match_line else "    "
                print(f"{prefix}{lines[j].rstrip()}")


def main():
    parser = argparse.ArgumentParser(description="Shepherd Log Analysis Tool")
    parser.add_argument("--logs-dir", default="logs", help="Directory containing log files")
    parser.add_argument("--errors", type=int, metavar="HOURS", help="Analyze errors from last N hours")
    parser.add_argument("--workflows", type=int, default=10, help="Analyze last N workflows")
    parser.add_argument("--agents", type=int, default=20, help="Analyze last N agent actions")
    parser.add_argument("--performance", action="store_true", help="Show performance analysis")
    parser.add_argument("--tail", type=int, metavar="LINES", help="Show last N log lines")
    parser.add_argument("--search", help="Search for pattern in logs")
    parser.add_argument("--all", action="store_true", help="Run all analyses")
    
    args = parser.parse_args()
    
    if not any([args.errors, args.workflows, args.agents, args.performance, args.tail, args.search, args.all]):
        args.all = True  # Default to all if no specific analysis requested
    
    analyzer = LogAnalyzer(args.logs_dir)
    
    if not analyzer.logs_dir.exists():
        print(f"Log directory '{args.logs_dir}' not found")
        print("Make sure to run the application first to generate logs")
        return 1
    
    print("🐑 Shepherd Log Analysis")
    print(f"Analyzing logs in: {analyzer.logs_dir.absolute()}")
    
    if args.all or args.errors is not None:
        hours = args.errors if args.errors is not None else 24
        analyzer.analyze_errors(hours)
    
    if args.all or args.workflows:
        analyzer.analyze_workflows(args.workflows)
    
    if args.all or args.agents:
        analyzer.analyze_agents(args.agents)
    
    if args.all or args.performance:
        analyzer.analyze_performance()
    
    if args.tail:
        analyzer.tail_logs(args.tail)
    
    if args.search:
        analyzer.search_logs(args.search)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
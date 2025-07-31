#!/usr/bin/env python3
import argparse
from src.core.orchestrator import IntelligentOrchestrator
from src.core.models import ExecutionStatus
from src.utils.logger import get_logger, log_user_interaction, log_system_info


def main():
    logger = get_logger('cli_app')
    logger.info("Starting Shepherd CLI application")
    
    parser = argparse.ArgumentParser(
        description="Shepherd - Intelligent Workflow Orchestrator"
    )
    parser.add_argument(
        "request",
        nargs="?",
        help="Natural language request to process"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode with step confirmation"
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Run in development mode (launches Gradio interface)"
    )
    
    args = parser.parse_args()
    log_system_info("cli_startup", {"args": vars(args)})
    
    if args.dev:
        from app import create_interface
        demo = create_interface()
        print("Starting Gradio interface...")
        demo.launch(server_name="0.0.0.0", server_port=7860)
        return
    
    orchestrator = IntelligentOrchestrator()
    
    if args.request:
        user_request = args.request
    else:
        print("Shepherd - Intelligent Workflow Orchestrator")
        print("==========================================")
        user_request = input("\nEnter your request: ")
    
    print("\nProcessing your request...")
    
    if args.interactive:
        result = orchestrator.execute_interactive(user_request)
    else:
        result = orchestrator.execute_request(user_request)
    
    print("\n=== Execution Results ===")
    print(f"Status: {result.status.value}")
    print(f"Total Time: {result.total_execution_time:.2f}s")
    print(f"Steps Completed: {sum(1 for s in result.steps if s.status == ExecutionStatus.COMPLETED)}/{len(result.steps)}")
    
    if result.errors:
        print("\nErrors:")
        for error in result.errors:
            print(f"  - {error}")
    
    print("\nOutput:")
    for key, value in result.output.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
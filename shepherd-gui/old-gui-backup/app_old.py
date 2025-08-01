import gradio as gr
from src.core.orchestrator import IntelligentOrchestrator
from src.core.models import ExecutionStatus
from src.utils.logger import get_logger, log_user_interaction, log_system_info
import json
import sys
from datetime import datetime
from decimal import Decimal


logger = get_logger('gradio_app')
orchestrator = IntelligentOrchestrator()


def safe_json_dumps(obj, indent=2):
    """Safely serialize objects to JSON, handling non-serializable types."""
    def json_serializer(obj):
        """JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, (datetime,)):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        elif hasattr(obj, '_asdict'):  # namedtuple
            return obj._asdict()
        else:
            # For other non-serializable objects, convert to string
            return str(obj)
    
    try:
        return json.dumps(obj, indent=indent, default=json_serializer)
    except Exception as e:
        logger.warning(f"JSON serialization failed: {e}")
        # Fallback: create a simple representation
        return json.dumps({
            "error": "Could not serialize output to JSON",
            "message": str(e),
            "output_type": str(type(obj)),
            "output_str": str(obj)
        }, indent=indent)


def process_request(user_request: str, show_analysis: bool = True):
    if not user_request.strip():
        return "Please enter a request.", "", ""
    
    logger.info(f"Processing Gradio request: {user_request[:50]}...")
    log_user_interaction("gradio_request", {"request": user_request, "show_analysis": show_analysis})
    
    try:
        analysis = orchestrator.analyze_prompt(user_request)
        
        analysis_text = ""
        if show_analysis:
            analysis_text = f"""### Prompt Analysis
- **Complexity Score**: {analysis.complexity_score:.2f}
- **Urgency Score**: {analysis.urgency_score:.2f}
- **Quality Requirements**: {analysis.quality_requirements:.2f}
- **Task Types**: {', '.join(analysis.task_types)}
- **Recommended Pattern**: {analysis.recommended_pattern.value}
- **Team Size Needed**: {analysis.team_size_needed}
- **Confidence**: {analysis.confidence:.2f}

**Features Detected**:
- Dependencies: {'Yes' if analysis.dependencies else 'No'}
- Parallel Potential: {'Yes' if analysis.parallel_potential else 'No'}
- Decision Points: {'Yes' if analysis.decision_points else 'No'}
- Iteration Needed: {'Yes' if analysis.iteration_needed else 'No'}
"""
        
        result = orchestrator.execute_request(user_request)
        
        execution_summary = f"""### Execution Summary
- **Workflow ID**: {result.workflow_id[:8]}...
- **Pattern Used**: {result.pattern.value}
- **Status**: {result.status.value}
- **Total Execution Time**: {result.total_execution_time:.2f}s
- **Steps Executed**: {len(result.steps)}
"""
        
        steps_detail = "### Step Details\n"
        for i, step in enumerate(result.steps):
            status_emoji = "✅" if step.status == ExecutionStatus.COMPLETED else "❌"
            steps_detail += f"""
**Step {i+1}**: {step.description}
- Status: {status_emoji} {step.status.value}
- Execution Time: {step.execution_time:.2f}s
- Output: {step.output if step.output else 'N/A'}
- Error: {step.error if step.error else 'None'}
"""
        
        output_json = safe_json_dumps(result.output, indent=2)
        
        logger.info("Gradio request processed successfully")
        return analysis_text, execution_summary + steps_detail, output_json
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Gradio request failed: {error_msg}", exc_info=True)
        return f"Error: {error_msg}", "", ""


def create_interface():
    with gr.Blocks(title="Shepherd - Intelligent Workflow Orchestrator") as demo:
        gr.Markdown("""
        # 🐑 Shepherd - Intelligent Workflow Orchestrator
        ### By InfraWorks.io
        
        Enter a natural language request and Shepherd will:
        1. Analyze the complexity and requirements
        2. Select the optimal workflow pattern
        3. Create specialized agents
        4. Execute the workflow
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                user_input = gr.Textbox(
                    label="Your Request",
                    placeholder="e.g., 'Analyze my React codebase and implement user authentication with JWT'",
                    lines=3
                )
                show_analysis = gr.Checkbox(
                    label="Show Prompt Analysis",
                    value=True
                )
                submit_btn = gr.Button("Execute", variant="primary")
        
        with gr.Row():
            with gr.Column():
                analysis_output = gr.Markdown(label="Analysis")
            
            with gr.Column():
                execution_output = gr.Markdown(label="Execution Details")
        
        with gr.Row():
            result_output = gr.Code(
                label="Execution Output (JSON)",
                language="json"
            )
        
        gr.Examples(
            examples=[
                "Create a simple todo list application",
                "Analyze sales data and create a report with visualizations",
                "Fix performance issues in my server and optimize database queries",
                "Research current AI trends and create a presentation",
                "Implement user authentication and create API documentation"
            ],
            inputs=user_input
        )
        
        submit_btn.click(
            fn=process_request,
            inputs=[user_input, show_analysis],
            outputs=[analysis_output, execution_output, result_output]
        )
    
    return demo


if __name__ == "__main__":
    import os
    
    # Initialize logging
    logger.info("Starting Shepherd Gradio application")
    log_system_info("gradio_startup", {"args": sys.argv, "cwd": os.getcwd()})
    
    # Check for desktop mode flag
    desktop_mode = "--desktop" in sys.argv or os.getenv("SHEPHERD_DESKTOP_MODE", "false").lower() == "true"
    
    demo = create_interface()
    
    if desktop_mode:
        logger.info("Launching in desktop mode")
        # Launch as desktop app
        demo.launch(
            inbrowser=True,
            share=False,
            quiet=True
        )
    else:
        logger.info("Launching as web server on port 7860")
        # Launch as web server
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False
        )
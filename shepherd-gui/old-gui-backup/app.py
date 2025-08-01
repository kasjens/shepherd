import gradio as gr
from src.core.orchestrator import IntelligentOrchestrator
from src.core.models import ExecutionStatus
from src.utils.logger import get_logger, log_user_interaction, log_system_info
import json
import sys
import os
import uuid
import base64
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any, Tuple

logger = get_logger('gradio_app')
orchestrator = IntelligentOrchestrator()

def get_logo_base64():
    """Convert logo image to base64 for embedding."""
    logo_path = os.path.join(os.path.dirname(__file__), "Shepherd.png")
    try:
        with open(logo_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode('utf-8')
            return f"data:image/png;base64,{encoded}"
    except Exception as e:
        logger.warning(f"Could not load logo: {e}")
        return ""

# Global chat storage (in production, this would be a database)
chat_sessions = {}
current_chat_id = None
artifacts_storage = {}

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

def create_new_chat() -> str:
    """Create a new chat session and return its ID."""
    chat_id = str(uuid.uuid4())
    chat_sessions[chat_id] = {
        "id": chat_id,
        "title": "New Chat",
        "messages": [],
        "artifacts": [],
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    return chat_id

def get_chat_list() -> List[Dict[str, Any]]:
    """Get list of all chat sessions for the sidebar."""
    chats = []
    for chat_id, chat_data in chat_sessions.items():
        chats.append({
            "id": chat_id,
            "title": chat_data.get("title", "Untitled Chat"),
            "message_count": len(chat_data.get("messages", [])),
            "artifact_count": len(chat_data.get("artifacts", [])),
            "updated_at": chat_data.get("updated_at", datetime.now()),
            "is_active": chat_id == current_chat_id
        })
    
    # Sort by most recent first
    chats.sort(key=lambda x: x["updated_at"], reverse=True)
    return chats

def format_chat_list_html() -> str:
    """Format chat list as HTML for the sidebar."""
    chats = get_chat_list()
    
    if not chats:
        return """
        <div class="chat-list-empty">
            <p>No conversations yet</p>
            <p class="text-muted">Click "New Chat" to start</p>
        </div>
        """
    
    html = '<div class="chat-list">'
    
    for chat in chats:
        active_class = "active" if chat["is_active"] else ""
        updated_str = chat["updated_at"].strftime("%I:%M %p") if chat["updated_at"].date() == datetime.now().date() else chat["updated_at"].strftime("%m/%d")
        
        html += f"""
        <div class="chat-item {active_class}" onclick="switchChat('{chat["id"]}')" data-chat-id="{chat["id"]}">
            <div class="chat-indicator">{'🔵' if chat["is_active"] else '⚪'}</div>
            <div class="chat-info">
                <div class="chat-title">{chat["title"][:30]}{'...' if len(chat["title"]) > 30 else ''}</div>
                <div class="chat-meta">{chat["artifact_count"]} artifacts • {updated_str}</div>
            </div>
        </div>
        """
    
    html += '</div>'
    return html

def format_artifacts_list_html(chat_id: str = None) -> str:
    """Format artifacts list as HTML for the sidebar."""
    artifacts = []
    
    if chat_id and chat_id in chat_sessions:
        artifacts = chat_sessions[chat_id].get("artifacts", [])
    else:
        # Show all artifacts across all chats
        for session in chat_sessions.values():
            artifacts.extend(session.get("artifacts", []))
    
    if not artifacts:
        return """
        <div class="artifacts-empty">
            <p>No artifacts yet</p>
            <p class="text-muted">Generated files will appear here</p>
        </div>
        """
    
    html = '<div class="artifacts-list">'
    
    # Sort by most recent first
    artifacts.sort(key=lambda x: x.get("created_at", datetime.now()), reverse=True)
    
    for artifact in artifacts[:10]:  # Show last 10
        icon = get_artifact_icon(artifact.get("type", "unknown"))
        name = artifact.get("name", "Unnamed")
        artifact_type = artifact.get("type", "Unknown")
        created_str = artifact.get("created_at", datetime.now()).strftime("%I:%M %p")
        
        html += f"""
        <div class="artifact-item" onclick="showArtifact('{artifact.get("id", "")}')" data-artifact-id="{artifact.get('id', '')}">
            <div class="artifact-icon">{icon}</div>
            <div class="artifact-info">
                <div class="artifact-name">{name[:25]}{'...' if len(name) > 25 else ''}</div>
                <div class="artifact-meta">{artifact_type} • {created_str}</div>
            </div>
        </div>
        """
    
    html += '</div>'
    return html

def get_artifact_icon(artifact_type: str) -> str:
    """Get icon for artifact type."""
    icons = {
        "python": "🐍",
        "script": "🔧", 
        "shell": "🐚",
        "bash": "🐚",
        "json": "📄",
        "report": "📊",
        "markdown": "📝",
        "code": "💻",
        "config": "⚙️",
        "log": "📜"
    }
    return icons.get(artifact_type.lower(), "📦")

def format_message_history(chat_id: str) -> str:
    """Format message history as HTML for the conversation area."""
    if chat_id not in chat_sessions:
        return '<div class="no-messages">Start a conversation by typing a message below.</div>'
    
    messages = chat_sessions[chat_id].get("messages", [])
    
    if not messages:
        return '<div class="no-messages">Start a conversation by typing a message below.</div>'
    
    html = '<div class="message-history">'
    
    for message in messages:
        sender = message.get("sender", "user")
        content = message.get("content", "")
        timestamp = message.get("timestamp", datetime.now())
        artifacts = message.get("artifacts", [])
        
        timestamp_str = timestamp.strftime("%I:%M %p") if timestamp.date() == datetime.now().date() else timestamp.strftime("%m/%d %I:%M %p")
        
        if sender == "user":
            html += f"""
            <div class="message user-message">
                <div class="message-header">
                    <span class="sender">👤 You</span>
                    <span class="timestamp">{timestamp_str}</span>
                </div>
                <div class="message-content">{content}</div>
            </div>
            """
        else:
            html += f"""
            <div class="message ai-message">
                <div class="message-header">
                    <span class="sender">🐑 Shepherd</span>
                    <span class="timestamp">{timestamp_str}</span>
                </div>
                <div class="message-content">{content}</div>
            """
            
            # Add artifacts if any
            if artifacts:
                html += '<div class="message-artifacts">'
                for artifact in artifacts:
                    icon = get_artifact_icon(artifact.get("type", "unknown"))
                    name = artifact.get("name", "Unnamed")
                    html += f"""
                    <button class="artifact-button" onclick="showArtifact('{artifact.get("id", "")}')">
                        {icon} {name}
                    </button>
                    """
                html += '</div>'
            
            html += '</div>'
    
    html += '</div>'
    return html

def send_message(message: str, chat_id: str = None) -> Tuple[str, str, str, str]:
    """Send a message and get AI response."""
    global current_chat_id
    
    if not message.strip():
        return "", "", "", ""
    
    # Create new chat if none exists
    if not chat_id or chat_id not in chat_sessions:
        chat_id = create_new_chat()
        current_chat_id = chat_id
    
    # Add user message
    user_message = {
        "sender": "user",
        "content": message,
        "timestamp": datetime.now()
    }
    
    chat_sessions[chat_id]["messages"].append(user_message)
    
    # Generate title from first message
    if len(chat_sessions[chat_id]["messages"]) == 1:
        title = message[:50] + ("..." if len(message) > 50 else "")
        chat_sessions[chat_id]["title"] = title
    
    try:
        # Process the request
        logger.info(f"Processing chat message: {message[:50]}...")
        result = orchestrator.execute_request(message)
        
        # Create AI response
        ai_content = f"""I'll help you with that task. Let me analyze and execute your request.

🔄 **Analyzing request...**
- Complexity: {orchestrator.analyze_prompt(message).complexity_score:.2f}
- Pattern: {result.pattern.value}
- Status: {result.status.value}

**Execution Results:**
- Total Time: {result.total_execution_time:.2f}s
- Steps Completed: {len([s for s in result.steps if s.status == ExecutionStatus.COMPLETED])}/{len(result.steps)}
"""
        
        # Extract artifacts from result
        artifacts = []
        artifact_html = ""
        
        for step_id, output_data in result.output.items():
            if isinstance(output_data, dict):
                # Create artifact from output
                artifact_id = str(uuid.uuid4())
                artifact = {
                    "id": artifact_id,
                    "name": f"{step_id}_output.json",
                    "type": "json",
                    "content": safe_json_dumps(output_data),
                    "created_at": datetime.now(),
                    "chat_id": chat_id
                }
                
                artifacts.append(artifact)
                chat_sessions[chat_id]["artifacts"].append(artifact)
                artifacts_storage[artifact_id] = artifact
                
                # Add to AI content
                ai_content += f"\n\n📦 Generated artifact: `{artifact['name']}`"
        
        ai_message = {
            "sender": "ai", 
            "content": ai_content,
            "timestamp": datetime.now(),
            "artifacts": artifacts
        }
        
        chat_sessions[chat_id]["messages"].append(ai_message)
        chat_sessions[chat_id]["updated_at"] = datetime.now()
        
        # Return updated components
        message_history = format_message_history(chat_id)
        chat_list = format_chat_list_html()
        artifacts_list = format_artifacts_list_html(chat_id)
        
        # Show first artifact in panel if any
        artifact_panel = ""
        if artifacts:
            artifact_panel = format_artifact_display(artifacts[0])
        
        return message_history, chat_list, artifacts_list, artifact_panel
        
    except Exception as e:
        error_msg = f"Error processing request: {str(e)}"
        logger.error(f"Chat message processing failed: {error_msg}", exc_info=True)
        
        ai_message = {
            "sender": "ai",
            "content": f"❌ {error_msg}",
            "timestamp": datetime.now(),
            "artifacts": []
        }
        
        chat_sessions[chat_id]["messages"].append(ai_message)
        
        message_history = format_message_history(chat_id)
        chat_list = format_chat_list_html()
        artifacts_list = format_artifacts_list_html(chat_id)
        
        return message_history, chat_list, artifacts_list, ""

def format_artifact_display(artifact: Dict[str, Any]) -> str:
    """Format artifact for display in the artifacts panel."""
    if not artifact:
        return ""
    
    name = artifact.get("name", "Unnamed")
    artifact_type = artifact.get("type", "unknown")
    content = artifact.get("content", "")
    created_at = artifact.get("created_at", datetime.now())
    
    created_str = created_at.strftime("%I:%M %p")
    icon = get_artifact_icon(artifact_type)
    
    # Format content based on type
    if artifact_type in ["json", "python", "shell", "bash"]:
        language = "json" if artifact_type == "json" else "python" if artifact_type == "python" else "bash"
        content_html = f'<pre><code class="language-{language}">{content}</code></pre>'
    else:
        content_html = f'<pre>{content}</pre>'
    
    return f"""
    <div class="artifact-display">
        <div class="artifact-header">
            <span class="artifact-title">{icon} {name}</span>
            <div class="artifact-actions">
                <button onclick="copyArtifact('{artifact.get("id", "")}')">📋</button>
                <button onclick="downloadArtifact('{artifact.get("id", "")}')">📥</button>
            </div>
        </div>
        <div class="artifact-meta">
            Language: {artifact_type.title()} • {len(content)} chars • Created {created_str}
        </div>
        <div class="artifact-content">
            {content_html}
        </div>
        <div class="artifact-footer">
            <button class="btn-secondary" onclick="editArtifact('{artifact.get("id", "")}')">Edit</button>
            <button class="btn-secondary" onclick="saveArtifact('{artifact.get("id", "")}')">Save As...</button>
        </div>
    </div>
    """

def create_conversational_interface():
    """Create the new conversational interface."""
    
    # Get the logo as base64
    logo_base64 = get_logo_base64()
    
    # Custom CSS for the chat interface
    css = """
    <style>
    /* Nuclear CSS reset - override everything */
    * {
        margin: 0 !important;
        padding: 0 !important;
        box-sizing: border-box !important;
    }
    
    html, body {
        width: 100vw !important;
        height: 100vh !important;
        overflow: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Completely override Gradio */
    .gradio-container,
    .gradio-container *,
    .main,
    .wrap,
    .contain,
    .panel,
    .form,
    .block,
    .gr-row,
    .gr-column,
    .gr-group,
    .gr-form,
    .svelte-*,
    #root,
    #app {
        max-width: none !important;
        width: 100% !important;
        height: auto !important;
        margin: 0 !important;
        padding: 0 !important;
        border: none !important;
        box-shadow: none !important;
        background: transparent !important;
        gap: 0 !important;
        flex-shrink: 0 !important;
    }
    
    /* Force the main container to be full screen */
    .gradio-container {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        z-index: 1000 !important;
    }
    
    /* Hide Gradio's default styling completely */
    .gradio-container .main {
        display: none !important;
    }
    
    /* Our custom app layout */
    .shepherd-app {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        display: flex;
        background: #f8f9fa;
        z-index: 1001;
    }
    
    .sidebar {
        width: 280px;
        min-width: 200px;
        max-width: 500px;
        height: 100vh;
        background: white;
        border-right: 1px solid #e9ecef;
        padding: 16px;
        overflow-y: auto;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        flex-shrink: 0;
        resize: horizontal;
        resize: none; /* We'll handle resize manually */
        position: relative;
    }
    
    .conversation-column {
        flex: 1;
        height: 100vh;
        display: flex;
        flex-direction: column;
        background: white;
        overflow: hidden;
    }
    
    .conversation-area {
        flex: 1;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }
    
    .input-area {
        height: 100px;
        border-top: 1px solid #e9ecef;
        background: white;
        padding: 16px;
        flex-shrink: 0;
    }
    
    .input-container {
        display: flex;
        gap: 12px;
        align-items: flex-end;
        height: 100%;
    }
    
    #message-input {
        flex: 1;
        min-height: 40px;
        max-height: 68px;
        padding: 8px 12px;
        border: 1px solid #ced4da;
        border-radius: 6px;
        resize: none;
        font-family: inherit;
        font-size: 14px;
        outline: none;
    }
    
    .artifacts-panel {
        width: 350px;
        min-width: 250px;
        max-width: 600px;
        height: 100vh;
        background: white;
        border-left: 1px solid #e9ecef;
        padding: 16px;
        overflow-y: auto;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        flex-shrink: 0;
        position: relative;
    }
    
    /* Remove scrollbar when not needed */
    .sidebar::-webkit-scrollbar {
        width: 6px;
    }
    
    .sidebar::-webkit-scrollbar-track {
        background: transparent;
    }
    
    .sidebar::-webkit-scrollbar-thumb {
        background: #e9ecef;
        border-radius: 3px;
    }
    
    .sidebar.collapsed {
        width: 60px;
    }
    
    .sidebar-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 16px;
        padding-bottom: 16px;
        border-bottom: 1px solid #e9ecef;
    }
    
    .logo {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 18px;
        font-weight: 600;
        color: var(--text-primary);
    }
    
    .logo-image {
        width: 24px;
        height: 24px;
        object-fit: contain;
    }
    
    .new-chat-btn {
        background: #0d6efd;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 14px;
    }
    
    .collapse-btn {
        background: none;
        border: none;
        font-size: 18px;
        cursor: pointer;
    }
    
    .section-title {
        font-size: 12px;
        font-weight: 600;
        color: #6c757d;
        text-transform: uppercase;
        margin: 16px 0 8px 0;
    }
    
    .chat-item {
        padding: 8px;
        border-radius: 6px;
        cursor: pointer;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
    }
    
    .chat-item:hover {
        background: #f8f9fa;
    }
    
    .chat-item.active {
        background: #e7f3ff;
        border: 1px solid #0d6efd;
    }
    
    .chat-indicator {
        margin-right: 8px;
        font-size: 12px;
    }
    
    .chat-title {
        font-weight: 500;
        font-size: 14px;
        color: #212529;
    }
    
    .chat-meta {
        font-size: 12px;
        color: #6c757d;
    }
    
    .artifact-item {
        padding: 6px 8px;
        border-radius: 4px;
        cursor: pointer;
        margin-bottom: 2px;
        display: flex;
        align-items: center;
    }
    
    .artifact-item:hover {
        background: #f8f9fa;
    }
    
    .artifact-icon {
        margin-right: 8px;
        font-size: 14px;
    }
    
    .artifact-name {
        font-weight: 500;
        font-size: 13px;
        color: #212529;
    }
    
    .artifact-meta {
        font-size: 11px;
        color: #6c757d;
    }
    
    .conversation-area {
        flex: 1;
        height: 100vh;
        display: flex;
        flex-direction: column;
        background: white;
        box-sizing: border-box;
    }
    
    .chat-header {
        padding: 16px;
        border-bottom: 1px solid #e9ecef;
        background: white;
    }
    
    .chat-title-display {
        font-size: 18px;
        font-weight: 600;
        color: #212529;
        margin-bottom: 4px;
    }
    
    .chat-subtitle {
        font-size: 14px;
        color: #6c757d;
    }
    
    .message-container {
        flex: 1;
        overflow-y: auto;
        padding: 16px;
        height: 100%;
        max-height: calc(100vh - 180px); /* Account for header and input */
    }
    
    /* Custom scrollbar for message container */
    .message-container::-webkit-scrollbar {
        width: 6px;
    }
    
    .message-container::-webkit-scrollbar-track {
        background: transparent;
    }
    
    .message-container::-webkit-scrollbar-thumb {
        background: #e9ecef;
        border-radius: 3px;
    }
    
    .message {
        margin-bottom: 24px;
    }
    
    .message-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
    }
    
    .sender {
        font-weight: 600;
        font-size: 14px;
    }
    
    .timestamp {
        font-size: 12px;
        color: #6c757d;
    }
    
    .message-content {
        background: #f8f9fa;
        padding: 12px;
        border-radius: 8px;
        white-space: pre-wrap;
        line-height: 1.5;
    }
    
    .user-message .message-content {
        background: #e7f3ff;
        border: 1px solid #b3d9ff;
    }
    
    .ai-message .message-content {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
    }
    
    .message-artifacts {
        margin-top: 8px;
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
    }
    
    .artifact-button {
        background: white;
        border: 1px solid #0d6efd;
        color: #0d6efd;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        cursor: pointer;
    }
    
    .artifact-button:hover {
        background: #0d6efd;
        color: white;
    }
    
    .input-area {
        padding: 16px;
        border-top: 1px solid #e9ecef;
        background: white;
    }
    
    .input-container {
        display: flex;
        gap: 12px;
        align-items: flex-end;
    }
    
    /* Message input styling */
    .message-input textarea, .message-input input {
        flex: 1 !important;
        min-height: 40px !important;
        max-height: 68px !important;
        padding: 8px 12px !important;
        border: 1px solid #ced4da !important;
        border-radius: 6px !important;
        resize: none !important;
        font-family: inherit !important;
        font-size: 14px !important;
        margin: 0 !important;
        overflow-y: auto !important;
    }
    
    .message-input {
        flex: 1 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .send-btn {
        background: #0d6efd;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        cursor: pointer;
        font-weight: 500;
    }
    
    /* Settings button */
    .settings-btn {
        width: 100%;
        padding: 8px 16px;
        background: var(--accent-color);
        color: white;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        font-size: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
        transition: background 0.2s;
    }
    
    .settings-btn:hover {
        background: var(--accent-hover);
    }
    
    .settings-icon {
        font-size: 16px;
    }
    
    /* Settings modal */
    .settings-modal {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0, 0, 0, 0.5);
        z-index: 2000;
        align-items: center;
        justify-content: center;
    }
    
    .settings-modal.active {
        display: flex;
    }
    
    .settings-content {
        background: white;
        padding: 24px;
        border-radius: 8px;
        width: 500px;
        max-height: 80vh;
        overflow-y: auto;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
    }
    
    .settings-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        padding-bottom: 16px;
        border-bottom: 1px solid #e9ecef;
    }
    
    .settings-title {
        font-size: 20px;
        font-weight: 600;
        color: #212529;
    }
    
    .close-settings {
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        color: #6c757d;
        padding: 0;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 4px;
        transition: background 0.2s;
    }
    
    .close-settings:hover {
        background: #f8f9fa;
    }
    
    .settings-section {
        margin-bottom: 24px;
    }
    
    .settings-section-title {
        font-size: 16px;
        font-weight: 600;
        color: #212529;
        margin-bottom: 12px;
    }
    
    .theme-options {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
    }
    
    .theme-card {
        border: 2px solid #e9ecef;
        border-radius: 8px;
        padding: 16px;
        cursor: pointer;
        transition: all 0.2s;
        text-align: center;
    }
    
    .theme-card:hover {
        border-color: #0d6efd;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .theme-card.active {
        border-color: #0d6efd;
        background: #e7f3ff;
    }
    
    .theme-preview {
        width: 100%;
        height: 60px;
        border-radius: 4px;
        margin-bottom: 8px;
        display: flex;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .theme-preview-sidebar {
        width: 30%;
        background: #f8f9fa;
    }
    
    .theme-preview-main {
        flex: 1;
        background: white;
    }
    
    .theme-name {
        font-size: 14px;
        font-weight: 500;
        color: #212529;
    }
    
    .artifacts-panel {
        width: 350px;
        height: 100vh;
        background: white;
        border-left: 1px solid #e9ecef;
        padding: 16px;
        overflow-y: auto;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
    }
    
    /* Custom scrollbar for artifacts panel */
    .artifacts-panel::-webkit-scrollbar {
        width: 6px;
    }
    
    .artifacts-panel::-webkit-scrollbar-track {
        background: transparent;
    }
    
    .artifacts-panel::-webkit-scrollbar-thumb {
        background: #e9ecef;
        border-radius: 3px;
    }
    
    .artifacts-panel-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
        padding-bottom: 16px;
        border-bottom: 1px solid #e9ecef;
    }
    
    .panel-title {
        font-size: 16px;
        font-weight: 600;
        color: #212529;
    }
    
    .artifact-display {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 6px;
        overflow: hidden;
    }
    
    .artifact-header {
        padding: 12px;
        background: white;
        border-bottom: 1px solid #e9ecef;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .artifact-title {
        font-weight: 600;
        font-size: 14px;
    }
    
    .artifact-actions button {
        background: none;
        border: none;
        font-size: 16px;
        cursor: pointer;
        margin-left: 4px;
    }
    
    .artifact-meta {
        padding: 8px 12px;
        font-size: 12px;
        color: #6c757d;
        background: #f8f9fa;
        border-bottom: 1px solid #e9ecef;
    }
    
    .artifact-content {
        padding: 0;
        max-height: 400px;
        overflow-y: auto;
    }
    
    .artifact-content pre {
        margin: 0;
        padding: 12px;
        background: #1e1e1e;
        color: #d4d4d4;
        font-size: 12px;
        line-height: 1.4;
    }
    
    .artifact-footer {
        padding: 12px;
        background: white;
        border-top: 1px solid #e9ecef;
        display: flex;
        gap: 8px;
    }
    
    .btn-secondary {
        background: #6c757d;
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 4px;
        font-size: 12px;
        cursor: pointer;
    }
    
    .no-messages {
        text-align: center;
        color: #6c757d;
        padding: 40px;
        font-style: italic;
    }
    
    .chat-list-empty, .artifacts-empty {
        text-align: center;
        color: #6c757d;
        padding: 20px;
        font-style: italic;
    }
    
    .text-muted {
        font-size: 12px;
        margin-top: 4px;
    }
    
    /* Theme System */
    /* Default Light Theme */
    .theme-light {
        --bg-primary: #ffffff;
        --bg-secondary: #f8f9fa;
        --bg-tertiary: #e9ecef;
        --text-primary: #212529;
        --text-secondary: #6c757d;
        --border-color: #e9ecef;
        --accent-color: #0d6efd;
        --accent-hover: #0a58ca;
        --user-message-bg: #e7f3ff;
        --user-message-border: #b3d9ff;
        --ai-message-bg: #f8f9fa;
        --ai-message-border: #e9ecef;
        --code-bg: #1e1e1e;
        --code-text: #d4d4d4;
    }
    
    /* Dark Theme */
    .theme-dark {
        --bg-primary: #1a1d21;
        --bg-secondary: #212529;
        --bg-tertiary: #2c3136;
        --text-primary: #f8f9fa;
        --text-secondary: #adb5bd;
        --border-color: #495057;
        --accent-color: #0d6efd;
        --accent-hover: #3d8bfd;
        --user-message-bg: #1e3a5f;
        --user-message-border: #2c5282;
        --ai-message-bg: #2c3136;
        --ai-message-border: #495057;
        --code-bg: #0d1117;
        --code-text: #e6edf3;
    }
    
    /* Blue Theme */
    .theme-blue {
        --bg-primary: #f0f7ff;
        --bg-secondary: #e0efff;
        --bg-tertiary: #c2dfff;
        --text-primary: #0a3069;
        --text-secondary: #0969da;
        --border-color: #b8d3f0;
        --accent-color: #0969da;
        --accent-hover: #0860ca;
        --user-message-bg: #dbeafe;
        --user-message-border: #93c5fd;
        --ai-message-bg: #e0efff;
        --ai-message-border: #b8d3f0;
        --code-bg: #0a3069;
        --code-text: #e0efff;
    }
    
    /* Apply theme variables */
    .shepherd-app {
        background: var(--bg-secondary);
        color: var(--text-primary);
    }
    
    .sidebar, .conversation-column, .artifacts-panel {
        background: var(--bg-primary);
        border-color: var(--border-color);
    }
    
    .sidebar {
        border-right-color: var(--border-color);
    }
    
    .artifacts-panel {
        border-left-color: var(--border-color);
    }
    
    .chat-header, .input-area {
        background: var(--bg-primary);
        border-color: var(--border-color);
    }
    
    .message-content {
        background: var(--bg-secondary);
        border-color: var(--border-color);
        color: var(--text-primary);
    }
    
    .user-message .message-content {
        background: var(--user-message-bg);
        border-color: var(--user-message-border);
    }
    
    .ai-message .message-content {
        background: var(--ai-message-bg);
        border-color: var(--ai-message-border);
    }
    
    #message-input {
        background: var(--bg-primary);
        border-color: var(--border-color);
        color: var(--text-primary);
    }
    
    .send-btn, .new-chat-btn {
        background: var(--accent-color);
    }
    
    .send-btn:hover, .new-chat-btn:hover {
        background: var(--accent-hover);
    }
    
    .chat-item:hover, .artifact-item:hover {
        background: var(--bg-secondary);
    }
    
    .chat-item.active {
        background: var(--user-message-bg);
        border-color: var(--accent-color);
    }
    
    .section-title, .chat-meta, .artifact-meta, .timestamp {
        color: var(--text-secondary);
    }
    
    .chat-title, .artifact-name, .sender {
        color: var(--text-primary);
    }
    
    .settings-content {
        background: var(--bg-primary);
        color: var(--text-primary);
    }
    
    .settings-header {
        border-bottom-color: var(--border-color);
    }
    
    .theme-card {
        background: var(--bg-primary);
        border-color: var(--border-color);
    }
    
    .theme-card:hover, .theme-card.active {
        border-color: var(--accent-color);
    }
    
    .theme-card.active {
        background: var(--user-message-bg);
    }
    
    .artifact-content pre {
        background: var(--code-bg);
        color: var(--code-text);
    }
    
    /* Resize handles */
    .resize-handle {
        position: absolute;
        background: transparent;
        z-index: 10;
    }
    
    .resize-handle:hover {
        background: var(--accent-color);
        opacity: 0.3;
    }
    
    .resize-handle.active {
        background: var(--accent-color);
        opacity: 0.5;
    }
    
    .sidebar-resize {
        top: 0;
        right: -3px;
        width: 6px;
        height: 100%;
        cursor: ew-resize;
    }
    
    .artifacts-resize {
        top: 0;
        left: -3px;
        width: 6px;
        height: 100%;
        cursor: ew-resize;
    }
    </style>
    """
    
    # Initialize with a default chat
    if not chat_sessions:
        create_new_chat()
        current_chat_id = list(chat_sessions.keys())[0]
    
    with gr.Blocks(
        title="Shepherd - Intelligent Workflow Orchestrator", 
        css=css,
        theme=gr.themes.Base(),
        elem_classes=["app-container"]
    ) as demo:
        
        # Hidden state variables
        current_chat_state = gr.State(current_chat_id)
        
        # Complete custom HTML layout that bypasses Gradio's layout system
        main_interface = gr.HTML(f"""
        <div class="shepherd-app theme-light" id="app-container">
            <!-- Settings Modal -->
            <div class="settings-modal" id="settings-modal">
                <div class="settings-content">
                    <div class="settings-header">
                        <h2 class="settings-title">Settings</h2>
                        <button class="close-settings" onclick="closeSettings()">×</button>
                    </div>
                    
                    <div class="settings-section">
                        <h3 class="settings-section-title">Appearance</h3>
                        <div class="theme-options">
                            <div class="theme-card active" onclick="setTheme('light')" data-theme="light">
                                <div class="theme-preview">
                                    <div class="theme-preview-sidebar" style="background: #f8f9fa;"></div>
                                    <div class="theme-preview-main" style="background: white;"></div>
                                </div>
                                <div class="theme-name">Light</div>
                            </div>
                            
                            <div class="theme-card" onclick="setTheme('dark')" data-theme="dark">
                                <div class="theme-preview">
                                    <div class="theme-preview-sidebar" style="background: #212529;"></div>
                                    <div class="theme-preview-main" style="background: #1a1d21;"></div>
                                </div>
                                <div class="theme-name">Dark</div>
                            </div>
                            
                            <div class="theme-card" onclick="setTheme('blue')" data-theme="blue">
                                <div class="theme-preview">
                                    <div class="theme-preview-sidebar" style="background: #e0efff;"></div>
                                    <div class="theme-preview-main" style="background: #f0f7ff;"></div>
                                </div>
                                <div class="theme-name">Blue</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Sidebar -->
            <div class="sidebar" id="sidebar">
                <div class="resize-handle sidebar-resize" id="sidebar-resize"></div>
                <div class="sidebar-header">
                    <div class="logo">
                        <img src="{logo_base64}" alt="Shepherd Logo" class="logo-image">
                        Shepherd
                    </div>
                </div>
                
                <div class="section-title">💬 NEW CHAT</div>
                <button class="new-chat-btn" onclick="createNewChat()">+ New Chat</button>
                
                <div class="section-title">📋 CONVERSATIONS</div>
                <div id="chat-list">
                    {format_chat_list_html()}
                </div>
                
                <div class="section-title">📦 ARTIFACTS</div>
                <div id="artifacts-list">
                    {format_artifacts_list_html()}
                </div>
                
                <div class="section-title">⚙️ SETTINGS</div>
                <button class="settings-btn" onclick="openSettings()">
                    <span class="settings-icon">⚙️</span>
                    <span>Settings</span>
                </button>
                
                <div style="margin-top: auto; padding-top: 20px; border-top: 1px solid #e9ecef;">
                    <div style="font-size: 12px; color: #6c757d;">Status: ● Connected</div>
                </div>
            </div>
            
            <!-- Conversation Area -->
            <div class="conversation-column">
                <div class="conversation-area">
                    <div class="chat-header">
                        <div class="chat-title-display">New Chat</div>
                        <div class="chat-subtitle">Ready to help with your workflow orchestration</div>
                    </div>
                    
                    <div class="message-container" id="message-container">
                        {format_message_history(current_chat_id) if current_chat_id else '<div class="no-messages">Start a conversation by typing a message below.</div>'}
                    </div>
                </div>
                
                <div class="input-area">
                    <div class="input-container">
                        <textarea id="message-input" placeholder="Type your message... (Shift+Enter for new line, Enter to send)" rows="3"></textarea>
                        <button id="send-button" class="send-btn">Send</button>
                    </div>
                </div>
            </div>
            
            <!-- Artifacts Panel -->
            <div class="artifacts-panel" id="artifacts-panel">
                <div class="resize-handle artifacts-resize" id="artifacts-resize"></div>
                <div class="artifacts-panel-header">
                    <div class="panel-title">📦 Artifacts</div>
                    <div>
                        <button onclick="searchArtifacts()">🔍</button>
                        <button onclick="downloadAllArtifacts()">📥</button>
                    </div>
                </div>
                <div id="artifact-display">
                    <div class="no-messages">Artifacts will appear here when generated</div>
                </div>
            </div>
        </div>
        """)
        
        # Hidden input and button for Gradio functionality
        hidden_input = gr.Textbox(visible=False, elem_id="hidden-input")
        hidden_button = gr.Button(visible=False, elem_id="hidden-button")
        
        # Event handlers
        def handle_send_message(message, chat_state):
            if not message.strip():
                return f"""
                <div class="shepherd-app">
                    <!-- Sidebar -->
                    <div class="sidebar" id="sidebar">
                        <div class="resize-handle sidebar-resize" id="sidebar-resize"></div>
                        <div class="sidebar-header">
                            <div class="logo">
                                <img src="{logo_base64}" alt="Shepherd Logo" class="logo-image">
                                Shepherd
                            </div>
                        </div>
                        
                        <div class="section-title">💬 NEW CHAT</div>
                        <button class="new-chat-btn" onclick="createNewChat()">+ New Chat</button>
                        
                        <div class="section-title">📋 CONVERSATIONS</div>
                        <div id="chat-list">
                            {format_chat_list_html()}
                        </div>
                        
                        <div class="section-title">📦 ARTIFACTS</div>
                        <div id="artifacts-list">
                            {format_artifacts_list_html()}
                        </div>
                        
                        <div class="section-title">⚙️ SETTINGS</div>
                        <button class="settings-btn" onclick="openSettings()">
                            <span class="settings-icon">⚙️</span>
                            <span>Settings</span>
                        </button>
                        
                        <div style="margin-top: auto; padding-top: 20px; border-top: 1px solid #e9ecef;">
                            <div style="font-size: 12px; color: #6c757d;">Status: ● Connected</div>
                        </div>
                    </div>
                    
                    <!-- Conversation Area -->
                    <div class="conversation-column">
                        <div class="conversation-area">
                            <div class="chat-header">
                                <div class="chat-title-display">New Chat</div>
                                <div class="chat-subtitle">Ready to help with your workflow orchestration</div>
                            </div>
                            
                            <div class="message-container" id="message-container">
                                <div class="no-messages">Start a conversation by typing a message below.</div>
                            </div>
                        </div>
                        
                        <div class="input-area">
                            <div class="input-container">
                                <textarea id="message-input" placeholder="Type your message... (Shift+Enter for new line, Enter to send)" rows="3"></textarea>
                                <button id="send-button" class="send-btn">Send</button>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Artifacts Panel -->
                    <div class="artifacts-panel" id="artifacts-panel">
                        <div class="resize-handle artifacts-resize" id="artifacts-resize"></div>
                        <div class="artifacts-panel-header">
                            <div class="panel-title">📦 Artifacts</div>
                            <div>
                                <button onclick="searchArtifacts()">🔍</button>
                                <button onclick="downloadAllArtifacts()">📥</button>
                            </div>
                        </div>
                        <div id="artifact-display">
                            <div class="no-messages">Artifacts will appear here when generated</div>
                        </div>
                    </div>
                </div>
                """, ""
            
            msg_history, chat_list, artifacts_list, artifact_panel = send_message(message, chat_state)
            
            # Create complete app HTML with updated content
            full_app_html = f"""
            <div class="shepherd-app">
                <!-- Sidebar -->
                <div class="sidebar" id="sidebar">
                    <div class="resize-handle sidebar-resize" id="sidebar-resize"></div>
                    <div class="sidebar-header">
                        <div class="logo">
                            <img src="{logo_base64}" alt="Shepherd Logo" class="logo-image">
                            Shepherd
                        </div>
                    </div>
                    
                    <div class="section-title">💬 NEW CHAT</div>
                    <button class="new-chat-btn" onclick="createNewChat()">+ New Chat</button>
                    
                    <div class="section-title">📋 CONVERSATIONS</div>
                    <div id="chat-list">
                        {chat_list}
                    </div>
                    
                    <div class="section-title">📦 ARTIFACTS</div>
                    <div id="artifacts-list">
                        {artifacts_list}
                    </div>
                    
                    <div class="section-title">⚙️ SETTINGS</div>
                    <button class="settings-btn" onclick="openSettings()">
                        <span class="settings-icon">⚙️</span>
                        <span>Settings</span>
                    </button>
                    
                    <div style="margin-top: auto; padding-top: 20px; border-top: 1px solid #e9ecef;">
                        <div style="font-size: 12px; color: #6c757d;">Status: ● Connected</div>
                    </div>
                </div>
                
                <!-- Conversation Area -->
                <div class="conversation-column">
                    <div class="conversation-area">
                        <div class="chat-header">
                            <div class="chat-title-display">Chat Session</div>
                            <div class="chat-subtitle">Intelligent workflow orchestration in progress</div>
                        </div>
                        
                        <div class="message-container" id="message-container">
                            {msg_history}
                        </div>
                    </div>
                    
                    <div class="input-area">
                        <div class="input-container">
                            <textarea id="message-input" placeholder="Type your message... (Shift+Enter for new line, Enter to send)" rows="3"></textarea>
                            <button id="send-button" class="send-btn">Send</button>
                        </div>
                    </div>
                </div>
                
                <!-- Artifacts Panel -->
                <div class="artifacts-panel" id="artifacts-panel">
                    <div class="resize-handle artifacts-resize" id="artifacts-resize"></div>
                    <div class="artifacts-panel-header">
                        <div class="panel-title">📦 Artifacts</div>
                        <div>
                            <button onclick="searchArtifacts()">🔍</button>
                            <button onclick="downloadAllArtifacts()">📥</button>
                        </div>
                    </div>
                    <div id="artifact-display">
                        {artifact_panel if artifact_panel else '<div class="no-messages">Artifacts will appear here when generated</div>'}
                    </div>
                </div>
            </div>
            """
            
            return full_app_html, ""
        
        # Connect hidden button for functionality
        hidden_button.click(
            fn=handle_send_message,
            inputs=[hidden_input, current_chat_state],
            outputs=[main_interface, hidden_input]
        )
        
        # Add JavaScript for interactivity
        demo.load(js="""
        function createNewChat() {
            console.log('Creating new chat...');
        }
        
        function switchChat(chatId) {
            console.log('Switching to chat:', chatId);
            // Update active chat indicator
            document.querySelectorAll('.chat-item').forEach(item => {
                item.classList.remove('active');
            });
            const chatItem = document.querySelector(`[data-chat-id="${chatId}"]`);
            if (chatItem) {
                chatItem.classList.add('active');
            }
        }
        
        function showArtifact(artifactId) {
            console.log('Showing artifact:', artifactId);
        }
        
        function copyArtifact(artifactId) {
            console.log('Copying artifact:', artifactId);
        }
        
        function downloadArtifact(artifactId) {
            console.log('Downloading artifact:', artifactId);
        }
        
        function searchArtifacts() {
            console.log('Searching artifacts...');
        }
        
        function downloadAllArtifacts() {
            console.log('Downloading all artifacts...');
        }
        
        // Settings and theme functions
        function openSettings() {
            const modal = document.getElementById('settings-modal');
            if (modal) {
                modal.classList.add('active');
            }
        }
        
        function closeSettings() {
            const modal = document.getElementById('settings-modal');
            if (modal) {
                modal.classList.remove('active');
            }
        }
        
        function setTheme(themeName) {
            const appContainer = document.getElementById('app-container');
            if (appContainer) {
                // Remove all theme classes
                appContainer.classList.remove('theme-light', 'theme-dark', 'theme-blue');
                // Add selected theme class
                appContainer.classList.add('theme-' + themeName);
                
                // Update active theme card
                document.querySelectorAll('.theme-card').forEach(card => {
                    card.classList.remove('active');
                });
                const activeCard = document.querySelector('.theme-card[data-theme="' + themeName + '"]');
                if (activeCard) {
                    activeCard.classList.add('active');
                }
                
                // Save theme preference
                localStorage.setItem('shepherd-theme', themeName);
            }
        }
        
        // Load saved theme on startup
        function loadSavedTheme() {
            const savedTheme = localStorage.getItem('shepherd-theme') || 'light';
            setTheme(savedTheme);
        }
        
        // Set up the custom input handling
        function setupInputHandling() {
            const messageInput = document.getElementById('message-input');
            const sendButton = document.getElementById('send-button');
            const hiddenInput = document.getElementById('hidden-input');
            const hiddenButton = document.getElementById('hidden-button');
            
            if (messageInput && sendButton && hiddenInput && hiddenButton) {
                // Handle send button click
                sendButton.addEventListener('click', function() {
                    const message = messageInput.value.trim();
                    if (message) {
                        // Update hidden input and trigger Gradio event
                        hiddenInput.value = message;
                        hiddenInput.dispatchEvent(new Event('input', { bubbles: true }));
                        hiddenButton.click();
                        messageInput.value = '';
                    }
                });
                
                // Handle Enter key (but allow Shift+Enter for new lines)
                messageInput.addEventListener('keydown', function(e) {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        sendButton.click();
                    }
                });
                
                // Auto-resize textarea
                messageInput.addEventListener('input', function() {
                    this.style.height = 'auto';
                    this.style.height = Math.min(this.scrollHeight, 100) + 'px';
                });
            }
        }
        
        // Set up when DOM is ready
        document.addEventListener('DOMContentLoaded', function() {
            setupInputHandling();
            loadSavedTheme();
            setupResizeHandles();
        });
        
        // Also try to set up immediately and on any mutations
        setupInputHandling();
        loadSavedTheme();
        setupResizeHandles();
        
        // Resize functionality
        function setupResizeHandles() {
            const sidebarResize = document.getElementById('sidebar-resize');
            const artifactsResize = document.getElementById('artifacts-resize');
            const sidebar = document.getElementById('sidebar');
            const artifactsPanel = document.getElementById('artifacts-panel');
            
            let isResizing = false;
            let currentResizer = null;
            
            function startResize(e, resizer, panel) {
                isResizing = true;
                currentResizer = resizer;
                resizer.classList.add('active');
                document.body.style.cursor = 'ew-resize';
                document.body.style.userSelect = 'none';
                
                e.preventDefault();
            }
            
            function doResize(e) {
                if (!isResizing || !currentResizer) return;
                
                if (currentResizer === sidebarResize) {
                    const newWidth = Math.max(200, Math.min(500, e.clientX));
                    sidebar.style.width = newWidth + 'px';
                } else if (currentResizer === artifactsResize) {
                    const newWidth = Math.max(250, Math.min(600, window.innerWidth - e.clientX));
                    artifactsPanel.style.width = newWidth + 'px';
                }
            }
            
            function stopResize() {
                if (currentResizer) {
                    currentResizer.classList.remove('active');
                    currentResizer = null;
                }
                isResizing = false;
                document.body.style.cursor = '';
                document.body.style.userSelect = '';
            }
            
            if (sidebarResize && sidebar) {
                sidebarResize.addEventListener('mousedown', (e) => startResize(e, sidebarResize, sidebar));
            }
            
            if (artifactsResize && artifactsPanel) {
                artifactsResize.addEventListener('mousedown', (e) => startResize(e, artifactsResize, artifactsPanel));
            }
            
            document.addEventListener('mousemove', doResize);
            document.addEventListener('mouseup', stopResize);
        }
        
        // Watch for DOM changes to set up handlers
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    setupInputHandling();
                    setupResizeHandles();
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        """)
    
    return demo

def create_interface():
    """Create the interface - wrapper for compatibility."""
    return create_conversational_interface()

if __name__ == "__main__":
    import os
    
    # Initialize logging
    logger.info("Starting Shepherd Conversational Interface")
    log_system_info("gradio_startup", {"args": sys.argv, "cwd": os.getcwd()})
    
    # Check for desktop mode flag
    desktop_mode = "--desktop" in sys.argv or os.getenv("SHEPHERD_DESKTOP_MODE", "false").lower() == "true"
    
    demo = create_interface()
    
    if desktop_mode:
        logger.info("Launching in desktop mode")
        demo.launch(
            inbrowser=True,
            share=False,
            quiet=True
        )
    else:
        logger.info("Launching as web server on port 7860")
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False
        )
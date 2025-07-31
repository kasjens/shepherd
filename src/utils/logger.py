import logging
import logging.handlers
import sys
import os
from pathlib import Path
from datetime import datetime
import json


class ShepherdLogger:
    _instance = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._logger is None:
            self._setup_logger()
    
    def _setup_logger(self):
        """Set up comprehensive logging with rotation"""
        # Get project root directory
        project_root = Path(__file__).parent.parent.parent
        logs_dir = project_root / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # Create main logger
        self._logger = logging.getLogger('shepherd')
        self._logger.setLevel(logging.DEBUG)
        
        # Clear any existing handlers
        self._logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-20s | %(filename)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # 1. Main application log with rotation
        main_log_file = logs_dir / "shepherd.log"
        file_handler = logging.handlers.RotatingFileHandler(
            main_log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        self._logger.addHandler(file_handler)
        
        # 2. Error-only log
        error_log_file = logs_dir / "shepherd_errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        self._logger.addHandler(error_handler)
        
        # 3. Daily log files
        daily_log_file = logs_dir / f"shepherd_{datetime.now().strftime('%Y%m%d')}.log"
        daily_handler = logging.handlers.TimedRotatingFileHandler(
            daily_log_file,
            when='midnight',
            interval=1,
            backupCount=30,  # Keep 30 days
            encoding='utf-8'
        )
        daily_handler.setLevel(logging.INFO)
        daily_handler.setFormatter(detailed_formatter)
        self._logger.addHandler(daily_handler)
        
        # 4. Console handler (only for INFO and above)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        self._logger.addHandler(console_handler)
        
        # 5. JSON structured log for analysis
        json_log_file = logs_dir / "shepherd_structured.log"
        json_handler = logging.handlers.RotatingFileHandler(
            json_log_file,
            maxBytes=20*1024*1024,  # 20MB
            backupCount=3,
            encoding='utf-8'
        )
        json_handler.setLevel(logging.DEBUG)
        json_handler.setFormatter(self.JSONFormatter())
        self._logger.addHandler(json_handler)
        
        # Log startup
        self._logger.info("=" * 60)
        self._logger.info(f"Shepherd Logger initialized - Session started")
        self._logger.info(f"Python version: {sys.version}")
        self._logger.info(f"Working directory: {os.getcwd()}")
        self._logger.info(f"Log directory: {logs_dir}")
        self._logger.info("=" * 60)
    
    class JSONFormatter(logging.Formatter):
        """Custom formatter to output logs in JSON format"""
        def format(self, record):
            log_entry = {
                'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno,
                'message': record.getMessage(),
                'thread': record.thread,
                'process': record.process
            }
            
            # Add exception info if present
            if record.exc_info:
                log_entry['exception'] = self.formatException(record.exc_info)
            
            # Add extra fields if present
            if hasattr(record, 'extra_data'):
                log_entry['extra'] = record.extra_data
            
            return json.dumps(log_entry, ensure_ascii=False)
    
    def get_logger(self, name=None):
        """Get a logger instance"""
        if name:
            return logging.getLogger(f'shepherd.{name}')
        return self._logger
    
    def log_workflow_start(self, workflow_id, pattern, analysis):
        """Log workflow start with structured data"""
        logger = self.get_logger('workflow')
        extra_data = {
            'workflow_id': workflow_id,
            'pattern': pattern.value if hasattr(pattern, 'value') else str(pattern),
            'complexity': analysis.complexity_score,
            'task_types': analysis.task_types,
            'team_size': analysis.team_size_needed
        }
        logger.info(f"Workflow started: {workflow_id}", extra={'extra_data': extra_data})
    
    def log_workflow_end(self, workflow_id, status, execution_time, errors=None):
        """Log workflow completion with structured data"""
        logger = self.get_logger('workflow')
        extra_data = {
            'workflow_id': workflow_id,
            'status': status.value if hasattr(status, 'value') else str(status),
            'execution_time': execution_time,
            'error_count': len(errors) if errors else 0
        }
        if errors:
            extra_data['errors'] = errors
        
        if errors:
            logger.error(f"Workflow completed with errors: {workflow_id}", extra={'extra_data': extra_data})
        else:
            logger.info(f"Workflow completed successfully: {workflow_id}", extra={'extra_data': extra_data})
    
    def log_agent_action(self, agent_id, agent_name, action, status, duration=None, error=None):
        """Log agent actions with structured data"""
        logger = self.get_logger('agent')
        extra_data = {
            'agent_id': agent_id,
            'agent_name': agent_name,
            'action': action,
            'status': status,
            'duration': duration
        }
        if error:
            extra_data['error'] = str(error)
        
        if error:
            logger.error(f"Agent action failed: {agent_name} - {action}", extra={'extra_data': extra_data})
        else:
            logger.info(f"Agent action: {agent_name} - {action}", extra={'extra_data': extra_data})
    
    def log_prompt_analysis(self, request, analysis):
        """Log prompt analysis results"""
        logger = self.get_logger('analysis')
        extra_data = {
            'request_length': len(request),
            'complexity_score': analysis.complexity_score,
            'urgency_score': analysis.urgency_score,
            'quality_requirements': analysis.quality_requirements,
            'task_types': analysis.task_types,
            'recommended_pattern': analysis.recommended_pattern.value,
            'confidence': analysis.confidence,
            'dependencies': analysis.dependencies,
            'parallel_potential': analysis.parallel_potential
        }
        logger.info(f"Prompt analyzed: {request[:100]}...", extra={'extra_data': extra_data})
    
    def log_system_info(self, info_type, data):
        """Log system information"""
        logger = self.get_logger('system')
        logger.info(f"System info - {info_type}: {data}")
    
    def log_user_interaction(self, interaction_type, data):
        """Log user interactions"""
        logger = self.get_logger('ui')
        extra_data = {'interaction_type': interaction_type, 'data': data}
        logger.info(f"User interaction: {interaction_type}", extra={'extra_data': extra_data})


# Global logger instance
def get_logger(name=None):
    """Get logger instance - main entry point"""
    return ShepherdLogger().get_logger(name)


# Convenience functions
def log_workflow_start(workflow_id, pattern, analysis):
    return ShepherdLogger().log_workflow_start(workflow_id, pattern, analysis)


def log_workflow_end(workflow_id, status, execution_time, errors=None):
    return ShepherdLogger().log_workflow_end(workflow_id, status, execution_time, errors)


def log_agent_action(agent_id, agent_name, action, status, duration=None, error=None):
    return ShepherdLogger().log_agent_action(agent_id, agent_name, action, status, duration, error)


def log_prompt_analysis(request, analysis):
    return ShepherdLogger().log_prompt_analysis(request, analysis)


def log_system_info(info_type, data):
    return ShepherdLogger().log_system_info(info_type, data)


def log_user_interaction(interaction_type, data):
    return ShepherdLogger().log_user_interaction(interaction_type, data)
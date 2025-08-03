"""
Calculator tool for mathematical computations.

Provides safe mathematical expression evaluation with support for
basic arithmetic, functions, and constants.
"""

import ast
import math
import operator
from typing import Dict, Any, List

from ..base_tool import BaseTool, ToolCategory, ToolParameter, ToolResult


class CalculatorTool(BaseTool):
    """
    Calculator tool for evaluating mathematical expressions.
    
    Supports:
    - Basic arithmetic: +, -, *, /, //, %, **
    - Mathematical functions: sin, cos, tan, log, sqrt, etc.
    - Constants: pi, e
    - Safe evaluation without code execution risks
    """
    
    @property
    def name(self) -> str:
        return "calculator"
    
    @property
    def description(self) -> str:
        return "Safely evaluate mathematical expressions and perform calculations"
    
    @property
    def category(self) -> ToolCategory:
        return ToolCategory.COMPUTATION
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="expression",
                type="str",
                description="Mathematical expression to evaluate (e.g., '2 + 2', 'sin(pi/2)', 'sqrt(16)')",
                required=True
            )
        ]
    
    @property
    def usage_examples(self) -> List[Dict[str, Any]]:
        return [
            {
                "description": "Basic arithmetic",
                "parameters": {"expression": "2 + 2 * 3"},
                "expected_result": 8
            },
            {
                "description": "Using functions",
                "parameters": {"expression": "sqrt(16) + sin(pi/2)"},
                "expected_result": 5.0
            },
            {
                "description": "Complex calculation",
                "parameters": {"expression": "log(100, 10) ** 2"},
                "expected_result": 4.0
            }
        ]
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """
        Execute mathematical calculation.
        
        Args:
            parameters: Must contain 'expression' key
            
        Returns:
            ToolResult with calculated value or error
        """
        expression = parameters.get("expression", "")
        
        if not expression:
            return ToolResult(
                success=False,
                data=None,
                error="No expression provided"
            )
        
        try:
            # Evaluate expression safely
            result = self._safe_eval(expression)
            
            return ToolResult(
                success=True,
                data={
                    "expression": expression,
                    "result": result,
                    "type": type(result).__name__
                }
            )
            
        except ValueError as e:
            return ToolResult(
                success=False,
                data=None,
                error=f"Invalid expression: {str(e)}"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                data=None,
                error=f"Calculation error: {str(e)}"
            )
    
    def _safe_eval(self, expression: str) -> float:
        """
        Safely evaluate mathematical expression.
        
        Uses AST parsing to ensure only mathematical operations are performed,
        preventing arbitrary code execution.
        
        Args:
            expression: Mathematical expression string
            
        Returns:
            Calculated result
            
        Raises:
            ValueError: If expression contains unsafe operations
        """
        # Allowed operators
        operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.FloorDiv: operator.floordiv,
            ast.Mod: operator.mod,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }
        
        # Allowed functions
        allowed_functions = {
            'abs': abs,
            'round': round,
            'min': min,
            'max': max,
            'sum': sum,
            'len': len,
            # Math functions
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'asin': math.asin,
            'acos': math.acos,
            'atan': math.atan,
            'atan2': math.atan2,
            'sinh': math.sinh,
            'cosh': math.cosh,
            'tanh': math.tanh,
            'log': math.log,
            'log10': math.log10,
            'log2': math.log2,
            'exp': math.exp,
            'sqrt': math.sqrt,
            'pow': pow,
            'ceil': math.ceil,
            'floor': math.floor,
            'degrees': math.degrees,
            'radians': math.radians,
        }
        
        # Allowed constants
        allowed_names = {
            'pi': math.pi,
            'e': math.e,
            'tau': math.tau,
            'inf': math.inf,
        }
        
        def _eval(node):
            if isinstance(node, ast.Constant):  # Python 3.8+
                return node.value
            elif isinstance(node, ast.Num):  # Python < 3.8
                return node.n
            elif isinstance(node, ast.Name):
                if node.id in allowed_names:
                    return allowed_names[node.id]
                raise ValueError(f"Name '{node.id}' is not allowed")
            elif isinstance(node, ast.BinOp):
                left = _eval(node.left)
                right = _eval(node.right)
                return operators[type(node.op)](left, right)
            elif isinstance(node, ast.UnaryOp):
                operand = _eval(node.operand)
                return operators[type(node.op)](operand)
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name in allowed_functions:
                        args = [_eval(arg) for arg in node.args]
                        return allowed_functions[func_name](*args)
                    else:
                        raise ValueError(f"Function '{func_name}' is not allowed")
                else:
                    raise ValueError("Complex function calls are not allowed")
            elif isinstance(node, ast.Compare):
                # Allow comparisons for min/max operations
                left = _eval(node.left)
                comparisons = []
                for op, comp in zip(node.ops, node.comparators):
                    right = _eval(comp)
                    if isinstance(op, ast.Lt):
                        comparisons.append(left < right)
                    elif isinstance(op, ast.LtE):
                        comparisons.append(left <= right)
                    elif isinstance(op, ast.Gt):
                        comparisons.append(left > right)
                    elif isinstance(op, ast.GtE):
                        comparisons.append(left >= right)
                    elif isinstance(op, ast.Eq):
                        comparisons.append(left == right)
                    elif isinstance(op, ast.NotEq):
                        comparisons.append(left != right)
                    else:
                        raise ValueError(f"Comparison operator {type(op).__name__} is not allowed")
                    left = right
                return all(comparisons)
            else:
                raise ValueError(f"Expression type {type(node).__name__} is not allowed")
        
        try:
            # Parse expression
            tree = ast.parse(expression, mode='eval')
            
            # Evaluate safely
            result = _eval(tree.body)
            
            # Convert to float if numeric
            if isinstance(result, (int, float)):
                return float(result)
            return result
            
        except SyntaxError:
            raise ValueError("Invalid mathematical expression syntax")
        except ZeroDivisionError:
            raise ValueError("Division by zero")
        except OverflowError:
            raise ValueError("Result too large to compute")
        except Exception as e:
            raise ValueError(f"Evaluation error: {str(e)}")
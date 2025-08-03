"""
Unit tests for CalculatorTool.
"""

import pytest
import asyncio

from src.tools.core.calculator import CalculatorTool
from src.tools.base_tool import ToolResult


class TestCalculatorTool:
    """Test cases for CalculatorTool."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.calculator = CalculatorTool()
    
    def test_tool_properties(self):
        """Test tool basic properties."""
        assert self.calculator.name == "calculator"
        assert "mathematical" in self.calculator.description.lower()
        assert len(self.calculator.parameters) == 1
        assert self.calculator.parameters[0].name == "expression"
    
    @pytest.mark.asyncio
    async def test_basic_arithmetic(self):
        """Test basic arithmetic operations."""
        test_cases = [
            ("2 + 2", 4.0),
            ("10 - 5", 5.0),
            ("3 * 4", 12.0),
            ("15 / 3", 5.0),
            ("2 ** 3", 8.0),
            ("17 % 5", 2.0),
        ]
        
        for expression, expected in test_cases:
            result = await self.calculator.execute({"expression": expression})
            
            assert result.success, f"Failed to execute: {expression}"
            assert result.data["result"] == expected, f"Wrong result for {expression}"
            assert result.data["expression"] == expression
    
    @pytest.mark.asyncio
    async def test_mathematical_functions(self):
        """Test mathematical functions."""
        test_cases = [
            ("sin(0)", 0.0),
            ("cos(0)", 1.0),
            ("sqrt(16)", 4.0),
            ("abs(-5)", 5.0),
            ("round(3.7)", 4.0),
            ("max(1, 2, 3)", 3),
            ("min(1, 2, 3)", 1),
        ]
        
        for expression, expected in test_cases:
            result = await self.calculator.execute({"expression": expression})
            
            assert result.success, f"Failed to execute: {expression}"
            assert abs(result.data["result"] - expected) < 1e-10, f"Wrong result for {expression}"
    
    @pytest.mark.asyncio
    async def test_constants(self):
        """Test mathematical constants."""
        import math
        
        test_cases = [
            ("pi", math.pi),
            ("e", math.e),
            ("tau", math.tau),
        ]
        
        for expression, expected in test_cases:
            result = await self.calculator.execute({"expression": expression})
            
            assert result.success, f"Failed to execute: {expression}"
            assert abs(result.data["result"] - expected) < 1e-10, f"Wrong result for {expression}"
    
    @pytest.mark.asyncio
    async def test_complex_expressions(self):
        """Test complex mathematical expressions."""
        test_cases = [
            ("2 + 3 * 4", 14.0),  # Order of operations
            ("(2 + 3) * 4", 20.0),  # Parentheses
            ("sin(pi/2)", 1.0),  # Functions with constants
            ("sqrt(2**2 + 3**2)", 3.605551275463989),  # Nested operations
            ("log(100, 10)", 2.0),  # Function with multiple arguments
        ]
        
        for expression, expected in test_cases:
            result = await self.calculator.execute({"expression": expression})
            
            assert result.success, f"Failed to execute: {expression}"
            assert abs(result.data["result"] - expected) < 1e-10, f"Wrong result for {expression}"
    
    @pytest.mark.asyncio
    async def test_invalid_expressions(self):
        """Test handling of invalid expressions."""
        invalid_cases = [
            "",  # Empty expression
            "2 +",  # Incomplete expression
            "invalid_function(1)",  # Unknown function
            "import os",  # Code injection attempt
            "exec('print(1)')",  # Code execution attempt
            "2 / 0",  # Division by zero
        ]
        
        for expression in invalid_cases:
            result = await self.calculator.execute({"expression": expression})
            assert not result.success, f"Should have failed: {expression}"
            assert result.error is not None
    
    @pytest.mark.asyncio
    async def test_parameter_validation(self):
        """Test parameter validation."""
        # Missing expression
        result = await self.calculator.execute({})
        assert not result.success
        assert "expression" in result.error.lower()
        
        # Empty expression
        result = await self.calculator.execute({"expression": ""})
        assert not result.success
        assert "no expression" in result.error.lower()
    
    @pytest.mark.asyncio
    async def test_safe_execution_timeout(self):
        """Test that safe_execute handles timeouts properly."""
        # This would timeout if we had a very complex calculation
        # For now, test a simple case to ensure safe_execute works
        result = await self.calculator.safe_execute({"expression": "2 + 2"}, timeout=1)
        assert result.success
        assert result.data["result"] == 4.0
        assert result.execution_time > 0
    
    def test_usage_examples(self):
        """Test that usage examples are properly defined."""
        examples = self.calculator.usage_examples
        assert len(examples) > 0
        
        for example in examples:
            assert "description" in example
            assert "parameters" in example
            assert "expression" in example["parameters"]
    
    def test_parameter_definitions(self):
        """Test parameter definitions are correct."""
        params = self.calculator.parameters
        assert len(params) == 1
        
        expr_param = params[0]
        assert expr_param.name == "expression"
        assert expr_param.type == "str"
        assert expr_param.required is True
        assert expr_param.description is not None
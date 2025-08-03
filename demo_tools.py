#!/usr/bin/env python3
"""
Demo script for Phase 4: Tool Use Foundation

Demonstrates the tool system capabilities with agents.
"""

import asyncio
import tempfile
from pathlib import Path

from src.agents.base_agent import BaseAgent
from src.tools.builtin_tools import get_tool_info_summary


class DemoAgent(BaseAgent):
    """Demo agent for showcasing tool capabilities."""
    
    def create_crew_agent(self):
        return None  # Mock implementation


async def demo_calculator_tool():
    """Demonstrate calculator tool."""
    print("\n🧮 Calculator Tool Demo")
    print("=" * 40)
    
    agent = DemoAgent("calculator_agent", "mathematician", "Solve mathematical problems")
    
    test_expressions = [
        "2 + 2",
        "sqrt(16) + sin(pi/2)",
        "log(100, 10) ** 2",
        "((5 + 3) * 2) / 4"
    ]
    
    for expr in test_expressions:
        result = await agent.execute_tool("calculator", {"expression": expr})
        if result.success:
            print(f"✅ {expr} = {result.data['result']}")
        else:
            print(f"❌ {expr} → Error: {result.error}")


async def demo_web_search_tool():
    """Demonstrate web search tool."""
    print("\n🔍 Web Search Tool Demo")
    print("=" * 40)
    
    agent = DemoAgent("research_agent", "researcher", "Find information")
    
    queries = [
        ("artificial intelligence", 3),
        ("python programming", 2),
        ("climate change", 1)
    ]
    
    for query, max_results in queries:
        result = await agent.execute_tool("web_search", {
            "query": query,
            "max_results": max_results
        })
        
        if result.success:
            print(f"✅ Search: '{query}' → {len(result.data['results'])} results")
            for i, res in enumerate(result.data['results'], 1):
                print(f"   {i}. {res['title'][:50]}...")
        else:
            print(f"❌ Search: '{query}' → Error: {result.error}")


async def demo_file_operations_tool():
    """Demonstrate file operations tool."""
    print("\n📁 File Operations Tool Demo")
    print("=" * 40)
    
    agent = DemoAgent("file_agent", "file_manager", "Manage files")
    from src.tools.base_tool import ToolPermission
    agent.add_tool_permission(ToolPermission.WRITE)
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        agent.set_project_folder(temp_dir)
        
        # Write a file
        result = await agent.execute_tool("file_operations", {
            "operation": "write",
            "path": "demo.txt",
            "content": "Hello from Shepherd Tool System!\nThis is a demonstration of file operations."
        })
        
        if result.success:
            print("✅ Created demo.txt")
        else:
            print(f"❌ Write failed: {result.error}")
            return
        
        # Read the file
        result = await agent.execute_tool("file_operations", {
            "operation": "read",
            "path": "demo.txt"
        })
        
        if result.success:
            print(f"✅ Read demo.txt ({result.data['size']} bytes)")
            print(f"   Content: {result.data['content'][:50]}...")
        else:
            print(f"❌ Read failed: {result.error}")
        
        # List directory
        result = await agent.execute_tool("file_operations", {
            "operation": "list",
            "path": "."
        })
        
        if result.success:
            print(f"✅ Directory listing: {result.data['count']} items")
            for item in result.data['items']:
                print(f"   - {item['name']} ({item['type']})")
        else:
            print(f"❌ List failed: {result.error}")


async def demo_agent_capabilities():
    """Demonstrate agent tool integration features."""
    print("\n🤖 Agent Tool Integration Demo")
    print("=" * 40)
    
    agent = DemoAgent("smart_agent", "assistant", "Provide intelligent assistance")
    
    # Show available tools
    tools = agent.get_available_tools()
    print(f"✅ Agent has access to {len(tools)} tools:")
    for tool in tools:
        print(f"   - {tool['name']}: {tool['description'][:50]}...")
    
    # Tool suggestion
    print("\n🎯 Tool Suggestions:")
    test_tasks = [
        "Calculate the area of a circle with radius 5",
        "Find information about machine learning",
        "Read the configuration file",
        "Save the results to a file"
    ]
    
    for task in test_tasks:
        suggestions = await agent.select_tools_for_task(task)
        print(f"   Task: {task[:40]}... → Tools: {suggestions}")
    
    # Execute a tool and check statistics
    await agent.execute_tool("calculator", {"expression": "pi * 5**2"})
    stats = await agent.get_tool_usage_statistics()
    
    print(f"\n📊 Usage Statistics:")
    print(f"   Total executions: {stats['total_executions']}")
    print(f"   Success rate: {stats['success_rate']:.1%}")
    print(f"   Tools used: {list(stats['tools_used'].keys())}")


def demo_tool_system_overview():
    """Show tool system overview."""
    print("\n🔧 Tool System Overview")
    print("=" * 40)
    
    summary = get_tool_info_summary()
    
    print(f"✅ Total tools registered: {summary['total_tools']}")
    print(f"✅ Tool categories: {list(summary['categories'].keys())}")
    
    print("\n📋 Available Tools:")
    for tool in summary['tools']:
        print(f"   • {tool['name']}: {tool['description']}")
        print(f"     Category: {tool['category']}, Parameters: {tool['parameters']}")
        print(f"     Permissions: {', '.join(tool['required_permissions'])}")


async def main():
    """Run the tool system demo."""
    print("🐑 Shepherd Phase 4: Tool Use Foundation Demo")
    print("=" * 50)
    
    demo_tool_system_overview()
    
    await demo_calculator_tool()
    await demo_web_search_tool()
    await demo_file_operations_tool()
    await demo_agent_capabilities()
    
    print("\n🎉 Demo Complete!")
    print("✅ Phase 4: Tool Use Foundation successfully implemented!")
    print("\nFeatures demonstrated:")
    print("  • Tool registry and discovery")
    print("  • Permission-based access control")
    print("  • Tool execution engine with monitoring")
    print("  • Agent-tool integration")
    print("  • Built-in tools: Calculator, Web Search, File Operations")
    print("  • Comprehensive error handling and validation")


if __name__ == "__main__":
    asyncio.run(main())
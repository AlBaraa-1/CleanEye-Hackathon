"""
CleanEye MCP Client Example
----------------------------
Demonstrates how to use CleanEye as an MCP agent from Python.
This shows the agent-to-agent interaction pattern.
"""

import asyncio
import json
from pathlib import Path

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("MCP not installed. Run: pip install mcp")
    exit(1)


async def demo_cleaneye_agent():
    """
    Demonstrate CleanEye MCP agent capabilities.
    """
    print("🤖 CleanEye MCP Agent Demo")
    print("=" * 60)
    
    # Path to the MCP server
    server_script = Path(__file__).parent / "mcp_server.py"
    
    # Configure server parameters
    server_params = StdioServerParameters(
        command="python",
        args=[str(server_script)],
        env=None
    )
    
    print("📡 Connecting to CleanEye MCP server...")
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                await session.initialize()
                print("✅ Connected!\n")
                
                # List available tools
                print("🔧 Available Tools:")
                tools_response = await session.list_tools()
                for tool in tools_response.tools:
                    print(f"  - {tool.name}: {tool.description[:80]}...")
                print()
                
                # Demo 1: Detect garbage in an image
                print("📸 Demo 1: Detecting garbage in an image...")
                print("-" * 60)
                
                test_image = Path(__file__).parent / "media"
                if test_image.exists():
                    test_images = list(test_image.glob("*.jpg")) + list(test_image.glob("*.png"))
                    if test_images:
                        image_path = str(test_images[0])
                        print(f"Analyzing: {test_images[0].name}")
                        
                        result = await session.call_tool(
                            "detect_garbage_image",
                            arguments={
                                "image_path": image_path,
                                "confidence": 0.3
                            }
                        )
                        
                        # Parse and display result
                        if result.content and result.content[0].text:
                            data = json.loads(result.content[0].text)
                            print(f"\n📊 Detection Results:")
                            print(f"  Total detections: {data.get('total_detections', 0)}")
                            print(f"  Image size: {data.get('image_size', {})}")
                            print(f"  Severity: {data.get('severity', {}).get('level', 'unknown').upper()}")
                            
                            if data.get('category_breakdown'):
                                print(f"\n  Category breakdown:")
                                for cat, count in data['category_breakdown'].items():
                                    print(f"    - {cat}: {count}")
                            
                            print()
                    else:
                        print("⚠️  No test images found in media folder\n")
                else:
                    print("⚠️  Media folder not found\n")
                
                # Demo 2: Get detection statistics
                print("📈 Demo 2: Getting detection statistics...")
                print("-" * 60)
                
                stats_result = await session.call_tool(
                    "get_detection_statistics",
                    arguments={}
                )
                
                if stats_result.content and stats_result.content[0].text:
                    stats_data = json.loads(stats_result.content[0].text)
                    print(f"Status: {stats_data.get('status', 'N/A')}")
                    if stats_data.get('status') == 'no_data':
                        print(f"Message: {stats_data.get('message', 'N/A')}")
                    else:
                        print(f"Statistics: {json.dumps(stats_data, indent=2)}")
                    print()
                
                # Demo 3: Analyze area severity
                print("🎯 Demo 3: Analyzing area severity...")
                print("-" * 60)
                
                severity_result = await session.call_tool(
                    "analyze_area_severity",
                    arguments={
                        "detection_count": 12,
                        "image_area": 1920 * 1080,
                        "detection_areas": [5000, 3000, 8000, 4500, 6000, 2500, 7000, 3500, 9000, 4000, 5500, 6500]
                    }
                )
                
                if severity_result.content and severity_result.content[0].text:
                    severity_data = json.loads(severity_result.content[0].text)
                    print(f"Severity Level: {severity_data.get('severity', {}).get('level', 'N/A').upper()}")
                    print(f"Cleanup Priority: {severity_data.get('cleanup_priority', 'N/A').upper()}")
                    print(f"Recommendation: {severity_data.get('recommendation', 'N/A')}")
                    print(f"Metrics: {json.dumps(severity_data.get('metrics', {}), indent=2)}")
                    print()
                
                # Demo 4: List detection reports
                print("📋 Demo 4: Listing detection reports...")
                print("-" * 60)
                
                reports_result = await session.call_tool(
                    "get_detection_reports",
                    arguments={"limit": 5}
                )
                
                if reports_result.content and reports_result.content[0].text:
                    reports_data = json.loads(reports_result.content[0].text)
                    if reports_data.get('status') == 'no_reports':
                        print(f"Message: {reports_data.get('message', 'N/A')}")
                    else:
                        print(f"Total reports: {reports_data.get('total_reports', 0)}")
                        for report in reports_data.get('reports', [])[:3]:
                            print(f"  - {report.get('report_id', 'N/A')}: {report.get('num_files', 0)} files")
                    print()
                
                print("=" * 60)
                print("✅ Demo complete!")
                print("\n💡 Integration Ideas:")
                print("  1. Connect to Claude Desktop for natural language control")
                print("  2. Build a multi-agent system with dispatcher + analyzer")
                print("  3. Create automated cleanup scheduling workflows")
                print("  4. Integrate with city infrastructure APIs")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def demo_agent_reasoning():
    """
    Simulate an LLM agent reasoning with CleanEye tools.
    This shows how an AI agent would use CleanEye in a workflow.
    """
    print("\n" + "=" * 60)
    print("🧠 Simulated Agent Reasoning Demo")
    print("=" * 60)
    print()
    
    print("Agent Task: Monitor city area and dispatch cleanup crew\n")
    
    print("Agent thinking...")
    print("  💭 I need to analyze the current state of the area")
    print("  💭 Let me use the detect_garbage_image tool")
    print("  🔧 [Calling: detect_garbage_image]")
    print("  📊 Result: 15 items detected (8 garbage_bags, 5 trash, 2 waste)")
    print()
    
    print("  💭 That's quite a lot. Let me assess the severity")
    print("  🔧 [Calling: analyze_area_severity]")
    print("  🎯 Result: SEVERE - Immediate cleanup required!")
    print()
    
    print("  💭 I should check if this is a trend")
    print("  🔧 [Calling: get_detection_statistics]")
    print("  📈 Result: Average of 12 detections per hour in this area")
    print()
    
    print("Agent Decision:")
    print("  ✅ Dispatch cleanup crew immediately")
    print("  ✅ Schedule follow-up inspection in 2 hours")
    print("  ✅ Flag this location as high-priority zone")
    print("  ✅ Generate incident report")
    print()
    
    print("🎯 This demonstrates how LLMs can reason with CleanEye tools!")


if __name__ == "__main__":
    print("\n" + "🌟" * 30 + "\n")
    print("  CleanEye MCP Agent - Hackathon Demo")
    print("  Making cities cleaner with AI agents")
    print("\n" + "🌟" * 30 + "\n")
    
    # Run the main demo
    asyncio.run(demo_cleaneye_agent())
    
    # Show agent reasoning simulation
    asyncio.run(demo_agent_reasoning())
    
    print("\n🚀 Ready for the MCP 1st Birthday Hackathon!")

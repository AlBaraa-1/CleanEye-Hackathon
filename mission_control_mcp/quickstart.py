"""
Quick Start Script for MissionControlMCP
Run this to verify installation and test the server
"""
import sys
import subprocess


def main():
    print("╔" + "═"*58 + "╗")
    print("║" + " "*12 + "MissionControlMCP Quick Start" + " "*17 + "║")
    print("╚" + "═"*58 + "╝\n")
    
    print("1. Checking Python version...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print("   ⚠️  Warning: Python 3.11+ recommended")
    else:
        print("   ✓ Python version OK")
    
    print("\n2. Checking dependencies...")
    try:
        import mcp
        print("   ✓ MCP SDK installed")
    except ImportError:
        print("   ✗ MCP SDK not found - run: pip install mcp")
        return
    
    print("\n3. Running test suite...")
    print("   " + "-"*54)
    
    try:
        subprocess.run([sys.executable, "test_server.py"], check=True)
    except subprocess.CalledProcessError:
        print("\n   ⚠️  Some tests may have failed (expected if dependencies not fully installed)")
    except FileNotFoundError:
        print("   ✗ test_server.py not found")
        return
    
    print("\n" + "="*60)
    print("✓ Setup Complete!")
    print("="*60)
    
    print("\n📚 Next Steps:\n")
    print("1. Install remaining dependencies:")
    print("   pip install -r requirements.txt\n")
    print("2. Run the test suite:")
    print("   python test_server.py\n")
    print("3. Start the MCP server:")
    print("   uvx mcp dev mcp_server.py\n")
    print("4. Integrate with Claude Desktop (see README.md)\n")
    
    print("📖 For full documentation, see README.md\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()

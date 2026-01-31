"""Main entry point for the Embedded Systems AI Agent"""

import os
import asyncio
import getpass

from src.cli import EmbeddedSystemsCLI


async def main():
    """Main execution function"""
    print("🚀 Starting Embedded Systems AI Agent with LangGraph...")

    # Get Groq API key
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        groq_api_key = getpass.getpass("Enter your Groq API key: ").strip()

    if not groq_api_key:
        print("❌ Groq API key is required")
        return

    try:
        # Initialize CLI
        cli = EmbeddedSystemsCLI(groq_api_key)

        print("✅ Web search enabled")

        # Run interactive session
        await cli.run_interactive_session()

    except Exception as e:
        print(f"❌ Failed to start agent: {e}")
        print("Make sure you have all required dependencies installed:")
        print("pip install -r requirements.txt")


if __name__ == "__main__":
    asyncio.run(main())

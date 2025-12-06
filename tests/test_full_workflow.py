#!/usr/bin/env python3
"""Test full research workflow with text-embedding-3-large"""
import asyncio
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

from gpt_researcher import GPTResearcher
from gpt_researcher.utils.enum import ReportType, ReportSource

async def test_research_workflow():
    """Test a simple research query with embeddings"""
    print("=" * 60)
    print("Testing Full Research Workflow with text-embedding-3-large")
    print("=" * 60)

    try:
        # Create researcher with a simple query
        print("\nInitializing GPTResearcher...")
        researcher = GPTResearcher(
            query="What is Python?",
            report_type=ReportType.ResearchReport.value,
            report_source=ReportSource.Web.value
        )
        print("✓ Researcher initialized successfully!")

        # Conduct research (this will use embeddings)
        print("\nConducting research...")
        print("(This will test embeddings with actual content)")
        await researcher.conduct_research()
        print(f"✓ Research completed!")
        print(f"  Context length: {len(researcher.context)} characters")
        print(f"  Visited URLs: {len(researcher.visited_urls)}")

        # Generate report
        print("\nGenerating report...")
        report = await researcher.write_report()
        print(f"✓ Report generated!")
        print(f"  Report length: {len(report)} characters")
        print(f"\nFirst 200 characters of report:")
        print(f"{report[:200]}...")

        return True

    except Exception as e:
        print(f"\n✗ Error during research workflow: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_research_workflow())
    print("\n" + "=" * 60)
    if success:
        print("✓ FULL WORKFLOW TEST SUCCESSFUL!")
        print("=" * 60)
        print("\nThe text-embedding-3-large model works correctly")
        print("in the complete research workflow.")
        sys.exit(0)
    else:
        print("✗ WORKFLOW TEST FAILED")
        print("=" * 60)
        sys.exit(1)

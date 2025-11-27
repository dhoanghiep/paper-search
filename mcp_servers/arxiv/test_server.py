#!/usr/bin/env python3
import asyncio
import json
from server import handle_request

async def test_tools():
    """Test all ArXiv MCP tools"""
    
    print("Testing search_papers...")
    result = await handle_request({
        "method": "search_papers",
        "params": {"query": "machine learning", "max_results": 3}
    })
    print(f"Found {len(result.get('papers', []))} papers")
    if result.get('papers'):
        print(f"First paper: {result['papers'][0]['title'][:60]}...")
    
    print("\nTesting get_recent_papers...")
    result = await handle_request({
        "method": "get_recent_papers",
        "params": {"category": "cs.AI", "max_results": 3}
    })
    print(f"Found {len(result.get('papers', []))} recent papers")
    if result.get('papers'):
        print(f"First paper: {result['papers'][0]['title'][:60]}...")
    
    print("\nTesting get_paper_details...")
    if result.get('papers'):
        arxiv_id = result['papers'][0]['arxiv_id']
        detail = await handle_request({
            "method": "get_paper_details",
            "params": {"arxiv_id": arxiv_id}
        })
        print(f"Paper ID: {detail.get('arxiv_id')}")
        print(f"Authors: {', '.join(detail.get('authors', [])[:3])}")
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(test_tools())

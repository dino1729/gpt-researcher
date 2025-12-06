#!/usr/bin/env python3
"""Test script to verify the NVIDIA embedding fix works"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gpt_researcher.config.config import Config
from gpt_researcher.memory.embeddings import Memory

def test_embedding():
    """Test that NVIDIA embeddings work with the input_type fix"""
    print("=" * 60)
    print("Testing NVIDIA Embedding Model Fix")
    print("=" * 60)
    
    # Get config
    cfg = Config()
    
    print(f"\nCurrent embedding configuration:")
    print(f"  Provider: {cfg.embedding_provider}")
    print(f"  Model: {cfg.embedding_model}")
    print(f"  Kwargs: {cfg.embedding_kwargs}")
    
    try:
        # Create memory with embeddings
        print(f"\nInitializing embeddings...")
        memory = Memory(
            cfg.embedding_provider,
            cfg.embedding_model,
            **cfg.embedding_kwargs
        )
        
        embeddings = memory.get_embeddings()
        print(f"✓ Embeddings initialized successfully!")
        
        # Test embedding a query
        print(f"\nTesting embedding generation...")
        test_text = "What are the latest developments in AI?"
        
        try:
            result = embeddings.embed_query(test_text)
            print(f"✓ Successfully created embeddings!")
            print(f"  Dimensions: {len(result)}")
            print(f"  First 5 values: {result[:5]}")
            
            return True
        except Exception as e:
            print(f"✗ Failed to generate embeddings: {e}")
            return False
            
    except Exception as e:
        print(f"✗ Failed to initialize embeddings: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_embedding()
    print("\n" + "=" * 60)
    if success:
        print("✓ EMBEDDING FIX SUCCESSFUL!")
        print("=" * 60)
        print("\nThe NVIDIA embedding model is now working correctly.")
        print("You can now run research queries without embedding errors.")
        sys.exit(0)
    else:
        print("✗ EMBEDDING TEST FAILED")
        print("=" * 60)
        print("\nPlease check the error messages above.")
        sys.exit(1)


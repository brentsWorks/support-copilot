#!/usr/bin/env python3
"""
Test script for EmbeddingService functionality.
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.services.embedding_service import EmbeddingService


async def test_embedding_service():
    """Test the EmbeddingService functionality."""
    
    print("🧪 Testing EmbeddingService")
    print("=" * 40)
    
    service = EmbeddingService()
    
    # Test 1: Connection test
    print("\n1. Testing BigQuery connection...")
    try:
        result = await service.test_connection()
        if result["status"] == "success":
            print(f"✅ {result['message']}")
        else:
            print(f"❌ {result['message']}")
            return False
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False
    
    # Test 2: prepare_ticket_text method
    print("\n2. Testing prepare_ticket_text method...")
    
    # Test with complete ticket
    complete_ticket = {
        "ticket_subject": "Login Issues",
        "ticket_description": "User cannot log into their account",
        "ticket_resolution": "Reset password and cleared cache"
    }
    
    formatted_text = service.prepare_ticket_text(complete_ticket)
    expected = "Subject: Login Issues\nIssue: User cannot log into their account\nResolution: Reset password and cleared cache"
    
    if formatted_text == expected:
        print("✅ Complete ticket formatting works correctly")
    else:
        print(f"❌ Expected: {expected}")
        print(f"❌ Got: {formatted_text}")
        return False
    
    # Test with missing fields
    partial_ticket = {
        "subject": "Password Reset",
        "description": "Need password reset",
        # resolution is missing
    }
    
    formatted_text = service.prepare_ticket_text(partial_ticket)
    expected = "Subject: Password Reset\nIssue: Need password reset"
    
    if formatted_text == expected:
        print("✅ Partial ticket formatting works correctly")
    else:
        print(f"❌ Expected: {expected}")
        print(f"❌ Got: {formatted_text}")
        return False
    
    # Test with null/empty values
    ticket_with_nulls = {
        "ticket_subject": "Test Subject",
        "ticket_description": None,  # null value
        "ticket_resolution": ""      # empty string
    }
    
    formatted_text = service.prepare_ticket_text(ticket_with_nulls)
    expected = "Subject: Test Subject"
    
    if formatted_text == expected:
        print("✅ Null/empty value handling works correctly")
    else:
        print(f"❌ Expected: {expected}")
        print(f"❌ Got: {formatted_text}")
        return False
    
    # Test 3: generate_embedding method
    print("\n3. Testing generate_embedding method...")
    
    test_text = "Subject: Login Issues\nIssue: User cannot access their account\nResolution: Password reset required"
    
    try:
        embedding = await service.generate_embedding(test_text)
        
        if isinstance(embedding, list) and len(embedding) == 768:
            print(f"✅ Generated 768-dimensional embedding")
            print(f"   First 5 values: {embedding[:5]}")
        else:
            print(f"❌ Expected 768-dimensional list, got {type(embedding)} with length {len(embedding) if isinstance(embedding, list) else 'N/A'}")
            return False
            
    except Exception as e:
        print(f"❌ Embedding generation failed: {e}")
        return False
    
    # Test 4: generate_ticket_embedding method
    print("\n4. Testing generate_ticket_embedding method...")
    
    try:
        ticket_embedding = await service.generate_ticket_embedding(complete_ticket)
        
        if isinstance(ticket_embedding, list) and len(ticket_embedding) == 768:
            print(f"✅ Generated ticket embedding successfully")
            print(f"   Embedding dimension: {len(ticket_embedding)}")
        else:
            print(f"❌ Ticket embedding failed")
            return False
            
    except Exception as e:
        print(f"❌ Ticket embedding generation failed: {e}")
        return False
    
    print("\n" + "=" * 40)
    print("🎉 All EmbeddingService tests passed!")
    
    return True


async def main():
    """Main function to run the tests."""
    try:
        success = await test_embedding_service()
        if success:
            print("\n🚀 EmbeddingService is ready for use!")
        else:
            print("\n❌ Some tests failed. Check the output above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

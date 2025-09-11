#!/usr/bin/env python3
"""
Setup script for BigQuery ML text-embedding-004 model.
This script creates the necessary BigQuery ML model for text embeddings.
"""

import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.services.embedding_service import EmbeddingService
from app.core.config import settings


def setup_embedding_model():
    """Set up the BigQuery ML text-embedding-004 model."""
    
    print("🔧 Setting up BigQuery ML Text Embedding Model")
    print("=" * 50)
    
    service = EmbeddingService()
    
    # Create the text-embedding-004 model
    print(f"\n1. Creating {settings.EMBEDDING_MODEL_NAME} model...")
    
    model_name = f"{settings.EMBEDDING_MODEL_NAME}_model"
    
    create_model_query = f"""
    CREATE OR REPLACE MODEL `{settings.GOOGLE_CLOUD_PROJECT}.{settings.BIGQUERY_DATASET_ID}.{model_name}`
    REMOTE WITH CONNECTION `{settings.GOOGLE_CLOUD_PROJECT}.us-west1.vertex_ai_connection`
    OPTIONS (
        remote_service_type = 'CLOUD_AI_TEXT_EMBEDDING_MODEL_V1',
        endpoint = '{settings.EMBEDDING_MODEL_NAME}'
    )
    """
    
    try:
        print(f"Creating model: {model_name}")
        print(f"Using endpoint: {settings.EMBEDDING_MODEL_NAME}")
        
        query_job = service.client.query(create_model_query)
        query_job.result()  # Wait for completion
        
        print(f"✅ Model '{model_name}' created successfully!")
        
    except Exception as e:
        print(f"❌ Model creation failed: {e}")
        print("\n💡 Troubleshooting tips:")
        print("1. Ensure you have a Vertex AI connection named 'vertex_ai_connection'")
        print("2. Create the connection with: bq mk --connection --display_name='Vertex AI Connection' --connection_type=CLOUD_RESOURCE --location=us-west1 vertex_ai_connection")
        print("3. Grant the connection service account Vertex AI User role")
        return False
    
    # Test the model
    print(f"\n2. Testing the model...")
    
    test_query = f"""
    SELECT ml_generate_text_embedding_result
    FROM ML.GENERATE_TEXT_EMBEDDING(
        MODEL `{settings.GOOGLE_CLOUD_PROJECT}.{settings.BIGQUERY_DATASET_ID}.{model_name}`,
        (SELECT 'Hello, world! This is a test.' AS content)
    )
    """
    
    try:
        query_job = service.client.query(test_query)
        results = list(query_job.result())
        
        if results:
            embedding = results[0].ml_generate_text_embedding_result
            print(f"✅ Model test successful!")
            print(f"   Generated {len(embedding)}-dimensional embedding")
            print(f"   First 5 values: {embedding[:5]}")
            
            if len(embedding) == 768:
                print("✅ Confirmed: 768-dimensional embeddings as expected")
            else:
                print(f"⚠️  Warning: Expected 768 dimensions, got {len(embedding)}")
        else:
            print("❌ No results returned from model test")
            return False
            
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 BigQuery ML Text Embedding Model Setup Complete!")
    print(f"✅ Model: {settings.GOOGLE_CLOUD_PROJECT}.{settings.BIGQUERY_DATASET_ID}.{model_name}")
    print(f"✅ Endpoint: {settings.EMBEDDING_MODEL_NAME}")
    print("✅ Ready for production use!")
    
    return True


def main():
    """Main function to run the setup."""
    try:
        success = setup_embedding_model()
        if success:
            print("\n🚀 Setup completed successfully!")
            print("You can now use the EmbeddingService class to generate embeddings.")
        else:
            print("\n❌ Setup failed. Check the output above for details.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

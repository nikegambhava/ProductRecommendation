import asyncio
import os
import sys
import time
from dotenv import load_dotenv
from google.genai import types
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from agent import root_agent

# Import specialized agents for the runner
from .product_recommender import product_recommender

load_dotenv()

# Check if using Vertex AI (recommended for Cloud Run)
use_vertex_ai = os.environ.get('GOOGLE_GENAI_USE_VERTEXAI', 'False').lower() == 'true'

if use_vertex_ai:
    print("✅ Using Vertex AI (no API key required)")
else:
    # Verify API key for local development
    google_api_key = os.environ.get('GOOGLE_API_KEY', '')
    if not google_api_key:
        print("❌ GOOGLE_API_KEY is not set! Please set it in your .env file or set GOOGLE_GENAI_USE_VERTEXAI=True")
        sys.exit(1)
    print("✅ API key is configured.")
async def analyze_products(keyword, runner, session_service):
    """Recommend top products based on a keyword using the Product Recommender agent."""
    
    # Set up session
    session = session_service.create_session(
        app_name="multi_agent_product_recommender", user_id="cli_user"
    )

    # Create the user query content
    query = f"Suggest the 5 best products for: {keyword}"
    content = types.Content(role="user", parts=[types.Part(text=query)])

    print(f"\n🛍️  Recommending products for: '{keyword}'...")
    print("This may take a few seconds while we search and filter top options.")

    # Initialize variables
    result = ""
    search_count = 0

    # Run the agent and stream events
    async for event in runner.run_async(
        session_id=session.id,
        user_id="cli_user",
        new_message=content
    ):
        # Track when searches are being triggered
        if hasattr(event, 'content') and hasattr(event.content, 'parts'):
            for part in event.content.parts:
                if hasattr(part, 'function_call') and hasattr(part.function_call, 'name'):
                    if part.function_call.name == 'google_search':
                        search_count += 1
                        print(f"🔍 Search #{search_count}: Looking for top products...")
                elif hasattr(part, 'function_response'):
                    print("✅ Received search results")

        # Final response from agent
        if hasattr(event, 'is_final_response') and event.is_final_response:
            if hasattr(event, 'content') and hasattr(event.content, 'parts'):
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        result += part.text

    return result
async def main():
    print("\n===============================================")
    print("🛒  PRODUCT RECOMMENDER - CLI INTERFACE")
    print("===============================================")

    # Initialize session service and runner
    session_service = InMemorySessionService()
    runner = Runner(
        agent=product_recommender,  # Use the product recommendation agent here
        session_service=session_service,
        app_name="multi_agent_product_recommender",
    )

    # Get product keyword from user
    if len(sys.argv) > 1:
        keyword = " ".join(sys.argv[1:])  # Support multi-word keywords
    else:
        keyword = input("\nEnter a product keyword or category (e.g., 'gaming laptop'): ").strip()
        if not keyword:
            print("❌ No keyword entered. Exiting.")
            return

    try:
        start_time = time.time()
        result = await analyze_products(keyword, runner, session_service)
        end_time = time.time()

        print("\n===============================================")
        print(f"RECOMMENDATION COMPLETED IN {round(end_time - start_time, 1)} SECONDS")
        print("===============================================")

        print(result)

    except Exception as e:
        print(f"\n❌ Error during product recommendation: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())


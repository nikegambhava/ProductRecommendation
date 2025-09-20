from google.adk.agents import Agent
from google.adk.tools import google_search



product_recommender = Agent(
    model="gemini-2.0-flash",
    name="product_recommender",
    description="Suggests five best products based on a keyword or category.",
    instruction="""
You are a smart e-commerce assistant. Use the google_search tool to find 5 of the best products related to the specified keyword. Prioritize products with strong customer reviews, good ratings, and recent relevance. Avoid listing outdated or unavailable products.

Keyword: [Product Keyword]

For each product, provide:
1. Product Name
2. Brief description (1-2 sentences)
3. Price (if available)
4. Average rating or review summary (if available)
5. A direct link (if found)

Present the results as a numbered list of recommendations. Do not include any additional text beyond the list.
""",
    tools=[google_search]
)
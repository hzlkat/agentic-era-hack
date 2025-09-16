# test_agent.py
import asyncio
from vertexai import agent_engines  # requires google-cloud-aiplatform >= 1.111 with [adk,agent_engines]

RESOURCE_NAME = "projects/783020517917/locations/us-central1/reasoningEngines/8377297839281143808"

async def main():
    # Get the remote app by its ReasoningEngine resource name
    remote_app = agent_engines.get(RESOURCE_NAME)

    # Create a managed (server-side) session
    session = await remote_app.async_create_session(user_id="u_cli_test")

    # Stream a query
    final_text = None
    async for event in remote_app.async_stream_query(
        user_id="u_cli_test",
        session_id=session["id"],
        message="Please check the warranty clause.",
    ):
        parts = event.get("content", {}).get("parts", [])
        if parts and parts[0].get("text") and not parts[0].get("function_call"):
            final_text = parts[0]["text"]

    print("\n--- Final Response ---")
    print(final_text or "(no text response)")

if __name__ == "__main__":
    asyncio.run(main())

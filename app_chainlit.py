import chainlit as cl
from team.dsa_team import create_dsa_team
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.base import TaskResult
import asyncio

@cl.on_chat_start
async def start():
    """Initialize the DSA team when a new chat starts."""
    cl.user_session.set("team", create_dsa_team())
    await cl.Message(
        content="Welcome to PyAlgo Master, your personal DSA problem solver! Here you can ask for solutions to various data structures and algorithms problems."
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages and process DSA problems."""
    task = message.content
    team, local_exec = cl.user_session.get("team")
    
    # Create a message to indicate processing has started
    msg = cl.Message(content="")
    await msg.send()
    
    # Process the task asynchronously
    async def process_task():
        try:
            async for message in team.run_stream(task=TextMessage(content=task, source="User")):
                if isinstance(message, TextMessage):
                    msg.content += f"{message.source}: {message.content}\n\n"
                    await msg.update()
                elif isinstance(message, TaskResult):
                    msg.content += f"\nTask completed. Stop reason: {message.stop_reason}"
                    await msg.update()
        except Exception as e:
            msg.content = f"An error occurred: {str(e)}"
            await msg.update()
    
    # Run the task
    await process_task()

if __name__ == "__main__":
    # This is for running the app directly with: python app_chainlit.py
    from chainlit.cli import run_chainlit
    run_chainlit("app_chainlit.py")

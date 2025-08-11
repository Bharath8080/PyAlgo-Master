from autogen_agentchat.agents import AssistantAgent, CodeExecutorAgent
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core import CancellationToken
from dotenv import load_dotenv
import asyncio
import os

load_dotenv()
key = os.getenv("GROQ_API_KEY")

async def main():
    # 1) Configure the LLM client (now with structured_output=True)
    model_client = OpenAIChatCompletionClient(
        base_url="https://api.groq.com/openai/v1",
        model="llama-3.3-70b-versatile",
        api_key=key,
        model_info={
            "family": "llama",
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "structured_output": True,      # ← new required field
        }
    )

    # 2) Instantiate your two agents
    problem_solver_agent = AssistantAgent(
        name="DSA_Problem_Solver_Agent",
        description="An agent that solves DSA problems",
        model_client=model_client,
        system_message="""
You are an expert DSA problem‐solver agent.  

-- On the **first** time you get a task from the user, you MUST:
1) Outline your plan in 20 words.
2) Provide the Python code in a single ```python``` code‐block.
3) Do **not** explain, do **not** say “STOP.”

-- When you receive a message **from** the CodeExecutorAgent containing the code’s execution output:
4) Explain that output in 20 words (plain text).
5) Finally, output exactly `STOP` on its own line.

"""
    )

    local_exec = LocalCommandLineCodeExecutor(work_dir="temp", timeout=120)
    code_executor_agent = CodeExecutorAgent(
        name="code_executor_agent",
        code_executor=local_exec
    )

    # 3) Build your team using *instances* of both agents
    termination = TextMentionTermination("STOP")
    team = RoundRobinGroupChat(
        participants=[problem_solver_agent, code_executor_agent],
        termination_condition=termination,
        max_turns=10
    )

    # 4) Define the user task
    task = TextMessage(
        content="Write a simple Python code to add two numbers.",
        source="User"
    )

    # 5) Run the agents in a streaming loop and print outputs
    try:
        #await docker.start()
        async for message in team.run_stream(task=task):
            # print("=" * 40)
            # # message.content or message.text depending on your API
            # print(f"{message.source}: {message.content}")
            # print("=" * 40)

            # WITH THIS WE ARE GETTING AN ERROR AT END AS - Error: 'TaskResult' object has no attribute 'source'
            # this is because all the other messages other then last one are textmessages and at the end after everything is done the message type is task result

            if isinstance(message, TextMessage):
                print(f"{message.source}: {message.content}")
            elif isinstance(message, TaskResult):
                print(f"Stop Reason : {message.stop_reason}")

    except Exception as e:
        print(f"Error: {e}")

    #finally
        # await docker.stop()

if __name__ == "__main__":
    asyncio.run(main())

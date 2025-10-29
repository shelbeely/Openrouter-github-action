# src/agents/image_generator_agent.py

from agents import Agent
from src.tools.image_generator_tool import ImageGeneratorTool

def get_image_generator_agent():
    """
    Returns an agent that can generate images.
    """
    return Agent(
        name="Image Generator Agent",
        tools=[ImageGeneratorTool()],
        instructions="You are an image generation expert. Your goal is to generate an image based on the user's prompt.",
    )

# src/tools/image_generator_tool.py

from agents import FunctionTool, run_context
from openai import AsyncOpenAI
import json

client = AsyncOpenAI()

class ImageGeneratorTool(FunctionTool):
    def __init__(self):
        super().__init__(
            name="generate_image",
            description="Generates an image from a prompt using DALL-E.",
            params_json_schema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "The prompt to use for image generation."}
                },
                "required": ["prompt"],
            },
            on_invoke_tool=self.on_invoke_tool,
        )

    async def on_invoke_tool(self, context, tool_input: str) -> str:
        """
        Generates an image from a prompt using DALL-E.
        """
        data = json.loads(tool_input)
        prompt = data["prompt"]

        response = await client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        return response.data[0].url

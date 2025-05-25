from typing import List, TypedDict, Callable, Tuple
import re
import json

import chatapi


class Toolwrapper:
    """
    Callable[[List[str]], Tuple[bool, str]]
    Tools should always take a single list as their argument
    Tools should respond with a tuple (urgent: bool, response: str)
        when urgent is True, the LLM will be given the response right away
        when urgent is False, the response will go in the unimportant message queue for later
        urgent should normally be True for actions
    """
    def __init__(self, name: str, action: Callable[[List[str]], Tuple[bool, str]], manual: str):
        self.name = name
        self.action: Callable[[List[str]], Tuple[bool, str]] = action
        self.manual = manual


# gemini-2.5-flash-preview-04-17
# gemini-2.0-flash
# gemini-2.0-flash-lite
GEMINI_API_KEY = ""

class ToolLLM:
    def __init__(self, directions: str = "", tool_objects: List[Toolwrapper] = None, model: str = "gemini-2.0-flash"):
        self.response_instructions = """
OUTPUT FORMAT REQUIREMENTS:
Your response MUST strictly follow this two-part structure:
PART 1: THINKING PROCESS
- Begin your response with your step-by-step reasoning and plan.
- Detail the inputs received, your interpretation, and the sequence of actions you intend to take and why.
- Review the rules and guidelines associated with your actions and how you should follow them.
- Include what actions you won't be taking, or why you will be waiting before calling a certain action.
- End your thoughts with a clear plan of what you will be doing and why
- Think for as long as you need to
- Do not write any JSON in your thoughts
- This section MUST come before any JSON code.
PART 2: JSON ACTION LIST
- Following your thinking process, provide the JSON list containing the actions to be executed.
- Arguments should ALWAYS be passed as strings
- You may perform multiple actions in the same json list
- If no actions are required, end with an empty list: `[]`
- This JSON block MUST be the absolute final part of your response. No text should follow it.
- Json format: 
[
    { "action": "{action name}", "args": ["{argument1}", "{argument2}", "{argument3}"] },
    { "action": "{action name}", "args": ["{argument1}"] },
    { "action": "{action name}", "args": [] },
    { "action": "{action name}", "args": ["{argument1}", "{argument2}", "{argument3}", "{argument4}", "{argument5}"] }
]
"""

        self.directions: str = directions
        self.tool_instructions: str = ""

        self.unimportant_messages: List[str] = []

        self.tools: TypedDict[str, Toolwrapper] = {}
        if tool_objects is not None:
            for tool in tool_objects:
                self.tools[tool.name] = tool
                self.tool_instructions = f"{self.tool_instructions}{tool.manual}\n"

        initial_prompt = f"""
Primary directions:
{directions}

{self.response_instructions}

Available tools:
{self.tool_instructions}

Instructions are complete. Acknowledge your instructions and wait patiently.
        """

        self.llm = chatapi.FlashChat(initial_prompt, model=model)

    def seperate_llm_response(self, text: str) -> (str, str):
        prematch = re.search(r'^(.*?)\[', text, re.DOTALL)
        thought = prematch.group(1) if prematch else ''

        postmatch = re.search(r'\[.*\]', text, re.DOTALL)
        actions = postmatch.group(0) if postmatch else "[]"

        return thought, actions

    def preform_action(self, action_name: str, arguments: List[str]) -> str:
        tool: Toolwrapper = self.tools.get(action_name)

        if tool is None:
            return f"error: action '{action_name}' was not found"

        urgent, response = tool.action(arguments)

        response = f"{action_name}: {response}" if response != "" else response

        if urgent:
            return response

        self.unimportant_messages.append(response)
        return ""

    def load_unimportant_messages(self) -> str:
        if len(self.unimportant_messages) == 0:
            return ""
        messages = ""
        for text in self.unimportant_messages:
            messages = f"{messages}{text}\n"
        self.unimportant_messages = []
        return f"{messages}\n"

    def prompt(self, user_prompt: str):
        llm_response: str = self.llm.prompt(f"{self.load_unimportant_messages()}{user_prompt}")
        thoughts: str
        cleansed_response: str

        thoughts, cleansed_response = self.seperate_llm_response(llm_response)

        while cleansed_response.replace("\n", "").replace(" ", "") != "[]":
            data = json.loads(cleansed_response)

            if isinstance(data, dict):
                data = [data]

            prompt: str = ""
            for block in data:
                action = block.get("action")

                if action is None:
                    continue

                arguments: List[str] = block.get("args", [])

                result = self.preform_action(action, arguments)
                if result != "":
                    prompt = f"{prompt}{result}\n"

            if prompt == "":
                break

            llm_response = self.llm.prompt(f"{self.load_unimportant_messages()}{prompt}")
            thoughts, cleansed_response = self.seperate_llm_response(llm_response)




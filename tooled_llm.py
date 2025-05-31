from typing import List, TypedDict, Callable, Tuple
import re
import json

import chatapi

print("tooled_llm.py")

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


class ToolLLM:
    def __init__(self,
                 directions: str = "",
                 tool_objects: List[Toolwrapper] = None,
                 model: str = "gemini-2.0-flash",
                 action_prompt: str = ""):

        self.response_instructions = """
            OUTPUT FORMAT REQUIREMENTS:
            Your response MUST strictly follow this two-part structure:
            PART 1: THINKING PROCESS
            - You should NEVER have any brackets '[', ']' in your thoughts.
            - Begin your response with your step-by-step reasoning and plan.
            - Detail the inputs received, your interpretation, and the sequence of actions you intend to take and why.
            - Review the rules and guidelines associated with your actions and how you should follow them.
            - Include what actions you won't be taking, or why you will be waiting before calling a certain action.
            - End your thoughts with a clear plan of what you will be doing and why
            - Think for as long as you need to
            - Do not write any JSON in your thoughts
            - You should NEVER have any brackets '[', ']' in your thoughts.
            - You should NEVER have any brackets '[', ']' in your thoughts.
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

            You may not preform any actions on this turn. 
            Instructions are complete. Acknowledge your instructions and wait patiently.
        """

        self.llm = chatapi.FlashChat(initial_prompt, model=model)

        if action_prompt:
            self.prompt(action_prompt)

    def seperate_llm_response(self, text: str) -> (str, list):
        try:
            prematch = re.search(r'^(.*?)\[', text, re.DOTALL)
            thought = prematch.group(1) if prematch else ''

            postmatch = re.search(r'\[[\s\S]*\]', text)
            actions = postmatch.group(0) if postmatch else "[]"
            data = json.loads(actions)

            if not (isinstance(data, list) and all(isinstance(item, dict) for item in data)):
                #print("data is not the correct type, printing data: ")
                #print(data)

                if isinstance(data, list):
                    inner_types = [type(item).__name__ for item in data]
                    raise TypeError(f"Expected a list[dict], but got: list containing {inner_types}")
                else:
                    raise TypeError(f"Expected a list[dict] but got {type(data).__name__}")

            return thought, data
        except Exception as e:
            print(f"LLM message failed to parse. Asking them to send it again.")
            print(f"\n'{text}'")
            self.prompt(f"""
                Your last message failed to be parsed.  
                Error -> '{e}'
                Send it again according to the response instructions so that it can be parsed properly.
                You should not have any brackets '[', ']' in your thoughts.
                {self.response_instructions}
            """)
            return "", []

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
        print(f"ToolLLM.prompt called with user_prompt: {user_prompt}")

        # Load unimportant messages and combine with user prompt
        unimportant_messages = self.load_unimportant_messages()
        full_prompt = f"{unimportant_messages}{user_prompt}"
        print(f"Full prompt to LLM: {full_prompt}")

        # Get response from LLM
        llm_response: str = self.llm.prompt(full_prompt)
        print(f"LLM response received, length: {len(llm_response)}")

        thoughts: str
        data: list = None

        # Parse the response
        print("Parsing LLM response")
        thoughts, data = self.seperate_llm_response(llm_response)
        print(f"Parsed thoughts (first 100 chars): {thoughts[:100] if thoughts else 'None'}")
        print(f"Parsed data: {data}")

        # Process actions
        while len(data):
            print(f"Processing {len(data)} actions")

            if isinstance(data, dict):
                print("Converting dict to list")
                data = [data]

            prompt: str = ""
            for block_index, block in enumerate(data):
                print(f"Processing action block {block_index}: {block}")
                action = block.get("action")

                if action is None:
                    print(f"No action in block {block_index}, skipping")
                    continue

                arguments: List[str] = block.get("args", [])
                print(f"Action: {action}, Arguments: {arguments}")

                result = self.preform_action(action, arguments)
                print(f"Action result: {result}")

                if result != "":
                    prompt = f"{prompt}{result}\n"
                    print(f"Updated prompt: {prompt}")

            if prompt == "":
                print("No prompt generated, breaking loop")
                break

            print(f"Sending follow-up prompt to LLM: {prompt}")
            llm_response = self.llm.prompt(f"{self.load_unimportant_messages()}{prompt}")
            print(f"Follow-up LLM response received, length: {len(llm_response)}")

            thoughts, data = self.seperate_llm_response(llm_response)
            print(f"Follow-up parsed thoughts (first 100 chars): {thoughts[:100] if thoughts else 'None'}")
            print(f"Follow-up parsed data: {data}")

        print("ToolLLM.prompt completed")

#! python3

import sys
import os
import json
import shutil
import argparse

from openai import OpenAI  # requires install

# constants
FILE_PATH = os.path.expanduser("~/.chat")
MODELS = ["gpt-3.5-turbo", "gpt-4"]
VERSION = "2.2"

# defaults
model = 3
retain = 3
temperature = 1.0
instructions = ("If you are asked to complete a complex task, break the task into "
                "multiple steps and reason your way through each step. Otherwise, "
                "keep responses short and direct.")
messages = []


# simplifies the default help format
class CustomHelpFormatter(argparse.HelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        pass

    def _format_action_invocation(self, action):
        if action.option_strings:
            return ', '.join(action.option_strings)
        return super()._format_action_invocation(action)


# set up argument parser
parser = argparse.ArgumentParser(
    description="terminal ChatGPT interface", formatter_class=CustomHelpFormatter)
parser.add_argument("prompt", nargs="?",
                    help='text prompt, e.g., "Explain how pi is calculated."')
parser.add_argument("-v", "--version", action="version",
                    version=f'%(prog)s {VERSION}', help="show version number and exit")
parser.add_argument("-s", "--settings", action="store_true",
                    help="show current settings and exit")
parser.add_argument("-m", "--model", type=int,
                    choices=[3, 4], help="[3, 4] model selected")
parser.add_argument("-r", "--retain", type=int, choices=range(0, 10),
                    help="[0, 9] messages retained in conversation")
parser.add_argument("-t", "--temperature", type=float,
                    choices=[x / 10.0 for x in range(1, 20)], help="[0.1, 1.9] creativity")
parser.add_argument("-i", "--instructions", type=str,
                    help="instructions for model")

# parse command line arguments
args = parser.parse_args()

# accept piped in prompts
if not sys.stdin.isatty():
    args.prompt = sys.stdin.read()

# print examples if no arguments
if len(sys.argv) == 1 and args.prompt is None:
    print("chat --help\n")
    print("examples:")
    print('  chat "Explain how pi is calculated."')
    print('  chat "Explain the following code: $(cat index.js)"')
    print('  chat "$(cat << EOF \n\tExplain the difference between \' and " in javascript. \n\tEOF \n\t)"')
    sys.exit(0)


# stored messages must be either 'user' or 'assistant'
def check_messages(messages):
    for message in messages:
        assert (message["role"] in ["user", "assistant"])
        assert ("content" in message)
    return messages


# read settings and update defaults accordingly
try:
    with open(FILE_PATH, "r") as file:
        memory = json.load(file)
        model = int(memory["model"])
        retain = int(memory["retain"])
        temperature = float(memory["temperature"])
        instructions = memory["instructions"]
        messages = check_messages(memory["messages"])
except Exception as e:
    pass  # continue using defaults

# update defaults with arguments
if args.model is not None:
    model = args.model
model = model if 3 <= model <= 4 else 3

if args.retain is not None:
    retain = args.retain
retain = retain if 0 <= retain <= 9 else 3

if args.temperature is not None:
    temperature = args.temperature
temperature = temperature if 0.0 < temperature < 2.0 else 1.0

if args.instructions is not None:
    instructions = args.instructions

# print settings and exit
if args.settings:
    print("settings:")
    print(f"  model: {MODELS[model - 3]}")
    print(f"  retain: {retain}")
    print(f"  temperature: {temperature}")
    print(f'  instructions: "{instructions}"')
    sys.exit(0)

# make API call
if args.prompt is not None:
    messages = [] if retain == 0 else messages[retain * -2:]

    messages.insert(0, {"role": "system", "content": instructions})
    messages.append({"role": "user", "content": args.prompt})

    openai = OpenAI()
    completion = openai.chat.completions.create(
        model=MODELS[model - 3],
        temperature=temperature,
        messages=messages
    ).choices[0].message.content

    messages.append({"role": "assistant", "content": completion})

    assert (messages[0]["role"] == "system")
    messages.pop(0)  # Remove instructions

    terminal_width = shutil.get_terminal_size().columns

    print("*" * terminal_width)
    print(completion)
    print("*" * terminal_width)

# rewrite settings file
with open(FILE_PATH, "w") as file:
    messages = [] if retain == 0 else messages[retain * -2:]

    memory = {
        "model": model,
        "retain": retain,
        "temperature": temperature,
        "instructions": instructions,
        "messages": messages
    }

    json.dump(memory, file)

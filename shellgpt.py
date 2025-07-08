import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("query", nargs="+", help="Task or input string")
parser.add_argument("--mode", choices=PROMPT_TEMPLATES.keys(), default="shell", help="Task type")
args = parser.parse_args()

query = " ".join(args.query)


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

query = " ".join(sys.argv[1:])

PROMPT_TEMPLATES = {
    "shell": "You're a Linux shell expert. Given the task: \"{query}\", generate a safe, well-commented Bash command. Include an explanation.",
    "terraform": "You're a senior DevOps engineer writing Terraform. Task: \"{query}\". Write an idiomatic module or snippet. Use variables and outputs. Include a brief docstring or comments.",
    "gitlab": "You're an expert in GitLab CI/CD. Task: \"{query}\". Create or optimize a `.gitlab-ci.yml` job or pipeline. Explain stages, dependencies, and best practices.",
    "explain": "Explain what this snippet does and how it could be improved:\n\n{query}"
}

prompt = PROMPT_TEMPLATES[args.mode].format(query=query)

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.3
)

print(response.choices[0].message.content)


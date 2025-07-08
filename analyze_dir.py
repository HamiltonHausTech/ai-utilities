#!/usr/bin/env python3
import os, sys, argparse
from dotenv import load_dotenv
from openai import OpenAI
import tiktoken

# --- Config ---
EXTS = {
  "terraform": [".tf", ".tfvars"],
  "gitlab": [".yml", ".yaml", ".gitlab-ci.yml"],
  "shell": [".sh"],
  "python": [".py"]
}

PROMPTS = {
  "terraform": "You're a Terraform expert. Analyze this file: explain its purpose, risks, inefficiencies, anti-patterns, and suggest improvements.\n\nFile: {filename}\nContent:\n{content}",
  "gitlab": "You're a GitLab CI/CD expert. Analyze this pipeline file for structure, reliability, security, and suggest improvements.\n\nFile: {filename}\nContent:\n{content}",
  "shell": "You're a Linux shell expert. Analyze this script: explain its function, risks, inefficiencies, and suggestions.\n\nFile: {filename}\nContent:\n{content}",
  "python": "You're a Python code reviewer. Analyze this script: explain its functionality, potential bugs, style issues, and improvements.\n\nFile: {filename}\nContent:\n{content}"
}

# --- GPT client init ---
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

enc = tiktoken.encoding_for_model("gpt-4-turbo")
MAX_TOK = 3500

def chunk_content(text):
    tokens = enc.encode(text)
    chunks = []
    for i in range(0, len(tokens), MAX_TOK):
        chunk = enc.decode(tokens[i:i+MAX_TOK])
        chunks.append(chunk)
    return chunks

def analyze_file(path, mode):
    out = []
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    if not content.strip(): return None
    for chunk in chunk_content(content):
        prompt = PROMPTS[mode].format(filename=os.path.basename(path), content=chunk)
        resp = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        out.append(resp.choices[0].message.content.strip())
    return "\n\n".join(out)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--path", "-p", required=True, help="Directory to analyze")
    p.add_argument("--mode", choices=PROMPTS.keys(), required=True)
    p.add_argument("--output", "-o", help="Write Markdown summary here")
    args = p.parse_args()

    summaries = {}
    for root, _, files in os.walk(args.path):
        for fn in files:
            if any(fn.endswith(ext) for ext in EXTS[args.mode]):
                path = os.path.join(root, fn)
                sys.stdout.write(f"🕵️ Analyzing {path}...\n")
                summ = analyze_file(path, args.mode)
                if summ:
                    summaries[path] = summ

    # Directory-level summary
    agg = "\n\n".join(f"### {p}\n\n{txt}" for p, txt in summaries.items())
    top_prompt = f"You are a senior DevOps architect. Based on these file analyses, provide:\n1) high-level intent\n2) cross-file issues\n3) modularity/reuse suggestions\n4) docs/test/CI improvements\n\n{agg}"
    top_resp = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": top_prompt}],
        temperature=0.2
    ).choices[0].message.content.strip()

    report = "# Analysis Report\n\n" + top_resp
    if args.output:
        with open(args.output, "w") as f: f.write(report)
        print(f"✅ Written summary to {args.output}")
    else:
        print(report)

if __name__=="__main__":
    main()

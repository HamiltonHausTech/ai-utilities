#!/usr/bin/env python3
import argparse, os, subprocess, sys, yaml, json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def query_llm(prompt, provider="openai", model="gpt-4"):
    if provider == "openai":
        return client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        ).choices[0].message.content.strip()

    elif provider == "ollama":
        import subprocess
        cmd = ["ollama", "run", model]
        result = subprocess.run(cmd, input=prompt, text=True, capture_output=True)
        return result.stdout.strip()

    else:
        raise ValueError(f"Unsupported provider: {provider}")


def load_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def get_git_diff(base, head):
    cmd = ["git", "diff", f"{base}..{head}", "--", ".gitlab-ci.yml"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()

def run_prompt(yml_text, mode):
    prompts = {
        "summary": "You're a GitLab CI/CD expert. Summarize this `.gitlab-ci.yml` file: jobs, structure, relationships.\n\n",
        "critic": "You're a senior DevOps reviewer. Identify flaws, risks, or inefficiencies in this GitLab CI/CD pipeline. Suggest improvements.\n\n",
        "suggest": "You're an SRE lead. Suggest 2–3 improvements to this pipeline for performance, security, or maintainability.\n\n"
    }
    return query_llm(prompts[mode] + yml_text,provider,model)

def run_score(yml_text, output_format):
    score_prompt = (
        "Score this GitLab CI/CD pipeline (1–5 scale) on:\n"
        "- Structure\n- Reliability\n- Security\n- Maintainability\n"
        "Give reasons. Provide an overall score. If output format is JSON, return parsable JSON.\n\n"
        f"YAML:\n{yml_text}"
    )

    result = query_llm(score_prompt,provider,model)
    if output_format == "json":
        try:
            return json.loads(result)
        except:
            print("⚠️ GPT returned invalid JSON. Raw output:\n", result)
            sys.exit(1)
    return result

def main():
    parser = argparse.ArgumentParser(description="LLM-based GitLab CI/CD linter")
    parser.add_argument("--file", help=".gitlab-ci.yml to analyze")
    parser.add_argument("--diff", nargs=2, metavar=("BASE", "HEAD"), help="Compare pipeline changes between two commits")
    parser.add_argument("--mode", choices=["summary", "critic", "suggest"], default="critic")
    parser.add_argument("--score", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--min-score", type=float, default=0)
    parser.add_argument("--output", help="Write result to file")
    parser.add_argument("--output-format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--provider", choices=["openai", "ollama"], default="openai")
    parser.add_argument("--model", help="Model name (e.g., gpt-4, llama3:instruct)", default="gpt-4")


    args = parser.parse_args()

    if args.diff:
        diff_output = get_git_diff(args.diff[0], args.diff[1])
        if not diff_output:
            print("✅ No changes to .gitlab-ci.yml detected.")
            return
        yml = diff_output
    elif args.file:
        yml = load_file(args.file)
    else:
        print("❌ Must specify --file or --diff.")
        return

    result = run_prompt(yml, args.mode)

    if args.score:
        score = run_score(yml, args.output_format)
        if args.strict and args.output_format == "json":
            overall = score.get("overall_score", 0)
            if overall < args.min_score:
                print(f"❌ Score {overall} < minimum {args.min_score}")
                sys.exit(1)

        result += "\n\n---\n\n" + (json.dumps(score, indent=2) if args.output_format == "json" else score)

    if args.output:
        with open(args.output, "w") as f:
            f.write(result)
        print(f"✅ Written to {args.output}")
    else:
        print("\n" + result + "\n")

if __name__ == "__main__":
    main()

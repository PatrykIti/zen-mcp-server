# Zen MCP: Many Workflows. One Context.

[zen_web.webm](https://github.com/user-attachments/assets/851e3911-7f06-47c0-a4ab-a2601236697c)

<div align="center">
  <b>🤖 <a href="https://www.anthropic.com/claude-code">Claude Code</a> OR <a href="https://github.com/google-gemini/gemini-cli">Gemini CLI</a> + [Gemini / OpenAI / Grok / OpenRouter / DIAL / Ollama / Anthropic / Any Model] = Your Ultimate AI Development Team</b>
</div>

<br/>

**AI orchestration for Claude Code** - A Model Context Protocol server that gives your CLI of choice (e.g. [Claude Code](https://www.anthropic.com/claude-code)) access to multiple AI models for enhanced code analysis, problem-solving, and collaborative development.

**True AI collaboration with conversation continuity** - Claude stays in control but gets perspectives from the best AI for each subtask. Context carries forward seamlessly across tools and models, enabling complex workflows like: code reviews with multiple models → automated planning → implementation → pre-commit validation.

> **You're in control.** Claude orchestrates the AI team, but you decide the workflow. Craft powerful prompts that bring in Gemini Pro, GPT 5, Flash, or local offline models exactly when needed.

#### Recommended AI Stack

Use Claude Code with **Opus 4.1** (for all the agentic work) + **Gemini 2.5 Pro** (for deeper thinking, reviews, helping debug, perform pre-commit analysis, general discussion) and achieve outstanding results.

## Quick Start (5 minutes)

**Prerequisites:** Python 3.10+, Git, [uv installed](https://docs.astral.sh/uv/getting-started/installation/)

**1. Get API Keys** (choose one or more):
- **[OpenRouter](https://openrouter.ai/)** - Access multiple models with one API
- **[Gemini](https://makersuite.google.com/app/apikey)** - Google's latest models
- **[OpenAI](https://platform.openai.com/api-keys)** - O3, GPT-5 series
- **[X.AI](https://console.x.ai/)** - Grok models
- **[DIAL](https://dialx.ai/)** - Vendor-agnostic model access
- **[Ollama](https://ollama.ai/)** - Local models (free)

**2. Install** (choose one):

**Option A: Instant Setup with uvx** (recommended)
```json
// Add to ~/.claude/settings.json or .mcp.json
{
  "mcpServers": {
    "zen": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/BeehiveInnovations/zen-mcp-server.git", "zen-mcp-server"],
      "env": {
        "PATH": "/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin:~/.local/bin",
        "GEMINI_API_KEY": "your-key-here"
      }
    }
  }
}
```

**Option B: Clone and Setup**
```bash
git clone https://github.com/BeehiveInnovations/zen-mcp-server.git
cd zen-mcp-server
./run-server.sh  # Handles everything: setup, config, API keys
```

**3. Start Using!**
```
"Use zen to analyze this code for security issues with gemini pro"
"Debug this error with o3 and then get flash to suggest optimizations"
"Plan the migration strategy with zen, get consensus from multiple models"
```

👉 **[Complete Setup Guide](docs/getting-started.md)** with detailed installation, configuration, and troubleshooting

## Core Tools

**Collaboration & Planning**
- **[`chat`](docs/tools/chat.md)** - Brainstorm ideas, get second opinions, validate approaches
- **[`thinkdeep`](docs/tools/thinkdeep.md)** - Extended reasoning, edge case analysis, alternative perspectives
- **[`planner`](docs/tools/planner.md)** - Break down complex projects into structured, actionable plans
- **[`consensus`](docs/tools/consensus.md)** - Get expert opinions from multiple AI models with stance steering

**Code Analysis & Quality**
- **[`analyze`](docs/tools/analyze.md)** - Understand architecture, patterns, dependencies across entire codebases
- **[`codereview`](docs/tools/codereview.md)** - Professional reviews with severity levels and actionable feedback
- **[`debug`](docs/tools/debug.md)** - Systematic investigation and root cause analysis
- **[`precommit`](docs/tools/precommit.md)** - Validate changes before committing, prevent regressions

**Development Tools**
- **[`refactor`](docs/tools/refactor.md)** - Intelligent code refactoring with decomposition focus
- **[`testgen`](docs/tools/testgen.md)** - Comprehensive test generation with edge cases
- **[`secaudit`](docs/tools/secaudit.md)** - Security audits with OWASP Top 10 analysis
- **[`docgen`](docs/tools/docgen.md)** - Generate documentation with complexity analysis

**Utilities**
- **[`challenge`](docs/tools/challenge.md)** - Prevent "You're absolutely right!" responses with critical analysis
- **[`tracer`](docs/tools/tracer.md)** - Static analysis prompts for call-flow mapping

👉 **[Complete Tools Reference](docs/tools/)** with examples, parameters, and workflows

## Key Features

**AI Orchestration**
- **Auto model selection** - Claude picks the right AI for each task
- **Multi-model workflows** - Chain different models in single conversations
- **Conversation continuity** - Context preserved across tools and models
- **[Context revival](docs/context-revival.md)** - Continue conversations even after context resets

**Model Support**
- **Multiple providers** - Gemini, OpenAI, X.AI, OpenRouter, DIAL, Ollama
- **Latest models** - GPT-5, Gemini 2.5 Pro, O3, Grok-4, local Llama
- **[Thinking modes](docs/advanced-usage.md#thinking-modes)** - Control reasoning depth vs cost
- **Vision support** - Analyze images, diagrams, screenshots

**Developer Experience**
- **Guided workflows** - Systematic investigation prevents rushed analysis
- **Smart file handling** - Auto-expand directories, manage token limits
- **Web search integration** - Access current documentation and best practices
- **[Large prompt support](docs/advanced-usage.md#working-with-large-prompts)** - Bypass MCP's 25K token limit

## Example Workflows

**Multi-model Code Review:**
```
"Perform a codereview using gemini pro and o3, then use planner to create a fix strategy"
```
→ Claude reviews code systematically → Consults Gemini Pro → Gets O3's perspective → Creates unified action plan

**Collaborative Debugging:**
```
"Debug this race condition with max thinking mode, then validate the fix with precommit"
```
→ Deep investigation → Expert analysis → Solution implementation → Pre-commit validation

**Architecture Planning:**
```
"Plan our microservices migration, get consensus from pro and o3 on the approach"
```
→ Structured planning → Multiple expert opinions → Consensus building → Implementation roadmap

👉 **[Advanced Usage Guide](docs/advanced-usage.md)** for complex workflows, model configuration, and power-user features

## Why Zen MCP?

**Problem:** Claude is brilliant but sometimes needs:
- Multiple AI perspectives for complex decisions
- Systematic workflows to prevent rushed analysis
- Extended context beyond its limits
- Access to specialized models (reasoning, speed, local)

**Solution:** Zen orchestrates AI models as Claude's development team:
- **Claude stays in control** - You give instructions to Claude
- **Models provide expertise** - Each AI contributes their strengths
- **Context flows seamlessly** - Full conversation history across tools
- **You decide the workflow** - Simple requests or complex orchestration

## Quick Links

**📖 Documentation**
- [Getting Started](docs/getting-started.md) - Complete setup guide
- [Tools Reference](docs/tools/) - All tools with examples
- [Advanced Usage](docs/advanced-usage.md) - Power user features
- [Configuration](docs/configuration.md) - Environment variables, restrictions

**🔧 Setup & Support**
- [WSL Setup](docs/wsl-setup.md) - Windows users
- [Troubleshooting](docs/troubleshooting.md) - Common issues
- [Contributing](docs/contributions.md) - Code standards, PR process

## License

Apache 2.0 License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

Built with the power of **Multi-Model AI** collaboration 🤝
- **A**ctual **I**ntelligence by real Humans
- [MCP (Model Context Protocol)](https://modelcontextprotocol.com) by Anthropic
- [Claude Code](https://claude.ai/code) - Your AI coding orchestrator
- [Gemini 2.5 Pro & Flash](https://ai.google.dev/) - Extended thinking & fast analysis
- [OpenAI O3 & GPT-5](https://openai.com/) - Strong reasoning & latest capabilities

### Star History

[![Star History Chart](https://api.star-history.com/svg?repos=BeehiveInnovations/zen-mcp-server&type=Date)](https://www.star-history.com/#BeehiveInnovations/zen-mcp-server&Date)

## Docker Image Usage (Fork Enhancement)

This fork maintains Docker support with pre-built images available at GitHub Container Registry.

### Quick Start with Docker

**Basic Configuration (Gemini only):**
```json
{
  "mcpServers": {
    "zen": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "GEMINI_API_KEY=<your_api_key_from_google_ai_studio>",
        "-v", "<path_to_your_workspace>:<path_to_your_workspace>",
        "ghcr.io/patrykiti/zen-mcp-server:latest"
      ]
    }
  }
}
```

**Full Configuration (All Providers):**
```json
{
  "mcpServers": {
    "zen": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "GEMINI_API_KEY=<your-gemini-key>",
        "-e", "OPENAI_API_KEY=<your-openai-key>",
        "-e", "XAI_API_KEY=<your-xai-key>",
        "-e", "OPENROUTER_API_KEY=<your-openrouter-key>",
        "-e", "CUSTOM_API_URL=http://host.docker.internal:11434/v1",
        "-e", "CUSTOM_API_KEY=",
        "-e", "CUSTOM_MODEL_NAME=llama3.2",
        "-e", "DEFAULT_MODEL=auto",
        "-e", "OPENAI_ALLOWED_MODELS=o3-mini,o4-mini",
        "-e", "GOOGLE_ALLOWED_MODELS=flash,pro",
        "-e", "XAI_ALLOWED_MODELS=grok,grok-3-fast",
        "-e", "OPENROUTER_ALLOWED_MODELS=opus,sonnet,mistral",
        "-e", "OPENROUTER_REFERER=https://your-app.com",
        "-e", "OPENROUTER_TITLE=Your App Name",
        "-e", "CUSTOM_MODELS_CONFIG_PATH=/path/to/custom_models.json",
        "-e", "DEFAULT_THINKING_MODE_THINKDEEP=high",
        "-e", "CONVERSATION_TIMEOUT_HOURS=5",
        "-e", "MAX_CONVERSATION_TURNS=20",
        "-e", "LOG_LEVEL=INFO",
        "-v", "<path_to_your_workspace>:<path_to_your_workspace>",
        "ghcr.io/patrykiti/zen-mcp-server:latest"
      ]
    }
  }
}
```

**Note:** Replace `<path_to_your_workspace>` with the directory where your projects are located.

### Using Docker Compose

```bash
git clone https://github.com/PatrykIti/zen-mcp-server.git
cd zen-mcp-server
cp .env.example .env
nano .env
docker-compose up -d
```

### Available Tags
- `ghcr.io/patrykiti/zen-mcp-server:latest` - Always the newest version
- `ghcr.io/patrykiti/zen-mcp-server:v5.2.4` - Specific version

For more details, see the [Docker setup guide](docker-compose.yml) in this repository.

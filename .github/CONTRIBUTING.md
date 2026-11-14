# Contributing

Thank you for your interest in contributing to Project Athena!

## ⚠️ Quality Bar (Read Before Contributing)

We maintain a high quality bar. PRs that meet **any** of the following criteria will be **closed without review**:

- **Generic/project-unrelated content** — e.g. "code optimization guides," "best practices checklists," or boilerplate docs that could apply to any repo
- **AI-generated filler** — bulk-generated content with no project-specific substance
- **No linked issue** — all PRs must reference an open issue or a clear gap in the project
- **Untested changes** — if you can't demonstrate it works, don't submit it
- **Drive-by contributions** — contributors with no prior engagement (issues, discussions, or meaningful context) submitting unsolicited docs or refactors

**The rule is simple**: if your PR doesn't make Athena specifically better, it doesn't belong here.

## Before You Open an Issue

> **Ask Athena first.** That's what it's built for.

Most questions, troubleshooting, and "how do I..." queries can be answered by your own Athena agent. Try asking it directly:

- *"How do I get a Gemini API key?"*
- *"How do I write a protocol?"*
- *"How do I set up Supabase?"*
- *"I'm getting [error]. Can you help me fix it?"*

If Athena can't answer, *then* open an issue. See [SUPPORT.md](SUPPORT.md) for the full self-service flow.

## How to Contribute

### 1. Submit a PR (Preferred)

Don't just report it — **fix it**. We actively welcome pull requests:

1. Fork the repo
2. Let your Athena agent help you implement the change
3. Test your changes locally
4. Submit a PR with a clear description of what and why

We'll review and merge if it fits the project direction.

### 2. Share Your Workflows

Built a useful workflow? Submit a PR with:

- Your workflow file in `examples/workflows/`
- A brief description of what it does

### 3. Improve Documentation

Found something unclear? Help make it better:

- Fix typos or clarify explanations
- Add examples where helpful

### 4. Add Templates

Created a useful template? Share it:

- Add to `examples/templates/`
- Include usage instructions

### 5. Agent-Assisted Contributions

Let your Athena agent help you contribute! Using [Protocol 408](../examples/protocols/workflow/WFL-408-autonomous-contribution-engine.md):

1. **Ask a question**: "Does Athena support X?"
2. **Agent verifies**: Searches codebase to confirm it's a gap
3. **Agent drafts**: Creates a structured RFC using templates
4. **You submit**: One-click GitHub Issue submission

Use the [Agent-Assisted Contribution](ISSUE_TEMPLATE/agent_contribution.md) issue template for submissions.

## Guidelines

- Keep files modular (< 500 lines)
- Use clear, descriptive names
- Include comments where helpful
- Test your changes before submitting
- One PR = one topic (don't bundle unrelated changes)

## Code of Conduct

Be respectful. Be helpful. We're all learning together.

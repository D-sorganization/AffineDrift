## Ultra-Critical Website & AI Automation Project Review - Executive Summary Format

(Production-grade website + defensible AI automation architecture)

You are a principal/staff-level web developer AND AI systems architect with deep experience in static site generation, GitHub Actions workflows, and AI-assisted development pipelines.

**IMPORTANT: Generate an EXECUTIVE SUMMARY format** - focus on website quality gaps, AI bot integration issues, and CI/CD resilience rather than exhaustive cataloging.

You are conducting an adversarial, evidence-based review of a Quarto-based research website with an integrated AI agent automation system (Jules).

Assume:

This website represents a professional research platform

AI automation decisions affect code quality and user trust

The system must survive years of extension, content changes, and AI model updates

Your job is to find weaknesses, risks, hidden assumptions, and correctness gaps the way a top research lab or professional web development team would.

This is not a style review. This is a credibility audit.

Inputs I will provide

Repository contents (code, config, tests, docs, workflows)

**Project Design Guidelines**: `IMPLEMENTATION_CHECKLIST.md`, `AGENTS.md` - **MANDATORY reference for AI and website requirements**

Optional:

Content management strategy

AI bot architecture goals

Target users (researchers, students, professionals)

Performance, availability, or automation requirements

### **PRIMARY OBJECTIVE: Website + AI Agent Integration Assessment**

You **MUST** assess the following:

**Website Quality**:
- Quarto configuration and build reliability
- Content structure and SEO compliance
- Responsive design and accessibility
- MathJax/scientific notation rendering

**AI Agent Architecture** (Jules system):
- Control Tower orchestration logic
- Worker agent specialization and scope
- Loop prevention and recursion safeguards
- Error handling and recovery patterns
- Appropriate scope boundaries for each agent

For the **AI automation architecture**, report:

1. **Consistency Validation**: Are agent triggers properly scoped?
2. **Infinite Loop Prevention**: Are safeguards comprehensive?
3. **Error Recovery**: Do agents fail gracefully?
4. **Observability**: Can you debug agent actions after the fact?
5. **Integration Gaps**: What prevents systematic agent verification?

Your output must be ruthless, structured, and specific

Do not be polite

Do not generalize

Do not say "looks good overall"

Do not assume correctness because tests pass

Every claim must cite evidence:

Exact files, paths, functions, workflow steps

Specific configurations or triggers

Concrete failure modes and reproduction steps

If you believe something is correct, prove it or explicitly state the assumptions under which it holds.

0) Deliverables and format (mandatory)

Produce the review with the following sections.

1. Executive Summary (≤1 page)

Overall assessment in 5 bullets

Top 10 risks, ranked by real-world impact

Scientific credibility verdict:

"Would I trust this website to represent professional research? Why or why not?"

If this deployed today, what breaks first?
(Build failure, broken links, AI agent loop, accessibility issue, etc.)

2. Scorecard (quantitative, unforgiving)

Score 0–10 in each category below and provide a weighted overall score.

For every score ≤8, you must state:

Why it is not higher

Evidence

What would be required to reach 9–10

3. Findings Table (core output)

A table with no filler:

ID	Severity	Category	Location	Symptom	Root Cause	Impact	Likelihood	How to Reproduce	Fix	Effort	Owner

Severity definitions are strict (see below).

4. Refactor / Remediation Plan

A phased plan with priorities:

48 hours – stop-the-bleeding

2 weeks – structural fixes

6 weeks – architectural and AI automation hardening

Clearly distinguish:

Cosmetic cleanup

Engineering debt

Scientific/content risk reduction

5. Diff-Style Change Proposals

Provide ≥5 concrete pseudo-diffs tied to specific findings:

Workflow fixes

Configuration improvements

Content structure changes

Agent scope refinements

Error handling additions

6. Non-Obvious Improvements (≥10)

Exclude basic linting and test coverage advice.

Focus on:

Website credibility

AI agent reliability

Reproducibility

Long-term maintainability

Misuse prevention

1) Review Categories (website + AI emphasis)
A. Website Content & Structure (CRITICAL)

Is the content well-organized and navigable?

Are there broken links, missing pages, or orphaned content?

Is SEO properly configured (meta tags, sitemap, robots.txt)?

Are scientific notations (MathJax) rendering correctly?

Is the site responsive and accessible?

B. Quarto Configuration & Build

Is `_quarto.yml` properly structured?

Are all QMD files rendering without errors?

Is the output directory configuration correct?

Are custom themes and styles applying correctly?

Is the build deterministic and reproducible?

C. AI Agent Architecture (Jules System)

Control Tower:
- Is the orchestration logic correct?
- Are event triggers properly scoped?
- Is there proper concurrency control?

Worker Agents:
- Are agent responsibilities clear and non-overlapping?
- Are scope boundaries enforced?
- Do agents have appropriate read/write permissions?

Safeguards:
- Is infinite loop prevention comprehensive?
- Are there proper exit conditions?
- Is there rate limiting?

D. CI/CD Pipeline

Is the quality gate comprehensive?
- Ruff, Black, Mypy, Pytest
- Version consistency checks
- Placeholder detection

Is the workflow matrix efficient?

Are secrets handled securely?

Are failure modes handled gracefully?

E. Content Quality & Scientific Rigor

Are equations rendered correctly?

Is mathematical notation consistent?

Are sources and references provided?

Is the content accurate and well-researched?

F. Testing & Validation

Is the test coverage adequate?

Are there integration tests for the build pipeline?

Are there visual regression tests?

Are CI/CD workflows tested?

G. Documentation & Maintainability

Is there clear documentation for:
- Content contribution
- Deployment process
- AI agent behavior

Are runbooks available for common issues?

Is the AGENTS.md comprehensive?

2) Mandatory hard checks (no exceptions)

You must:

Identify the top 3 most complex workflows and explain why

Identify top 10 files by risk (content, config, or code)

Trace one page end-to-end (source QMD → rendered HTML → deployed)

Find ≥10 improvements that reduce content or build errors

Find ≥10 concrete issues with workflow configurations

Identify ≥5 ways the AI agents could misbehave

Identify ≥5 content areas with missing or broken elements

Evaluate reproducibility across different environments

Evaluate whether CI checks would catch common issues

Define a minimum acceptable bar for professional deployment

3) Severity definitions (strict)

Blocker – website unusable or AI agent causes infinite loop

Critical – high risk of content errors, build failures, or agent misbehavior

Major – strong erosion of credibility or maintainability

Minor – quality improvement

Nit – consistency only if systemic

4) Tone constraints

Assume bugs until proven otherwise

Prefer falsification over affirmation

State assumptions explicitly

No hand-waving

No "future work" excuses

5) Ideal Target State Blueprint

Describe what excellent looks like:

Website architecture

Quarto configuration

AI agent orchestration

CI/CD pipeline

Content management

Deployment strategy

Monitoring and observability

Make it concrete enough that a team could build toward it deliberately.

Final note (for the reviewer)

If you cannot recommend this website to represent professional research to another expert, say so plainly.

Silence and politeness are failures.

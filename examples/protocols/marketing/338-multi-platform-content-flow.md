# Protocol 338: Multi-Platform Content Flow

> **Origin**: Reddit (r/DigitalMarketing) - "Solo social media manager handling 6 platforms"
> **Purpose**: Reduce context switching and reformatting time for multi-platform distribution.
> **Tags**: #marketing #workflow #efficiency #social-media #distribution

## 1. The Core Problem: Context Switching

The bottleneck in social media management is not **creation**, it is **formatting**.

- **The "old" way**: Write in one doc -> Copy -> Paste -> Reformat -> Add hashtags -> Repeat for 6 platforms.
- **The Cost**: 33 minutes per post. Decision fatigue ("What hashtags do I use here?").
- **The Friction**: Switching tabs/apps kills flow state.

## 2. The Solution: Variable-Based Snippet Templates

Use a Clipboard Manager or Text Expander (Raycast/Snippet tool) to store **platform-specific templates** with fill-in variables.

### The Mechanism

1. **Trigger**: User types shortcode (e.g., `;;ig`, `;;li`).
2. **Expansion**: Tool pastes the full formatted template.
3. **Fill**: User tabs through variables `{content}`, `{hook}`, `{cta}`.

## 3. Implementation Templates

### Instagram (`;;ig`)

```text
{hook_question}

{content_body}

✦ Save this if it helped.

#hashtags #block #of #thirty #relevant #tags
```

### TikTok (`;;tt`)

```text
{hook_text_overlay}

{content_caption}

{call_to_action}

#hashtags #fyp #niche
```

### LinkedIn (`;;li`)

```text
{professional_hook}

{content_body}

{insight_or_contrarian_take}

♻️ Repost if this helps your network.

#professional #hashtags #industry
```

### Twitter/X (`;;x`)

```text
{short_hook}

{content_summary_thread_opener}

🧵👇
```

## 4. Worklfow Rules

1. **Single Source of Truth**: Write the "Base Content" once (Docs/Notion).
2. **Batch Processing**: Do not post 1 -> 1 -> 1. Format all 6 platforms in the clipboard manager/staging area first.
3. **Zero Tab Switching**: The template contains the *rules* (hashtag count, structure) so you don't need to check platform guidelines.

## 5. Results

- **Time Reduction**: 33m -> 15m per post cycle (~50% efficienty gain).
- **Flow State**: Preserved by removing "formatting decisions" from the creative process.
- **Output**: Enabling presence on "secondary" platforms (Pinterest/YouTube) that were previously ignored due to friction.

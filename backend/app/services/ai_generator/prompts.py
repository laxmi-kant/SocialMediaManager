"""Prompt templates for AI content generation."""

SYSTEM_PROMPT = """You are a social media content creator. Generate engaging posts optimized for the target platform.
Follow these rules:
- Never include placeholder text or brackets
- Output ONLY the post text, no explanations
- Include relevant hashtags at the end (2-5 hashtags)
- Match the requested tone exactly"""

TEMPLATES = {
    "twitter": {
        "tech_insight": """Write a tweet (max 270 chars including hashtags) sharing a key insight from this article.
Tone: {tone}

Title: {title}
URL: {url}
Summary: {content}""",
        "joke": """Write a funny tweet (max 270 chars) based on this joke, adapted for a tech audience.
Tone: {tone}

Joke: {content}""",
        "news_commentary": """Write a tweet (max 270 chars) with a brief hot take on this news.
Tone: {tone}

Title: {title}
URL: {url}
Summary: {content}""",
        "github_spotlight": """Write a tweet (max 270 chars) spotlighting this trending GitHub repo.
Tone: {tone}

Repo: {title}
Description: {content}
Stars: {score}
URL: {url}""",
        "tip": """Write a tweet (max 270 chars) sharing a practical tip inspired by this content.
Tone: {tone}

Title: {title}
Content: {content}""",
    },
    "linkedin": {
        "tech_insight": """Write a LinkedIn post (150-300 words) sharing insights from this article. Use short paragraphs and a hook opening.
Tone: {tone}

Title: {title}
URL: {url}
Summary: {content}""",
        "joke": """Write a short LinkedIn post (50-100 words) sharing a light-hearted tech joke. Keep it professional but fun.
Tone: {tone}

Joke: {content}""",
        "news_commentary": """Write a LinkedIn post (150-300 words) with your analysis of this news. Include a question to drive engagement.
Tone: {tone}

Title: {title}
URL: {url}
Summary: {content}""",
        "github_spotlight": """Write a LinkedIn post (100-200 words) highlighting this trending open-source project.
Tone: {tone}

Repo: {title}
Description: {content}
Stars: {score}
URL: {url}""",
        "tip": """Write a LinkedIn post (100-200 words) sharing a practical tip inspired by this content.
Tone: {tone}

Title: {title}
Content: {content}""",
    },
}


def get_prompt(
    platform: str,
    content_type: str,
    title: str = "",
    url: str = "",
    content: str = "",
    score: int = 0,
    tone: str = "professional",
) -> str:
    """Build a prompt from templates."""
    template = TEMPLATES.get(platform, {}).get(content_type)
    if not template:
        raise ValueError(f"No template for {platform}/{content_type}")

    return template.format(
        title=title or "N/A",
        url=url or "N/A",
        content=content or "N/A",
        score=score,
        tone=tone,
    )

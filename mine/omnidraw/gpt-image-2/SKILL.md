---
name: gpt-image-2
description: Image generation via OpenAI GPT-Image-2 / DALL-E 3 API. Illustrations, concept art, photo-realistic images, logos, icons. Covers prompt structure, parameters (size/quality/style), cost estimation, and error handling. Requires OPENAI_API_KEY.
---

# GPT-Image-2 / DALL-E 3

Generate images via OpenAI's image generation API. Requires an OpenAI API key.

## Setup

```bash
export OPENAI_API_KEY="sk-..."
```

## API

**Endpoint**: `POST https://api.openai.com/v1/images/generations`

```json
{
    "model": "dall-e-3",
    "prompt": "A watercolor fox reading under a tree, soft lighting, storybook style",
    "n": 1,
    "size": "1024x1024",
    "quality": "standard",
    "style": "vivid"
}
```

### Parameters

| Parameter | Values | Notes |
|-----------|--------|-------|
| `model` | `dall-e-3`, `dall-e-2` | DALL-E 3 recommended |
| `prompt` | max 4000 chars | Detailed prompts yield better results |
| `n` | 1 (DALL-E 3), 1-10 (DALL-E 2) | DALL-E 3 only n=1 |
| `size` | `1024x1024`, `1792x1024`, `1024x1792` | DALL-E 3 only |
| `quality` | `standard`, `hd` | `hd` = 2x cost, better detail |
| `style` | `vivid`, `natural` | `vivid` = dramatic; `natural` = subdued |
| `response_format` | `url`, `b64_json` | URL expires in 1 hour |

## When to Use

- Illustrations and concept art
- Photo-realistic images from text
- Logo and icon generation
- Visual concept exploration
- Storyboarding and mood boards
- When detailed prompt following matters (DALL-E 3 excels)

**Not for**: precise diagrams (use [mermaid](../mermaid/SKILL.md)), text-heavy output, specific fonts. For faster/cheaper: [nano-banana](../nano-banana/SKILL.md).

## Cost

| Model | Quality | Size | Cost |
|-------|---------|------|------|
| DALL-E 3 | standard | 1024×1024 | $0.040 |
| DALL-E 3 | standard | 1792×1024 / 1024×1792 | $0.080 |
| DALL-E 3 | hd | 1024×1024 | $0.080 |
| DALL-E 3 | hd | 1792×1024 / 1024×1792 | $0.120 |

## Prompt Structure

```
[Subject] + [Style/Medium] + [Composition] + [Lighting] + [Color palette] + [Mood]
```

### Style Keywords

| Category | Keywords |
|----------|----------|
| Medium | oil painting, watercolor, digital art, 3D render, pencil sketch, vector illustration, pixel art |
| Photo | cinematic, portrait, macro, wide-angle, studio lighting, golden hour |
| Art style | cyberpunk, minimalist, baroque, vaporware, ukiyo-e, art deco, neo-brutalist |
| Mood | serene, dramatic, mysterious, playful, melancholic, epic, cozy |
| Color | pastel, vibrant, monochromatic, muted, neon, earth tones, jewel tones |

### Good vs Bad
- **Bad**: "Draw a cat"
- **Good**: "A fluffy orange tabby sitting on a windowsill, rain on glass, warm lamp light, cozy melancholic mood, soft focus, cinematic composition"

## Templates by Category

### Illustration
```
A [medium] of [subject], [composition], [lighting], [color scheme], [mood]. [Style reference]. No text.
```

### Concept Art
```
Concept art: [subject], [setting/environment], [time of day], [atmosphere], [key visual features], wide establishing shot, digital painting, cinematic lighting, 1792x1024.
```

### Photo-Realistic
```
Photorealistic: [subject], [environment/context], [lighting setup], [camera/lens], [depth of field], professional photography, sharp focus, 8k detail.
```

### Logo / Icon
```
Logo design for [brand]: [key symbol], [style — minimalist/geometric/vintage], [color palette], clean vector style, white background. Professional brand identity quality. No text.
```

### Background / Abstract
```
Abstract [style] wallpaper: [color palette], [mood], minimal composition with space, digital art, 1792x1024, 8k.
```

## Limitations

- No accurate text rendering in images
- No precise layout control (can't specify pixel positions)
- URL expires in 1 hour — download promptly
- Content policy blocks NSFW, violence, public figures, copyrighted styles
- DALL-E 3: single image per request (n=1)

## Error Handling

| Status | Meaning | Action |
|--------|---------|--------|
| 401 | Invalid API key | Check `OPENAI_API_KEY` |
| 429 | Rate limited | Wait and retry with backoff |
| 400 | Content policy | Revise prompt, remove blocked terms |
| 500 | Server error | Retry after 30s |

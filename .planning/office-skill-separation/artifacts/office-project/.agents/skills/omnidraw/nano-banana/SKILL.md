---
name: nano-banana
description: Image generation via fal-ai MCP using Nano Banana Pro v1 and v2 models. Photo-realistic images, concept art, illustrations. Covers model selection (v1 vs v2), parameters (aspect ratio, inference steps, guidance scale), prompt techniques via globally configured fal-ai MCP server.
---

# Nano Banana Pro (v1 & v2)

Image generation via fal-ai MCP server using Nano Banana Pro models. Zero additional setup — fal-ai MCP is already globally configured.

## Dependencies

- **fal-ai MCP server**: globally configured in `~/.claude/mcp-configs/mcp-servers.json`

## Model Selection

| Model | fal-ai ID | Best For |
|-------|-----------|----------|
| Nano Banana Pro v1 | `fal-ai/nano-banana-pro` | Fast iterations, concept drafts |
| Nano Banana Pro v2 | `fal-ai/nano-banana-pro-v2` | High quality, final deliverables |

**v1 vs v2**:
- **v2**: Higher quality, better prompt adherence, more detailed. Use for finals.
- **v1**: Faster (2-5s), cheaper. Use for exploration and iteration.

## Parameters

| Parameter | Values | Recommended |
|-----------|--------|-------------|
| `model` | v1 or v2 ID | v2 for quality, v1 for speed |
| `aspect_ratio` | `1:1`, `16:9`, `9:16`, `4:3`, `3:4` | Match output destination |
| `num_inference_steps` | 20-50 | 28-36 (v2), 20-28 (v1) |
| `guidance_scale` | 1-20 | 7-9 |
| `num_images` | 1-4 | 1 for final, 2-4 for variants |

### Aspect Ratio Guide

| Ratio | Use Case |
|-------|----------|
| `1:1` | Social media, avatars |
| `16:9` | Presentation slides, hero images |
| `9:16` | Mobile, portrait compositions |
| `4:3` | Traditional photos |
| `3:4` | Book covers, portrait photos |

## Prompt Structure

### v2 (Detailed)
```
[Subject], [appearance details], [environment/context], [lighting type + direction], [color palette], [mood]. Highly detailed, sharp focus, professional composition, 8k.
```

### v1 (Concise)
```
[Subject], [style], [2-3 key details], [lighting mood]. High quality.
```

### Quality Boosters (v2)
- "highly detailed, sharp focus"
- "professional lighting, 8k resolution"
- "cinematic composition, depth of field"
- "masterpiece, best quality"

### Negative Prompt Elements
- "blurry, low quality, distorted"
- "text, watermark, signature, logo"
- "ugly, deformed, extra limbs, bad anatomy"

## Use Cases

### When to Use
- Photo-realistic images and scenes
- Quick concept art and illustrations
- Fast, cost-effective image generation
- Direct MCP integration in Claude Code

### When NOT to Use
- Precise diagrams → [mermaid](../mermaid/SKILL.md)
- Detailed prompt following required → [gpt-image-2](../gpt-image-2/SKILL.md)
- Text in images → not reliable with any image gen tool

## Workflow

### Exploration Phase (v1)
1. Start with v1 for quick iterations
2. Test 2-3 prompt variations
3. Adjust composition and style keywords

### Finalization Phase (v2)
1. Switch to v2 with best prompt
2. Increase inference steps (28-36)
3. Generate multiple variants, pick best

## Templates

### Photo-Realistic
```
[Subject], [environment], [lighting], [mood]. Photorealistic, [lens type], professional photography, sharp focus, 8k.
```

### Interior / Architecture
```
[Space description], [style], [key elements], [lighting], [time of day]. Architectural visualization, wide angle, photorealistic render.
```

### Nature / Landscape
```
[Landscape description], [season/weather], [time of day], [lighting quality]. National Geographic quality, breathtaking detail, wide panoramic.
```

### Portrait
```
[Person description], [pose/expression], [clothing], [setting], [lighting]. Professional portrait, [lens], sharp focus on eyes.
```

### Product
```
[Product], [material], [background], [lighting]. Product photography, hero shot, commercial quality.
```

## Limits

- No precise text rendering
- No pixel-level layout control
- No inpainting/outpainting
- Style consistency varies between generations
- Follows fal-ai usage policies

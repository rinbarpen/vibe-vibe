# Nano Banana Pro Reference

## Model IDs

| Model | fal-ai ID | Speed | Quality | Cost |
|-------|-----------|-------|---------|------|
| Nano Banana Pro v1 | `fal-ai/nano-banana-pro` | Fast (2-5s) | Good | Lower |
| Nano Banana Pro v2 | `fal-ai/nano-banana-pro-v2` | Medium (5-10s) | Excellent | Higher |

## Parameters Reference

| Parameter | Type | Range | Default | Notes |
|-----------|------|-------|---------|-------|
| `model` | string | v1 or v2 ID | v2 | v2 for quality, v1 for speed |
| `prompt` | string | — | *required* | Detailed for v2, concise for v1 |
| `negative_prompt` | string | — | "" | What to exclude |
| `aspect_ratio` | string | `1:1`, `16:9`, `9:16`, `4:3`, `3:4` | `1:1` | Match target format |
| `num_inference_steps` | int | 20-50 | 28 | Higher = more detail, slower |
| `guidance_scale` | float | 1-20 | 7.5 | Higher = more prompt adherence |
| `num_images` | int | 1-4 | 1 | 2-4 for variants |
| `seed` | int | any | random | Fixed seed = reproducible |

## Aspect Ratio Guide

| Ratio | Dimensions (typical) | Best For |
|-------|---------------------|----------|
| `1:1` | ~1024×1024 | Social media, avatars, square compositions |
| `16:9` | ~1280×720 up to 1920×1080 | Presentations, hero images, video thumbnails |
| `9:16` | ~720×1280 | Mobile wallpapers, Instagram stories, portrait |
| `4:3` | ~1024×768 | Traditional photos, general purpose |
| `3:4` | ~768×1024 | Book covers, portrait photos, posters |

## v1 vs v2 Decision Guide

### Use v1 when:
- Exploring multiple directions quickly
- Draft/concept stage — not final
- Simple subjects with few constraints
- Budget-sensitive batch generation
- Rough composition testing

### Use v2 when:
- Final/deliverable quality needed
- Complex scenes with many elements
- Strong prompt adherence required
- Fine details matter (faces, textures, text-like elements)
- Client-ready output

## Prompt Structure (v2)

```
[MAIN SUBJECT] + [APPEARANCE DETAILS] + [ENVIRONMENT/CONTEXT] + [LIGHTING TYPE + DIRECTION] + [COLOR PALETTE] + [MOOD/ATMOSPHERE] + [QUALITY BOOSTERS]
```

### v2 Example
```
A modern minimalist living room, floor-to-ceiling windows, natural oak flooring, L-shaped grey sofa,
indoor monstera and fiddle leaf fig plants, warm afternoon sunlight streaming through windows,
neutral color palette with sage green accents, serene and airy atmosphere.
Highly detailed, sharp focus, professional interior photography, 8k.
```

## Prompt Structure (v1)

```
[SUBJECT] + [STYLE] + [2-3 KEY DETAILS] + [LIGHTING/MOOD]. High quality.
```

### v1 Example
```
Minimalist living room, photorealistic, floor-to-ceiling windows, indoor plants, warm afternoon light. High quality.
```

## Negative Prompt

Common elements to exclude:
```
blurry, low quality, low resolution, distorted, deformed, ugly, bad anatomy,
bad proportions, extra limbs, cloned face, disfigured, gross proportions,
malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers,
too many fingers, long neck, watermark, text, signature, logo, artist name,
grainy, noisy, oversaturated, overexposed, underexposed, bad lighting
```

## Quality vs Speed

| Setting | v1 Speed | v1 Quality | v2 Speed | v2 Quality |
|---------|----------|------------|----------|------------|
| Low steps (20) | ~2s | Low | ~4s | Medium |
| Medium steps (28) | ~3s | Medium | ~6s | Good |
| High steps (36) | ~4s | Good | ~8s | Excellent |
| Max steps (50) | ~6s | Best(v1) | ~10s | Best(v2) |

# GPT-Image-2 Reference

## API Reference

**Endpoint**: `POST https://api.openai.com/v1/images/generations`

**Auth**: `Authorization: Bearer $OPENAI_API_KEY`

### Full Parameters

| Parameter | Type | Values | Default |
|-----------|------|--------|---------|
| `model` | string | `dall-e-3`, `dall-e-2` | `dall-e-3` |
| `prompt` | string | max 4000 chars | *required* |
| `n` | int | 1 (DALL-E 3), 1–10 (DALL-E 2) | 1 |
| `size` | string | `1024x1024`, `1792x1024`, `1024x1792` (DALL-E 3) / `256x256`, `512x512`, `1024x1024` (DALL-E 2) | `1024x1024` |
| `quality` | string | `standard`, `hd` (DALL-E 3 only) | `standard` |
| `style` | string | `vivid`, `natural` (DALL-E 3 only) | `vivid` |
| `response_format` | string | `url`, `b64_json` | `url` |
| `user` | string | end-user identifier | — |

### Size Guide

| Aspect | Size | Best For |
|--------|------|----------|
| 1:1 | 1024×1024 | General, social media, square compositions |
| 16:9 | 1792×1024 | Presentations, hero images, wide compositions |
| 9:16 | 1024×1792 | Mobile, portrait compositions, book covers |

### Style Comparison

| Setting | Effect | Use |
|---------|--------|-----|
| `vivid` | Hyper-real, dramatic, saturated | Eye-catching, marketing, concept art |
| `natural` | Realistic, subdued, natural tones | Photorealistic, editorial, factual |

## Cost Table

| Model | Quality | Size | Cost/Image |
|-------|---------|------|------------|
| DALL-E 3 | standard | 1024×1024 | $0.040 |
| DALL-E 3 | standard | 1024×1792 | $0.080 |
| DALL-E 3 | standard | 1792×1024 | $0.080 |
| DALL-E 3 | hd | 1024×1024 | $0.080 |
| DALL-E 3 | hd | 1024×1792 | $0.120 |
| DALL-E 3 | hd | 1792×1024 | $0.120 |
| DALL-E 2 | — | 1024×1024 | $0.020 |
| DALL-E 2 | — | 512×512 | $0.018 |
| DALL-E 2 | — | 256×256 | $0.016 |

## Style Keywords Reference

### Medium / Technique
`oil painting` `watercolor` `acrylic` `gouache` `pencil sketch` `charcoal` `ink drawing` `digital art` `digital painting` `3D render` `CGI` `vector illustration` `pixel art` `collage` `mixed media` `woodcut` `linocut` `screen print` `lithograph`

### Photography
`cinematic` `portrait photography` `landscape photography` `macro photography` `aerial photography` `street photography` `documentary style` `fashion photography` `product photography` `architectural photography` `astrophotography`

### Lens / Camera
`shot on 24mm` `shot on 35mm` `shot on 50mm` `shot on 85mm` `shot on 200mm` `wide angle` `telephoto` `macro lens` `tilt-shift` `fisheye`

### Lighting
`natural window light` `golden hour` `blue hour` `overcast` `studio lighting` `3-point lighting` `Rembrandt lighting` `split lighting` `rim light` `backlit` `soft diffused light` `hard directional light` `neon light` `candlelight` `moody chiaroscuro`

### Art Styles
`art nouveau` `art deco` `bauhaus` `baroque` `impressionism` `expressionism` `surrealism` `pop art` `minimalism` `brutalism` `cyberpunk` `steampunk` `vaporwave` `ukiyo-e` `art nouveau` `mid-century modern` `memphis design` `Swiss/international style`

### Mood / Atmosphere
`serene` `dramatic` `mysterious` `ominous` `playful` `whimsical` `melancholic` `nostalgic` `epic` `intimate` `cozy` `lonely` `energetic` `meditative` `chaotic`

### Color Palettes
`pastel` `vibrant` `monochromatic` `muted` `neon` `earth tones` `jewel tones` `warm colors` `cool colors` `complementary colors` `analogous colors` `high contrast` `low contrast` `black and white` `sepia` `duotone`

### Composition
`rule of thirds` `symmetrical` `asymmetrical` `centered` `diagonal` `leading lines` `framed` `negative space` `dutch angle` `bird's eye view` `worm's eye view` `close-up` `wide shot` `panoramic`

## Prompt Structure Formula

```
[SUBJECT] + [STYLE/MEDIUM] + [COMPOSITION/ANGLE] + [LIGHTING] + [COLOR PALETTE] + [MOOD/ATMOSPHERE] + [QUALIFIERS]
```

### Example Deconstruction
```
"A fluffy orange tabby cat"                           ← SUBJECT
"sitting on a windowsill"                             ← COMPOSITION
"rain streaming down the glass outside"               ← ENVIRONMENT
"warm lamp light from inside"                         ← LIGHTING
"cozy melancholic mood"                               ← MOOD
"soft focus, cinematic composition"                   ← QUALIFIERS
"natural color palette"                               ← COLOR
```

## Error Codes

| HTTP | Code | Meaning | Action |
|------|------|---------|--------|
| 400 | `invalid_request_error` | Bad prompt or param | Check prompt length, size validity |
| 401 | `authentication_error` | Bad API key | Verify `OPENAI_API_KEY` |
| 429 | `rate_limit_exceeded` | Too many requests | Exponential backoff |
| 429 | `insufficient_quota` | Billing limit | Check usage, add credits |
| 500 | `server_error` | OpenAI server | Retry after 30s |

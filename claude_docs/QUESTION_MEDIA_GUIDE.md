# Question Media Guide

## Overview

You can now add photos or videos to survey questions to provide visual context. This is perfect for:
- Product design comparisons ("Which design do you prefer?")
- Brand awareness studies (showing logos or packaging)
- Video tutorials or demonstrations
- Concept testing with mockups

The media (photo or video) is displayed **above the question text** and answer options.

---

## Quick Example

```json
{
  "id": "design_preference",
  "question": "Which design do you prefer?",
  "question_type": "single",
  "required": true,
  "options": ["Design A", "Design B", "No preference"],
  "media_url": "https://storage.googleapis.com/your-bucket/designs/comparison.jpg",
  "media_type": "photo"
}
```

---

## Schema Reference

### SurveyQuestion Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `media_url` | `string` | No | GCP bucket URL for the photo or video |
| `media_type` | `"photo"` or `"video"` | Only if `media_url` is provided | Type of media to display |

### Validation Rules

1. If `media_url` is provided, `media_type` **must** also be provided
2. Valid `media_type` values: `"photo"` or `"video"`
3. URLs should be publicly accessible GCS URLs

---

## Step-by-Step Guide

### 1. Upload Media to Google Cloud Storage

```bash
# Upload a photo
gsutil cp design-comparison.jpg gs://your-bucket-name/surveys/

# Upload a video
gsutil cp tutorial.mp4 gs://your-bucket-name/surveys/

# Make files publicly readable (or use signed URLs)
gsutil acl ch -u AllUsers:R gs://your-bucket-name/surveys/design-comparison.jpg
```

### 2. Get the Public URL

Format: `https://storage.googleapis.com/bucket-name/path/file.ext`

Example:
- Photo: `https://storage.googleapis.com/my-surveys/designs/option-a.jpg`
- Video: `https://storage.googleapis.com/my-surveys/videos/demo.mp4`

### 3. Add Media to Your Question

#### Using Python Script

```python
survey_flow = [
    {
        "id": "product_preference",
        "question": "Which product design appeals to you most?",
        "question_type": "single",
        "required": True,
        "options": [
            "Design A (shown above)",
            "Design B",
            "Neither"
        ],
        "media_url": "https://storage.googleapis.com/my-bucket/products/comparison.jpg",
        "media_type": "photo"
    },
    {
        "id": "tutorial_understanding",
        "question": "After watching the tutorial, how easy is the product to use?",
        "question_type": "single",
        "required": True,
        "options": [
            "Very easy",
            "Easy",
            "Neutral",
            "Difficult",
            "Very difficult"
        ],
        "media_url": "https://storage.googleapis.com/my-bucket/tutorials/setup.mp4",
        "media_type": "video"
    }
]
```

#### Using the API Directly

```bash
curl -X POST "http://localhost:8000/api/surveys/" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "survey_slug": "design-test",
    "name": "Product Design Survey",
    "survey_flow": [
      {
        "id": "q1",
        "question": "Which color do you prefer?",
        "question_type": "single",
        "required": true,
        "options": ["Red", "Blue", "Green"],
        "media_url": "https://storage.googleapis.com/bucket/colors.jpg",
        "media_type": "photo"
      }
    ],
    "is_active": true
  }'
```

---

## Media Type Details

### Photo Media

**Supported Formats:**
- JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)
- GIF (.gif)

**Recommendations:**
- Max file size: 5MB
- Recommended dimensions: 1200px wide max
- Aspect ratio: 16:9 or 4:3 works best
- Optimize images before uploading

**Display:**
- Renders as `<img>` tag
- Max height: 384px (24rem)
- Automatically sized to container width
- Maintains aspect ratio

### Video Media

**Supported Formats:**
- MP4 (.mp4) - **Recommended**
- WebM (.webm)
- Ogg (.ogg)

**Recommendations:**
- Max file size: 50MB
- Recommended resolution: 720p or 1080p
- Codec: H.264 for MP4
- Keep videos under 2 minutes

**Display:**
- Renders as `<video>` tag with controls
- Max height: 384px (24rem)
- User can play/pause, adjust volume, fullscreen
- Shows loading state while buffering

---

## Use Cases & Examples

### 1. Product Design Comparison

```json
{
  "id": "package_design",
  "question": "Which package design is more appealing?",
  "question_type": "single",
  "required": true,
  "options": [
    "Design A (left)",
    "Design B (right)",
    "Both are equal",
    "Neither"
  ],
  "media_url": "https://storage.googleapis.com/brand-study/packaging-options.jpg",
  "media_type": "photo"
}
```

### 2. Logo Recognition

```json
{
  "id": "logo_recognition",
  "question": "Do you recognize this brand?",
  "question_type": "single",
  "required": true,
  "options": [
    "Yes",
    "No",
    "Looks familiar but can't name it"
  ],
  "media_url": "https://storage.googleapis.com/brand-study/logo-test.jpg",
  "media_type": "photo"
}
```

### 3. Video Tutorial Feedback

```json
{
  "id": "tutorial_clarity",
  "question": "How clear were the instructions in the video?",
  "question_type": "single",
  "required": true,
  "options": [
    "Very clear",
    "Somewhat clear",
    "Neutral",
    "Somewhat unclear",
    "Very unclear"
  ],
  "media_url": "https://storage.googleapis.com/product-demos/setup-tutorial.mp4",
  "media_type": "video"
}
```

### 4. Multiple Media Questions

```json
{
  "survey_flow": [
    {
      "id": "concept_a",
      "question": "How appealing is this concept?",
      "question_type": "single",
      "required": true,
      "options": ["Very appealing", "Appealing", "Neutral", "Unappealing", "Very unappealing"],
      "media_url": "https://storage.googleapis.com/concepts/concept-a.jpg",
      "media_type": "photo"
    },
    {
      "id": "concept_b",
      "question": "How appealing is this concept?",
      "question_type": "single",
      "required": true,
      "options": ["Very appealing", "Appealing", "Neutral", "Unappealing", "Very unappealing"],
      "media_url": "https://storage.googleapis.com/concepts/concept-b.jpg",
      "media_type": "photo"
    },
    {
      "id": "preference",
      "question": "Which concept do you prefer overall?",
      "question_type": "single",
      "required": true,
      "options": ["Concept A", "Concept B", "No preference"]
    }
  ]
}
```

---

## Frontend Display

### Visual Hierarchy

```
┌─────────────────────────────────┐
│  Question Text                   │
│  (with required * if applicable) │
└─────────────────────────────────┘
            ↓
┌─────────────────────────────────┐
│                                  │
│     📷 MEDIA DISPLAY             │
│     (Photo or Video)             │
│                                  │
└─────────────────────────────────┘
            ↓
┌─────────────────────────────────┐
│  Answer Options                  │
│  ○ Option 1                      │
│  ○ Option 2                      │
│  ○ Option 3                      │
└─────────────────────────────────┘
```

### Component Features

- **Loading State**: Spinner while media loads
- **Error Handling**: Graceful fallback if media fails to load
- **Responsive**: Adapts to mobile and desktop screens
- **Accessibility**: Proper alt text and ARIA labels
- **Performance**: Lazy loading for images

---

## Testing Your Media Questions

### Run the Example Script

```bash
cd /home/mackers/tmg/marketResearch
python create_survey_with_media_example.py
```

This creates a demo survey with:
- Photo question (design comparison)
- Photo question (color variants)
- Video question (tutorial)
- Free text follow-up

### Manual Testing Checklist

- [ ] Photo loads correctly on desktop
- [ ] Photo loads correctly on mobile
- [ ] Video plays with controls
- [ ] Video doesn't autoplay
- [ ] Loading spinner shows while media loads
- [ ] Error message shows for invalid URLs
- [ ] Question is still answerable without media
- [ ] Submit button works after viewing media

---

## Best Practices

### Media Preparation

1. **Optimize Before Upload**
   - Compress images (TinyPNG, ImageOptim)
   - Compress videos (HandBrake, FFmpeg)
   - Remove unnecessary metadata

2. **File Naming**
   - Use descriptive names: `product-comparison-a-vs-b.jpg`
   - Avoid spaces: use hyphens or underscores
   - Include version if needed: `logo-v2.jpg`

3. **Organization**
   - Create folders by survey: `/surveys/product-test/`
   - Separate by type: `/photos/` and `/videos/`

### Question Design

1. **Clear Context**
   ```
   ✅ Good: "Which design shown above do you prefer?"
   ❌ Bad: "Which do you prefer?" (doesn't reference media)
   ```

2. **Refer to Media in Options**
   ```
   ✅ Good: ["Design A (left)", "Design B (right)"]
   ❌ Bad: ["This one", "That one"]
   ```

3. **Consider Load Times**
   - Keep videos under 2 minutes
   - Use lower resolution for longer videos
   - Provide context that doesn't require media

---

## Troubleshooting

### Media Not Displaying

**Check:**
1. Is the URL publicly accessible?
   ```bash
   curl -I https://storage.googleapis.com/your-bucket/file.jpg
   # Should return: HTTP/2 200
   ```

2. Is CORS configured on your bucket?
   ```bash
   gsutil cors set cors.json gs://your-bucket
   ```

   `cors.json`:
   ```json
   [{
     "origin": ["*"],
     "method": ["GET"],
     "responseHeader": ["Content-Type"],
     "maxAgeSeconds": 3600
   }]
   ```

3. Is the `media_type` correct?
   - Use `"photo"` for images
   - Use `"video"` for videos

### Video Won't Play

**Check:**
1. Video format is supported (MP4 recommended)
2. Video codec is H.264 (most compatible)
3. File size is reasonable (< 50MB)
4. URL is direct to video file (not a web page)

---

## API Reference

### POST /api/surveys/

Create a survey with media questions:

```json
{
  "survey_slug": "string",
  "name": "string",
  "survey_flow": [
    {
      "id": "string",
      "question": "string",
      "question_type": "single" | "multi" | "free_text" | "photo" | "video",
      "required": boolean,
      "options": ["string"],
      "media_url": "string (optional)",
      "media_type": "photo" | "video (required if media_url provided)"
    }
  ],
  "is_active": boolean
}
```

### Response

```json
{
  "id": 123,
  "survey_slug": "design-test",
  "name": "Product Design Survey",
  "survey_flow": [...],
  "is_active": true,
  "created_at": "2025-10-22T..."
}
```

---

## Security Considerations

1. **Public Access**: Only use media that's appropriate for public viewing
2. **Content Rights**: Ensure you have rights to all media used
3. **PII**: Don't include personally identifiable information in media
4. **File Size**: Large files can impact survey completion rates
5. **Bandwidth Costs**: Consider GCS egress costs for high-traffic surveys

---

## Support

For questions or issues:
1. Check this guide
2. Review the example script: `create_survey_with_media_example.py`
3. Test with the demo survey
4. Check browser console for errors

---

## Version History

- **v1.0** (2025-10-22): Initial release
  - Photo support
  - Video support
  - GCS URL integration
  - Loading states and error handling

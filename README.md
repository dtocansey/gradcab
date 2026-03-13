# GradCab - Student Peer Support Platform

GradCab is a student-led platform that supports newly admitted students during arrival and early campus settlement. It connects verified current students with incoming students to provide safe, structured peer assistance and coordination during their first days.

## Content Moderation System

To ensure a safe and welcoming community, GradCab uses an automated content moderation system powered by OpenAI's Moderation API. This system analyzes user posts in real-time and makes allow/block decisions based on customizable safety thresholds.

### ✨ Key Features

- **🚀 One-Command Operation** - Single Python script handles everything
- **📦 Batch Processing** - Moderate multiple posts from YAML files
- **⚙️ Custom Thresholds** - Fine-tune sensitivity per content category
- **🎯 Smart Decisions** - Clear ALLOW/BLOCK verdicts with reasoning
- **📝 Context-Aware** - Customizable system prompt for your platform
- **💾 Complete Logging** - JSON output with full details and scores
- **🔄 Production-Ready** - Built-in rate limiting and retry logic
- **💰 Free API** - OpenAI Moderation API is free to use

---

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [How It Works](#how-it-works)
- [Configuration Guide](#configuration-guide)
- [Usage Examples](#usage-examples)
- [File Reference](#file-reference)
- [Moderation Categories](#moderation-categories)
- [Decision Logic](#decision-logic)
- [Recommended Settings](#recommended-settings)
- [Troubleshooting](#troubleshooting)
- [Integration](#integration)
- [Security](#security)

---

## Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

**Requirements:**
- Python 3.7+
- openai >= 1.0.0
- pyyaml >= 6.0.0

### 2. Configuration

Add your OpenAI API key to `config.yaml`:

```yaml
openai:
  api_key: your-api-key-here
```

Or set environment variable:
```bash
export OPENAI_API_KEY='your-api-key-here'
```

### 3. Add Content

Edit `content.yaml` with posts to moderate:

```yaml
posts:
  - user_id: user_001
    content: "Hi! Looking for help getting from airport to campus."
  
  - user_id: user_002
    content: "Thanks everyone for the warm welcome!"
```

### 4. Run Moderation

```bash
python moderate_content.py
```

**Output:**
- Console: Summary and detailed results
- File: `content_results.json` with complete data

### 5. View Results

```json
{
  "total_posts": 2,
  "allowed": 2,
  "blocked": 0,
  "results": [...]
}
```

---

## How It Works

```
┌─────────────────┐
│  content.yaml   │  ← Input: Posts to moderate
└────────┬────────┘
         │
         ├──────────┐
         │          │
         ▼          ▼
┌─────────────┐  ┌──────────────────┐
│ config.yaml │  │ OpenAI Moderation│
│             │  │      API         │
│ • Thresholds│  │  (Free to use)   │
│ • API Key   │  └──────────────────┘
│ • Prompt    │
└─────┬───────┘
      │
      ▼
┌──────────────────────┐
│ moderate_content.py  │  ← Main script
│                      │
│ • Batch process      │
│ • Apply thresholds   │
│ • Make decisions     │
│ • Handle errors      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────┐
│ content_results.json  │  ← Output: Decisions + Details
└──────────────────────────┘
```

**Process Flow:**
1. Load posts from `content.yaml`
2. For each post:
   - Send to OpenAI Moderation API
   - Receive category scores (0.0 to 1.0)
   - Compare against your thresholds
   - Decide: ALLOW if all scores ≤ thresholds, else BLOCK
3. Save results with reasoning to JSON
4. Display summary in console

---

## Configuration Guide

### config.yaml Structure

```yaml
# API Configuration
openai:
  api_key: sk-proj-...         # Your OpenAI API key
  model: omni-moderation-latest # Model to use

# Moderation Settings
moderation:
  enabled: true
  
  # Thresholds: 0.0 (strictest) to 1.0 (most lenient)
  thresholds:
    sexual: 0.7
    hate: 0.5
    harassment: 0.6
    self_harm: 0.3
    sexual_minors: 0.1
    hate_threatening: 0.4
    violence_graphic: 0.6
    self_harm_intent: 0.3
    self_harm_instructions: 0.2
    harassment_threatening: 0.5
    violence: 0.7
  
  # File paths
  input_file: content.yaml
  output_file: content_results.json

# System prompt provides context to your moderation
system_prompt: |
  You are moderating user-generated content for GradCab,
  a student peer support platform connecting new students
  with current students for campus arrival assistance.
  
  Content must be:
  - Safe and respectful
  - Free from harmful material
  - Appropriate for students
  - Professional and supportive
```

### Understanding Thresholds

**Scale:** 0.0 to 1.0
- **Lower threshold** = Stricter (blocks more content)
- **Higher threshold** = Lenient (allows more content)

**How it works:**
```
If ANY score > threshold → BLOCK
If ALL scores ≤ thresholds → ALLOW
```

**Examples:**
```yaml
hate: 0.3   # Very strict - blocks at 30% confidence
hate: 0.5   # Moderate - blocks at 50% confidence
hate: 0.8   # Lenient - blocks at 80% confidence
```

---

## Usage Examples

### Basic Usage

```bash
# Moderate all posts in content.yaml
python moderate_content.py
```

### Testing with Sample Data

```bash
# 1. Use the test file (only 2 posts)
# Edit config.yaml:
moderation:
  input_file: content_test.yaml

# 2. Run moderation
python moderate_content.py

# 3. Check it works, then switch back to content.yaml
```

### Programmatic Integration

```python
from moderate_content import moderate_user_post, load_config

# Load configuration
config = load_config()

# Moderate a single post
user_content = "Looking for study buddies for CS courses!"
allow, details, violations = moderate_user_post(user_content, config)

if allow:
    # Post is safe - proceed
    database.save_post(user_content)
    return {"status": "approved"}
else:
    # Post violates policy
    return {
        "status": "rejected",
        "reasons": violations,
        "scores": details['category_scores']
    }
```

### Console Output Example

```
================================================================================
CONTENT MODERATION SYSTEM
================================================================================

📋 System Prompt:
--------------------------------------------------------------------------------
You are moderating user-generated content for GradCab...
--------------------------------------------------------------------------------

🔍 Moderating 8 posts from content.yaml...
⏳ Processing with rate limiting to avoid API errors...

[1/8] Processing user_001... ✅ ALLOWED
[2/8] Processing user_002... ✅ ALLOWED
[3/8] Processing user_003... ⚠️  BLOCKED
[4/8] Processing user_004... ✅ ALLOWED
...

✅ Results saved to content_results.json

================================================================================
MODERATION SUMMARY
================================================================================
Total Posts: 8
✅ Allowed: 6
⚠️  Blocked: 2
================================================================================

POST #3: user_003 - BLOCK
Content: [Harmful content example]
⚠️  Violated Thresholds:
   - hate (0.612 > 0.5)
   - harassment (0.723 > 0.6)
```

---

## File Reference

### Project Files

| File | Purpose | Committed |
|------|---------|-----------|
| `moderate_content.py` | Main moderation script | ✅ Yes |
| `config.yaml` | Your API key & settings | ❌ No (gitignored) |
| `config.example.yaml` | Configuration template | ✅ Yes |
| `content.yaml` | Posts to moderate | ✅ Yes |
| `content_test.yaml` | Small test dataset | ✅ Yes |
| `requirements.txt` | Python dependencies | ✅ Yes |
| `content_results.json` | Output (auto-generated) | ❌ No (gitignored) |

### Input Format (content.yaml)

```yaml
posts:
  - user_id: user_001
    content: "Post text goes here"
  
  - user_id: user_002
    content: "Another post to check"
```

**Required fields:**
- `user_id` - String identifier for the user
- `content` - Text content to moderate

### Output Format (content_results.json)

```json
{
  "timestamp": "2026-03-07T14:30:00.123456",
  "total_posts": 10,
  "allowed": 8,
  "blocked": 2,
  "system_prompt": "Your system prompt...",
  "results": [
    {
      "user_id": "user_001",
      "content": "Looking for campus tour help!",
      "decision": "ALLOW",
      "reason": "Passed moderation",
      "violated_thresholds": [],
      "category_scores": {
        "sexual": 0.000012,
        "hate": 0.000034,
        "harassment": 0.000023,
        "self_harm": 0.000001,
        "sexual_minors": 0.000001,
        "hate_threatening": 0.000002,
        "violence_graphic": 0.000003,
        "self_harm_intent": 0.000001,
        "self_harm_instructions": 0.000001,
        "harassment_threatening": 0.000002,
        "violence": 0.000005
      },
      "api_flagged": false
    },
    {
      "user_id": "user_002",
      "content": "[Problematic content]",
      "decision": "BLOCK",
      "reason": "Policy violation",
      "violated_thresholds": [
        "hate (0.612 > 0.5)",
        "harassment (0.723 > 0.6)"
      ],
      "category_scores": {...},
      "api_flagged": true
    }
  ]
}
```

---

## Moderation Categories

OpenAI's Moderation API evaluates content across 11 categories:

| Category | Description | Student Platform Threshold |
|----------|-------------|----------------------------|
| `sexual` | Sexual content | 0.7 |
| `hate` | Hateful/discriminatory content | 0.5 |
| `harassment` | Harassing/bullying content | 0.6 |
| `self_harm` | Self-harm promotion | 0.3 |
| `sexual_minors` | Sexual content involving minors | 0.1 |
| `hate_threatening` | Hateful content with threats | 0.4 |
| `violence_graphic` | Graphic violent content | 0.6 |
| `self_harm_intent` | Expressed intent to self-harm | 0.3 |
| `self_harm_instructions` | Instructional self-harm content | 0.2 |
| `harassment_threatening` | Harassing content with threats | 0.5 |
| `violence` | Violent content | 0.7 |

**API Returns:**
- Score for each category (0.0 to 1.0)
- Higher score = higher confidence of violation
- Your thresholds determine when to block

---

## Decision Logic

### Algorithm

```python
def should_allow_post(category_scores, thresholds):
    """
    Returns: (allow, violations)
    """
    violations = []
    
    for category, score in category_scores.items():
        threshold = thresholds[category]
        if score > threshold:
            violations.append(f"{category} ({score} > {threshold})")
    
    allow = len(violations) == 0
    return allow, violations
```

### Decision Matrix

```
┌──────────────────────────┬─────────┐
│ Condition                │ Result  │
├──────────────────────────┼─────────┤
│ ALL scores ≤ thresholds  │ ALLOW   │
│ ANY score > threshold    │ BLOCK   │
│ Empty content            │ BLOCK   │
│ API error                │ BLOCK   │
└──────────────────────────┴─────────┘
```

### Examples

**Example 1: Safe Post**
```
Content: "Looking for study buddies!"

Scores:
  hate: 0.0001        Threshold: 0.5  ✓ Pass
  harassment: 0.0002  Threshold: 0.6  ✓ Pass
  violence: 0.0003    Threshold: 0.7  ✓ Pass
  
Decision: ALLOW ✅
```

**Example 2: Problematic Post**
```
Content: "[Hateful message]"

Scores:
  hate: 0.612         Threshold: 0.5  ✗ Fail
  harassment: 0.723   Threshold: 0.6  ✗ Fail
  violence: 0.234     Threshold: 0.7  ✓ Pass
  
Violations:
  - hate (0.612 > 0.5)
  - harassment (0.723 > 0.6)
  
Decision: BLOCK ⚠️
```

---

## Recommended Settings

### For Student Platform (GradCab)

```yaml
thresholds:
  sexual: 0.7              # Allow relationship/dating discussion
  hate: 0.3                # Very strict on discrimination
  harassment: 0.4          # Strict on bullying
  self_harm: 0.2           # Very strict on self-harm
  sexual_minors: 0.05      # Extremely strict
  hate_threatening: 0.2    # Very strict on threats
  violence_graphic: 0.5    # Moderate strictness
  self_harm_intent: 0.2    # Very strict
  self_harm_instructions: 0.1  # Extremely strict
  harassment_threatening: 0.3  # Very strict
  violence: 0.6            # Moderate strictness
```

### For Public Forum

```yaml
thresholds:
  sexual: 0.85             # More lenient
  hate: 0.5                # Moderate
  harassment: 0.6          # Moderate
  self_harm: 0.3           # Strict
  sexual_minors: 0.1       # Very strict
  hate_threatening: 0.4    # Moderate
  violence_graphic: 0.7    # More lenient
  self_harm_intent: 0.3    # Strict
  self_harm_instructions: 0.2  # Strict
  harassment_threatening: 0.5  # Moderate
  violence: 0.8            # More lenient
```

### For Professional Platform

```yaml
thresholds:
  sexual: 0.5              # Stricter
  hate: 0.3                # Very strict
  harassment: 0.3          # Very strict
  self_harm: 0.2           # Very strict
  sexual_minors: 0.05      # Extremely strict
  hate_threatening: 0.2    # Very strict
  violence_graphic: 0.4    # Strict
  self_harm_intent: 0.2    # Very strict
  self_harm_instructions: 0.1  # Extremely strict
  harassment_threatening: 0.3  # Very strict
  violence: 0.4            # Strict
```

### Tuning Tips

1. **Start stricter** - Begin with lower thresholds, relax if needed
2. **Monitor results** - Check `content_results.json` regularly
3. **Test before deploying** - Use `content_test.yaml` for validation
4. **Consider context** - Student platform needs different settings than forums
5. **Adjust gradually** - Change thresholds by 0.1 increments

---

## Troubleshooting

### Common Issues

#### ❌ No API Key Found

**Error:**
```
ERROR: No OpenAI API key found.
```

**Solution:**
```bash
# Option 1: Add to config.yaml
openai:
  api_key: sk-proj-...

# Option 2: Set environment variable
export OPENAI_API_KEY='sk-proj-...'
```

#### ❌ 429 Too Many Requests

**Error:**
```
Error code: 429 - Too Many Requests
```

**Solution:**
- Script has built-in retry logic (3 attempts)
- Adds 1-second delay between requests
- If problem persists, wait a few minutes
- Check your OpenAI API rate limits

#### ❌ All Posts Blocked

**Problem:**
All posts show `BLOCK` decision

**Solution:**
1. Check if thresholds are too low
2. Increase thresholds in `config.yaml`
3. Test with known-safe content first:
   ```bash
   # Use content_test.yaml which has safe posts
   python moderate_content.py
   ```

#### ❌ No Posts Found

**Error:**
```
No posts found to moderate.
```

**Solution:**
1. Verify `content.yaml` exists
2. Check YAML syntax:
   ```yaml
   posts:  # Must have this key
     - user_id: user_001  # Correct indentation
       content: "text"
   ```
3. Ensure `posts` array is not empty

#### ❌ Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'yaml'
```

**Solution:**
```bash
pip install -r requirements.txt
```

---

## Integration

### Flask API Example

```python
from flask import Flask, request, jsonify
from moderate_content import moderate_user_post, load_config

app = Flask(__name__)
config = load_config()

@app.route('/api/posts', methods=['POST'])
def create_post():
    data = request.json
    content = data.get('content', '')
    user_id = data.get('user_id', '')
    
    # Moderate content
    allow, details, violations = moderate_user_post(content, config)
    
    if not allow:
        return jsonify({
            'error': 'Content violates community guidelines',
            'violations': violations,
            'scores': details['category_scores']
        }), 400
    
    # Content is safe - save to database
    post_id = database.create_post(user_id, content)
    
    return jsonify({
        'id': post_id,
        'status': 'approved',
        'user_id': user_id,
        'content': content
    }), 201
```

### Django View Example

```python
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from moderate_content import moderate_user_post, load_config
from .models import Post

config = load_config()

@require_http_methods(["POST"])
def create_post(request):
    content = request.POST.get('content', '')
    user_id = request.user.id
    
    # Moderate content
    allow, details, violations = moderate_user_post(content, config)
    
    if not allow:
        return JsonResponse({
            'success': False,
            'error': 'Content violates community guidelines',
            'details': violations
        }, status=400)
    
    # Save post
    post = Post.objects.create(user_id=user_id, content=content)
    
    return JsonResponse({
        'success': True,
        'post_id': post.id
    })
```

### Async Processing Example

```python
import asyncio
from moderate_content import moderate_user_post, load_config

async def moderate_posts_async(posts, config):
    """Moderate multiple posts concurrently"""
    tasks = []
    for post in posts:
        task = asyncio.create_task(
            moderate_single_post(post, config)
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results

async def moderate_single_post(post, config):
    # Run moderation in thread pool (OpenAI SDK is not async)
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None, 
        moderate_user_post,
        post['content'],
        config
    )
    return {
        'user_id': post['user_id'],
        'allow': result[0],
        'details': result[1]
    }
```

---

## Security

### API Key Protection

⚠️ **CRITICAL:** Never expose your API key

**✅ Do:**
- Store in `config.yaml` (gitignored)
- Use environment variables in production
- Rotate keys if exposed
- Use `.env` files (also gitignored)

**❌ Don't:**
- Commit `config.yaml` to git
- Hardcode keys in source files
- Share keys in chat/email
- Push keys to public repos

### .gitignore Verification

Ensure these are in `.gitignore`:

```gitignore
config.yaml
*.env
.env.*
content_results.json
```

### Production Checklist

- [ ] API key stored securely
- [ ] `config.yaml` not in git
- [ ] Environment-specific configs
- [ ] Rate limiting configured
- [ ] Error handling tested
- [ ] Logs don't contain keys
- [ ] Thresholds tested thoroughly

---

## Additional Information

### API Cost

**OpenAI Moderation API is FREE!** ✨

- No usage costs
- No rate limits (within reasonable use)
- No billing required
- Part of OpenAI's commitment to safety

### Documentation

- **OpenAI Moderation API:** https://platform.openai.com/docs/guides/moderation
- **OpenAI API Reference:** https://platform.openai.com/docs/api-reference/moderations
- **Python SDK:** https://github.com/openai/openai-python

### Rate Limiting

Built-in protections:
- 1-second delay between requests
- Exponential backoff (2s, 4s, 6s)
- Up to 3 retry attempts
- Graceful error handling

### Performance

Typical throughput:
- ~1 post per second (with delays)
- ~60 posts per minute
- ~3,600 posts per hour

For higher throughput, adjust delays in `moderate_batch()`.

---

## Support

### Getting Help

1. **Check this README** - Most answers are here
2. **Verify configuration** - Double-check `config.yaml` format
3. **Test with sample data** - Use `content_test.yaml`
4. **Check API status** - https://status.openai.com

### Reporting Issues

When reporting issues, include:
- Error messages (redact API keys!)
- Configuration (exclude `api_key`)
- Python version
- Sample input that fails

---

## License

This project is part of GradCab, developed for student community safety.

**Last Updated:** March 7, 2026

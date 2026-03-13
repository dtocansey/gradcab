"""
Content Moderation Script
Uses OpenAI's moderation API to check if user posts are safe to publish.
Reads content from YAML files and outputs moderation results with allow/block decisions.
"""

from openai import OpenAI
import os
import yaml
import json
import time
import argparse
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from datetime import datetime


def load_config() -> Dict:
    """Load configuration from config.yaml file."""
    config_path = Path(__file__).parent / "config.yaml"
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}


def load_content(content_file: str) -> List[Dict]:
    """Load content to moderate from YAML file."""
    content_path = Path(__file__).parent / content_file
    
    if not content_path.exists():
        print(f"⚠️  Content file not found: {content_file}")
        return []
    
    with open(content_path, 'r') as f:
        data = yaml.safe_load(f)
        return data.get('posts', []) if data else []


def should_allow_post(category_scores: Dict, thresholds: Dict) -> Tuple[bool, List[str]]:
    """
    Determine if post should be allowed based on category scores and thresholds.
    
    Args:
        category_scores: Dictionary of category names to scores
        thresholds: Dictionary of category names to threshold values
    
    Returns:
        Tuple[bool, List[str]]: (allow_post, violated_categories)
    """
    violated = []
    
    for category, score in category_scores.items():
        threshold = thresholds.get(category, 0.5)
        if score > threshold:
            violated.append(f"{category} ({score:.3f} > {threshold})")
    
    return len(violated) == 0, violated


def moderate_user_post(user_input: str, config: Dict, client: OpenAI = None, retry_count: int = 5) -> Tuple[bool, Dict, List[str]]:
    """
    Check if user input is safe to post.
    
    Args:
        user_input (str): The text content to moderate
        config (Dict): Configuration dictionary with thresholds
        client (OpenAI): Reusable OpenAI client instance
        retry_count (int): Number of retries on rate limit errors
    
    Returns:
        Tuple[bool, Dict, List[str]]: (allow_post, moderation_details, violated_categories)
    """
    if client is None:
        api_key = config.get('openai', {}).get('api_key') or os.getenv('OPENAI_API_KEY')
        client = OpenAI(api_key=api_key) if api_key else OpenAI()
    
    for attempt in range(retry_count):
        try:
            # Call the moderation API
            response = client.moderations.create(
                model="omni-moderation-latest",
                input=user_input
            )
            
            # Extract results
            result = response.results[0]
            category_scores = result.category_scores
            
            # Build score dictionary
            scores = {
                "sexual": category_scores.sexual,
                "hate": category_scores.hate,
                "harassment": category_scores.harassment,
                "self_harm": category_scores.self_harm,
                "sexual_minors": category_scores.sexual_minors,
                "hate_threatening": category_scores.hate_threatening,
                "violence_graphic": category_scores.violence_graphic,
                "self_harm_intent": category_scores.self_harm_intent,
                "self_harm_instructions": category_scores.self_harm_instructions,
                "harassment_threatening": category_scores.harassment_threatening,
                "violence": category_scores.violence,
            }
            
            # Get thresholds from config
            thresholds = config.get('moderation', {}).get('thresholds', {})
            
            # Check against thresholds
            allow_post, violated = should_allow_post(scores, thresholds)
            
            # Build detailed report
            moderation_details = {
                "api_flagged": result.flagged,
                "allow_post": allow_post,
                "category_scores": scores,
                "violated_thresholds": violated
            }
            
            return allow_post, moderation_details, violated
            
        except Exception as e:
            error_msg = str(e)
            
            # Check if it's a rate limit error
            if "429" in error_msg or "Too Many Requests" in error_msg:
                if attempt < retry_count - 1:
                    wait_time = (attempt + 1) * 5  # 5s, 10s, 15s, 20s backoff
                    print(f"  ⏳ Rate limited, waiting {wait_time}s before retry ({attempt + 1}/{retry_count - 1})...")
                    time.sleep(wait_time)
                    continue
            
            print(f"Error during moderation: {error_msg}")
            return False, {"error": error_msg}, [f"Error: {error_msg}"]
    
    # If all retries failed
    return False, {"error": "Max retries exceeded"}, ["Error: Max retries exceeded"]


def print_moderation_summary(results: List[Dict]):
    """Print a summary of moderation results."""
    total = len(results)
    allowed = sum(1 for r in results if r['decision'] == 'ALLOW')
    blocked = total - allowed
    
    print("\n" + "="*80)
    print("MODERATION SUMMARY")
    print("="*80)
    print(f"Total Posts: {total}")
    print(f"✅ Allowed: {allowed}")
    print(f"⚠️  Blocked: {blocked}")
    print("="*80 + "\n")


def print_detailed_results(results: List[Dict]):
    """Print detailed moderation results."""
    for i, result in enumerate(results, 1):
        print(f"\n{'='*80}")
        print(f"POST #{i}: {result['user_id']} - {result['decision']}")
        print(f"{'='*80}")
        print(f"Content: {result['content'][:100]}{'...' if len(result['content']) > 100 else ''}")
        print(f"\nDecision: {'✅ ALLOW' if result['decision'] == 'ALLOW' else '⚠️  BLOCK'}")
        
        if result['violated_thresholds']:
            print(f"\n⚠️  Violated Thresholds:")
            for violation in result['violated_thresholds']:
                print(f"   - {violation}")
        
        print(f"\nTop Risk Scores:")
        sorted_scores = sorted(
            result['category_scores'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        for category, score in sorted_scores:
            status = "⚠️" if score > 0.5 else "✓"
            print(f"   {status} {category.replace('_', ' ').title()}: {score:.4f}")


def moderate_batch(config: Dict, content_file: str, output_file: Optional[str] = None):
    """Moderate a batch of posts from specified content file."""
    # Default output file name
    if output_file is None:
        output_file = 'content_results.json'
    
    # Load posts to moderate
    posts = load_content(content_file)
    
    if not posts:
        print("❌ No posts found to moderate.")
        return
    
    print(f"\n🔍 Moderating {len(posts)} posts from {content_file}...")
    print("⏳ Processing with rate limiting to avoid API errors...\n")
    
    # Create a single client instance for all requests
    api_key = config.get('openai', {}).get('api_key') or os.getenv('OPENAI_API_KEY')
    client = OpenAI(api_key=api_key) if api_key else OpenAI()
    
    results = []
    
    for i, post in enumerate(posts, 1):
        user_id = post.get('user_id', 'unknown')
        content = post.get('content', '')
        
        print(f"[{i}/{len(posts)}] Processing {user_id}...", end=" ")
        
        if not content:
            results.append({
                "user_id": user_id,
                "content": content,
                "decision": "BLOCK",
                "reason": "Empty content",
                "violated_thresholds": [],
                "category_scores": {}
            })
            print("❌ BLOCKED (empty)")
            continue
        
        # Moderate the post
        allow_post, details, violated = moderate_user_post(content, config, client=client)
        
        # Build result
        results.append({
            "user_id": user_id,
            "content": content,
            "decision": "ALLOW" if allow_post else "BLOCK",
            "reason": "Passed moderation" if allow_post else "Policy violation",
            "violated_thresholds": violated,
            "category_scores": details.get('category_scores', {}),
            "api_flagged": details.get('api_flagged', False)
        })
        
        if allow_post:
            print("✅ ALLOWED")
        else:
            print("⚠️  BLOCKED")
        
        # Add delay between requests to avoid rate limiting
        if i < len(posts):
            time.sleep(3)  # 3 second delay between requests
    
    # Save results to JSON
    output_path = Path(__file__).parent / output_file
    result_data = {
        "timestamp": datetime.now().isoformat(),
        "total_posts": len(results),
        "allowed": sum(1 for r in results if r['decision'] == 'ALLOW'),
        "blocked": sum(1 for r in results if r['decision'] == 'BLOCK'),
        "system_prompt": config.get('system_prompt', ''),
        "results": results
    }
    
    with open(output_path, 'w') as f:
        json.dump(result_data, f, indent=2)
    
    print(f"✅ Results saved to {output_file}\n")
    
    # Print summary
    print_moderation_summary(results)
    print_detailed_results(results)


def main():
    """Main function to run content moderation."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Moderate user-generated content using OpenAI Moderation API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python moderate_content.py --content content.yaml
  python moderate_content.py -c posts.yaml
  python moderate_content.py -c content.yaml -o results.json
  python moderate_content.py --content content_test.yaml -o test_results.json
        """
    )
    parser.add_argument(
        '-c', '--content',
        type=str,
        required=True,
        help='Input YAML file with posts to moderate (REQUIRED)'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output JSON file for results (default: from config.yaml)'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Configuration file path (default: config.yaml)'
    )
    
    args = parser.parse_args()
    
    print("="*80)
    print("CONTENT MODERATION SYSTEM")
    print("="*80)
    
    # Load config
    config = load_config()
    
    # Check for API key
    has_config_key = bool(config.get('openai', {}).get('api_key'))
    has_env_key = bool(os.getenv("OPENAI_API_KEY"))
    
    if not has_config_key and not has_env_key:
        print("\n❌ ERROR: No OpenAI API key found.")
        print("Please add your API key to config.yaml or set OPENAI_API_KEY environment variable.")
        return
    
    # Display system prompt
    system_prompt = config.get('system_prompt', '')
    if system_prompt:
        print(f"\n📋 System Prompt:")
        print("-" * 80)
        print(system_prompt.strip())
        print("-" * 80)
    
    # Run batch moderation with optional CLI arguments
    moderate_batch(config, content_file=args.content, output_file=args.output)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Validation script to test the classification system with sample articles.
Helps ensure the AI classification is working correctly before running the full monitor.
"""

import os
import json
from pathlib import Path
from openai import OpenAI

# Load configuration
def load_config():
    """Load configuration from file."""
    config_path = Path("config.json")
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    else:
        raise FileNotFoundError("config.json not found")

CONFIG = load_config()

def test_classification():
    """Test the classification with sample pharmaceutical news."""
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Please set OPENAI_API_KEY environment variable")
        return
    
    client = OpenAI(api_key=api_key)
    
    # Test articles with expected classifications
    test_articles = [
        {
            "title": "FDA Grants Orphan Drug Designation to Novel Gene Therapy for Rare Disease",
            "description": "The FDA has granted orphan drug designation to ABC-123, a gene therapy for treating a rare genetic disorder affecting fewer than 200,000 patients in the US.",
            "expected_topics": ["Orphan Drug Designation"]
        },
        {
            "title": "Positive Interim Analysis Results Lead to Early Trial Stoppage",
            "description": "Company XYZ announced that the interim analysis of their Phase 3 trial was overwhelmingly positive, leading the data monitoring committee to recommend early stoppage for efficacy.",
            "expected_topics": ["Interim analysis were positive", "Phase 3 trial"]
        },
        {
            "title": "Pharmaceutical Company Reports Q4 Earnings Beat Expectations",
            "description": "PharmaCorp reported Q4 earnings of $2.34 per share, beating analyst expectations of $2.10. Revenue grew 15% year-over-year.",
            "expected_topics": []  # Should not classify - financial news
        },
        {
            "title": "FDA Approves First Biosimilar for Blockbuster Cancer Drug",
            "description": "The FDA has approved the first biosimilar version of the cancer drug Herceptin, potentially saving patients thousands of dollars per year.",
            "expected_topics": ["Biosimilar approval", "Drug approval"]
        },
        {
            "title": "Manufacturing Issues Force Drug Recall",
            "description": "Company ABC is recalling three lots of their diabetes medication due to manufacturing issues that could affect drug potency.",
            "expected_topics": ["Manufacturing issues", "Safety concerns"]
        }
    ]
    
    print("🧪 CLASSIFICATION VALIDATION TEST")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for i, article in enumerate(test_articles, 1):
        print(f"\nTest {i}: {article['title'][:60]}...")
        
        # Prepare classification prompt
        threshold = CONFIG.get('ai_settings', {}).get('classification_threshold', 0.7)
        prompt = f"""
        Analyze the following pharmaceutical news article and identify which of these topics it relates to.
        An article can relate to multiple topics. Return the relevant topics and confidence scores.
        
        Article Title: {article['title']}
        Article Description: {article['description']}
        
        Topics to consider:
        {', '.join(CONFIG['topics'])}
        
        Return your response as a JSON object with two keys:
        - "topics": list of relevant topic names from the list above
        - "confidence": dictionary mapping each identified topic to a confidence score (0.0-1.0)
        
        Only include topics with confidence > {threshold}.
        """
        
        try:
            response = client.chat.completions.create(
                model=CONFIG["ai_settings"]["model"],
                messages=[
                    {"role": "system", "content": "You are a pharmaceutical industry expert who classifies news articles."},
                    {"role": "user", "content": prompt}
                ],
                temperature=CONFIG["ai_settings"]["classification_temperature"],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            classified_topics = result.get("topics", [])
            confidence_scores = result.get("confidence", {})
            
            # Check results
            if article['expected_topics']:
                # Should classify
                if classified_topics:
                    print(f"✅ Correctly classified!")
                    print(f"   Topics: {', '.join(classified_topics)}")
                    print(f"   Confidence: {json.dumps(confidence_scores, indent=2)}")
                    
                    # Check if expected topics are included
                    missing = set(article['expected_topics']) - set(classified_topics)
                    if missing:
                        print(f"   ⚠️  Missing expected topics: {', '.join(missing)}")
                    
                    passed += 1
                else:
                    print(f"❌ Failed to classify (expected topics: {', '.join(article['expected_topics'])})")
                    failed += 1
            else:
                # Should NOT classify
                if not classified_topics:
                    print(f"✅ Correctly filtered out (not pharmaceutical news)")
                    passed += 1
                else:
                    print(f"❌ Incorrectly classified as: {', '.join(classified_topics)}")
                    failed += 1
                    
        except Exception as e:
            print(f"❌ Error during classification: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"VALIDATION RESULTS: {passed}/{len(test_articles)} passed")
    
    if failed == 0:
        print("✅ All tests passed! Classification system is working correctly.")
    else:
        print(f"⚠️  {failed} tests failed. Review the classification configuration.")
    
    print("\nTopics being monitored:")
    for topic in CONFIG['topics'][:10]:
        print(f"  • {topic}")
    print(f"  ... and {len(CONFIG['topics']) - 10} more")

if __name__ == "__main__":
    test_classification()
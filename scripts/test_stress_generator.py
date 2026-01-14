"""
Stress test generator for Teams to Slack migration pipeline.
Generates large synthetic Teams datasets to test scalability.
"""

import json
from datetime import datetime, timedelta
import random

def generate_large_teams_dataset(num_conversations: int = 1000, 
                                replies_per_conversation: int = 10) -> str:
    """
    Generate synthetic Teams export data for testing.
    
    Args:
        num_conversations: Number of parent messages
        replies_per_conversation: Average replies per conversation
    
    Returns:
        Path to generated JSON file
    """
    conversations = []
    user_ids = ["T-USER-99", "T-USER-44", "T-USER-55", "T-USER-66"]
    
    print(f"Generating {num_conversations} conversations with ~{replies_per_conversation} replies each...")
    print(f"Estimated total messages: {num_conversations * (1 + replies_per_conversation):,}")
    
    base_time = datetime(2026, 1, 1, 9, 0, 0)
    
    for i in range(num_conversations):
        # Parent message
        parent = {
            "id": f"MSG_{i:06d}",
            "createdDateTime": (base_time + timedelta(seconds=i*3600)).isoformat() + "Z",
            "from": {
                "user": {"id": random.choice(user_ids), "displayName": f"User {i % 4}"}
            },
            "body": {
                "contentType": "html",
                "content": f"<div>Parent message {i}: Check the <b>important update</b> on project {i % 100}?</div>"
            },
            "importance": "high" if random.random() > 0.7 else "normal",
            "reactions": [],
            "attachments": [],
            "replies": []
        }
        
        # Replies
        num_replies = random.randint(0, replies_per_conversation * 2)
        for j in range(num_replies):
            reply = {
                "id": f"MSG_{i:06d}_R{j:03d}",
                "replyToId": f"MSG_{i:06d}",
                "createdDateTime": (
                    base_time + timedelta(seconds=i*3600 + j*300)
                ).isoformat() + "Z",
                "from": {
                    "user": {"id": random.choice(user_ids), "displayName": f"User {j % 4}"}
                },
                "body": {
                    "contentType": "html",
                    "content": f"<div>Reply {j}: <i>Looks good</i>, approved.</div>"
                },
                "attachments": []
            }
            parent["replies"].append(reply)
        
        conversations.append(parent)
        
        if (i + 1) % 100 == 0:
            print(f"  Generated {i + 1} conversations...")
    
    # Write to file
    output_file = "data/teams_large_dataset.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(conversations, f, indent=2, ensure_ascii=False)
    
    total_messages = num_conversations + sum(len(c['replies']) for c in conversations)
    print(f"\n✓ Generated {output_file}")
    print(f"  Total messages: {total_messages:,}")
    print(f"  File size: {(len(json.dumps(conversations)) / (1024*1024)):.2f} MB")
    
    return output_file

if __name__ == "__main__":
    # Generate test datasets of various sizes
    
    # Small (good for testing)
    print("\n" + "="*60)
    print("SMALL DATASET (100 conversations)")
    print("="*60)
    generate_large_teams_dataset(num_conversations=100, replies_per_conversation=5)
    
    # Medium (tests performance)
    print("\n" + "="*60)
    print("MEDIUM DATASET (10,000 conversations)")
    print("="*60)
    generate_large_teams_dataset(num_conversations=10000, replies_per_conversation=10)
    
    # Large (stress test)
    print("\n" + "="*60)
    print("LARGE DATASET (100,000 conversations)")
    print("="*60)
    generate_large_teams_dataset(num_conversations=100000, replies_per_conversation=15)
    
    print("\n" + "="*60)
    print("To test, run:")
    print("  python pipeline/script.py --input data/teams_large_dataset.json")
    print("="*60)

"""
Test script for the AI Question Generator API
"""

import requests
import json
import time

def test_api():
    """Test the AI Question Generator API endpoints"""
    base_url = "http://localhost:8001"
    
    print("Testing AI Question Generator API...")
    print(f"Base URL: {base_url}")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"[PASS] Health check passed: {health_data['status']}")
            print(f"   Generator ready: {health_data['generator_ready']}")
            print(f"   Uptime: {health_data['uptime_seconds']:.2f}s")
        else:
            print(f"[FAIL] Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Health check error: {e}")
        return False
    
    # Test 2: Get available topics
    print("\n2. Testing available topics...")
    try:
        response = requests.get(f"{base_url}/topics")
        if response.status_code == 200:
            topics_data = response.json()
            print(f"✅ Topics retrieved: {topics_data['topics']}")
            print(f"   Levels: {topics_data['levels']}")
        else:
            print(f"❌ Topics retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Topics retrieval error: {e}")
        return False
    
    # Test 3: Generate questions
    print("\n3. Testing question generation...")
    test_request = {
        "topic": "AWS",
        "level": "beginner",
        "num_questions": 3,
        "keywords": ["EC2", "S3"]
    }
    
    try:
        response = requests.post(
            f"{base_url}/generate-questions",
            json=test_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            quiz_data = response.json()
            print(f"✅ Questions generated successfully!")
            print(f"   Topic: {quiz_data['topic']}")
            print(f"   Level: {quiz_data['level']}")
            print(f"   Total questions: {quiz_data['total_questions']}")
            print(f"   Generation time: {quiz_data['generation_time_ms']}ms")
            
            # Display first question
            if quiz_data['questions']:
                first_q = quiz_data['questions'][0]
                print(f"\n   Sample Question:")
                print(f"   ID: {first_q['id']}")
                print(f"   Question: {first_q['question']}")
                print(f"   Options: {first_q['options']}")
                print(f"   Correct: {first_q['correct']}")
                print(f"   Explanation: {first_q['explanation']}")
        else:
            print(f"❌ Question generation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Question generation error: {e}")
        return False
    
    # Test 4: Generate quiz (alternative endpoint)
    print("\n4. Testing quiz generation endpoint...")
    try:
        response = requests.post(
            f"{base_url}/generate-quiz",
            json=test_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            quiz_data = response.json()
            print(f"✅ Quiz generated successfully!")
            print(f"   Format: {list(quiz_data.keys())}")
        else:
            print(f"❌ Quiz generation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Quiz generation error: {e}")
        return False
    
    # Test 5: Validate questions
    print("\n5. Testing question validation...")
    test_questions = [
        {
            "id": "TEST_001",
            "core_type": "baseline",
            "level": "beginner",
            "topic": "AWS",
            "question": "What is EC2?",
            "options": {
                "A": "Virtual server",
                "B": "Storage service",
                "C": "Database",
                "D": "Network"
            },
            "correct": "A",
            "explanation": "EC2 provides virtual servers"
        },
        {
            "id": "TEST_002",
            "core_type": "invalid_type",  # This should cause an error
            "level": "beginner",
            "topic": "AWS",
            "question": "What is S3?",
            "options": {
                "A": "Virtual server",
                "B": "Storage service"
            },
            "correct": "C",  # This should cause an error (not in options)
            "explanation": "S3 provides storage"
        }
    ]
    
    try:
        response = requests.post(
            f"{base_url}/validate-questions",
            json=test_questions,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            validation_data = response.json()
            print(f"✅ Validation completed!")
            print(f"   Total questions: {validation_data['total_questions']}")
            print(f"   Valid questions: {validation_data['valid_questions']}")
            
            for result in validation_data['validation_results']:
                status = "✅" if result['is_valid'] else "❌"
                print(f"   {status} Question {result['question_index']}: {result['question_id']}")
                if result['issues']:
                    for issue in result['issues']:
                        print(f"      - {issue}")
        else:
            print(f"❌ Validation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False
    
    # Test 6: Get stats
    print("\n6. Testing stats endpoint...")
    try:
        response = requests.get(f"{base_url}/stats")
        if response.status_code == 200:
            stats_data = response.json()
            print(f"✅ Stats retrieved!")
            print(f"   Uptime: {stats_data['uptime_seconds']:.2f}s")
            print(f"   Available topics: {stats_data['available_topics']}")
            print(f"   Template count: {stats_data['template_count']}")
        else:
            print(f"❌ Stats retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Stats retrieval error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All API tests passed successfully!")
    print("The AI Question Generator is ready for integration.")
    return True

if __name__ == "__main__":
    # Wait a moment for the server to start
    time.sleep(2)
    test_api()

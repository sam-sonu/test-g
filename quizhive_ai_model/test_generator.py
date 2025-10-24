#!/usr/bin/env python3
"""
Test script to verify the AI question generator works correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model_server.ai_question_generator import AIQuestionGenerator
import json

def test_generator():
    """Test the AI question generator"""
    print("=== TESTING AI QUESTION GENERATOR ===")
    
    # Initialize generator
    generator = AIQuestionGenerator()
    
    # Test 1: Generate 8 questions for Python beginner
    print("\n1. Testing 8 Python beginner questions (should be 5 baseline, 3 variable):")
    quiz = generator.generate_quiz('Python', 'beginner', 8)
    
    # Check distribution
    baseline_count = sum(1 for q in quiz['questions'] if q['core_type'] == 'baseline')
    variable_count = sum(1 for q in quiz['questions'] if q['core_type'] == 'variable')
    
    print(f"   Total questions: {quiz['total_questions']}")
    print(f"   Baseline questions: {baseline_count}")
    print(f"   Variable questions: {variable_count}")
    print(f"   Expected ratio: 5:3 (60:40)")
    print(f"   Actual ratio: {baseline_count}:{variable_count}")
    
    # Print each question
    for i, q in enumerate(quiz['questions']):
        print(f"   Q{i+1}: {q['core_type']} - {q['question']}")
    
    # Test 2: Verify format matches expected structure
    print("\n2. Checking output format:")
    required_fields = ['id', 'core_type', 'level', 'topic', 'question', 'options', 'correct', 'explanation']
    
    for i, q in enumerate(quiz['questions']):
        missing_fields = [field for field in required_fields if field not in q]
        if missing_fields:
            print(f"   Question {i+1} missing fields: {missing_fields}")
        else:
            print(f"   Question {i+1}: ✓ All required fields present")
    
    # Test 3: Check for concept repetition
    print("\n3. Checking for concept repetition:")
    concepts_used = [q['question'].split()[-2].lower() for q in quiz['questions']]  # Extract concept from question
    unique_concepts = set(concepts_used)
    print(f"   Total concepts used: {len(concepts_used)}")
    print(f"   Unique concepts: {len(unique_concepts)}")
    print(f"   Repetitions: {len(concepts_used) - len(unique_concepts)}")
    
    # Test 4: Test different numbers
    print("\n4. Testing different question counts:")
    for num in [5, 10, 15]:
        test_quiz = generator.generate_quiz('Python', 'beginner', num)
        baseline = sum(1 for q in test_quiz['questions'] if q['core_type'] == 'baseline')
        variable = sum(1 for q in test_quiz['questions'] if q['core_type'] == 'variable')
        expected_baseline = int(num * 0.6)
        expected_variable = num - expected_baseline
        print(f"   {num} questions: {baseline}:{variable} (expected {expected_baseline}:{expected_variable})")
    
    # Test 5: Test different levels
    print("\n5. Testing different levels:")
    for level in ['beginner', 'intermediate', 'advanced']:
        test_quiz = generator.generate_quiz('Python', level, 10)
        baseline = sum(1 for q in test_quiz['questions'] if q['core_type'] == 'baseline')
        variable = sum(1 for q in test_quiz['questions'] if q['core_type'] == 'variable')
        print(f"   {level}: {baseline}:{variable}")
    
    # Test 6: Full JSON output
    print("\n6. Full JSON output for 8 questions:")
    print(json.dumps(quiz, indent=2))
    
    return quiz

if __name__ == "__main__":
    test_generator()

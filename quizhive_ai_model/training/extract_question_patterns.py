"""
Question Bank Pattern Extractor
Analyzes existing questions to extract templates and patterns for generation
"""

import json
import os
import re
from collections import defaultdict, Counter
from typing import Dict, List, Any, Tuple
import pandas as pd
from pathlib import Path


class QuestionPatternExtractor:
    def __init__(self, question_bank_path: str):
        self.question_bank_path = question_bank_path
        self.questions = []
        self.patterns = {}
        self.templates = {}
        
    def load_questions(self) -> List[Dict]:
        """Load questions from JSON files"""
        questions = []
        
        # Load from sample.json first
        sample_file = os.path.join(self.question_bank_path, "sample.json")
        if os.path.exists(sample_file):
            with open(sample_file, 'r', encoding='utf-8') as f:
                sample_questions = json.load(f)
                questions.extend(sample_questions)
                print(f"Loaded {len(sample_questions)} questions from sample.json")
        
        # Look for other JSON files in the directory
        for file in os.listdir(self.question_bank_path):
            if file.endswith('.json') and file != 'sample.json':
                file_path = os.path.join(self.question_bank_path, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_questions = json.load(f)
                        if isinstance(file_questions, list):
                            questions.extend(file_questions)
                            print(f"Loaded {len(file_questions)} questions from {file}")
                except Exception as e:
                    print(f"Error loading {file}: {e}")
        
        self.questions = questions
        print(f"Total questions loaded: {len(self.questions)}")
        return questions
    
    def analyze_question_structure(self) -> Dict:
        """Analyze the structure of questions"""
        if not self.questions:
            return {}
        
        analysis = {
            'total_questions': len(self.questions),
            'topics': {},
            'levels': {},
            'core_types': {},
            'question_patterns': {},
            'option_patterns': {},
            'explanation_patterns': {}
        }
        
        # Analyze topics
        topics = [q.get('topic', 'unknown') for q in self.questions]
        analysis['topics'] = dict(Counter(topics))
        
        # Analyze levels
        levels = [q.get('level', 'unknown') for q in self.questions]
        analysis['levels'] = dict(Counter(levels))
        
        # Analyze core types
        core_types = [q.get('core_type', 'unknown') for q in self.questions]
        analysis['core_types'] = dict(Counter(core_types))
        
        # Analyze question patterns
        question_starters = []
        question_lengths = []
        
        for q in self.questions:
            question_text = q.get('question', '')
            question_lengths.append(len(question_text.split()))
            
            # Extract question starters (first few words)
            words = question_text.split()[:3]
            if words:
                question_starters.append(' '.join(words))
        
        analysis['question_patterns'] = {
            'starters': dict(Counter(question_starters).most_common(20)),
            'avg_length': sum(question_lengths) / len(question_lengths) if question_lengths else 0,
            'length_distribution': dict(Counter([min(l, 20) for l in question_lengths]))
        }
        
        # Analyze options
        option_counts = []
        for q in self.questions:
            options = q.get('options', {})
            option_counts.append(len(options))
        
        analysis['option_patterns'] = {
            'counts': dict(Counter(option_counts)),
            'avg_count': sum(option_counts) / len(option_counts) if option_counts else 0
        }
        
        # Analyze explanations
        explanation_lengths = []
        for q in self.questions:
            explanation = q.get('explanation', '')
            explanation_lengths.append(len(explanation.split()))
        
        analysis['explanation_patterns'] = {
            'avg_length': sum(explanation_lengths) / len(explanation_lengths) if explanation_lengths else 0
        }
        
        return analysis
    
    def extract_templates(self) -> Dict:
        """Extract question templates based on patterns"""
        templates = {
            'by_topic': {},
            'by_level': {},
            'by_core_type': {},
            'question_structures': []
        }
        
        # Group questions by different criteria
        by_topic = defaultdict(list)
        by_level = defaultdict(list)
        by_core_type = defaultdict(list)
        
        for q in self.questions:
            topic = q.get('topic', 'unknown')
            level = q.get('level', 'unknown')
            core_type = q.get('core_type', 'unknown')
            
            by_topic[topic].append(q)
            by_level[level].append(q)
            by_core_type[core_type].append(q)
        
        # Extract templates for each group
        templates['by_topic'] = self._create_group_templates(by_topic)
        templates['by_level'] = self._create_group_templates(by_level)
        templates['by_core_type'] = self._create_group_templates(by_core_type)
        
        # Extract question structure templates
        templates['question_structures'] = self._extract_question_structures()
        
        return templates
    
    def _create_group_templates(self, group_dict: Dict) -> Dict:
        """Create templates for a grouped set of questions"""
        templates = {}
        
        for group_name, questions in group_dict.items():
            if len(questions) < 2:  # Need at least 2 questions to create a template
                continue
            
            # Extract common patterns
            question_patterns = []
            option_patterns = []
            
            for q in questions:
                question_text = q.get('question', '')
                
                # Create a pattern by replacing specific terms with placeholders
                pattern = self._create_question_pattern(question_text)
                question_patterns.append(pattern)
                
                # Analyze options
                options = q.get('options', {})
                if options:
                    option_patterns.append(list(options.keys()))
            
            # Find most common patterns
            common_question_patterns = Counter(question_patterns).most_common(5)
            common_option_patterns = Counter([tuple(p) for p in option_patterns]).most_common(3)
            
            templates[group_name] = {
                'question_count': len(questions),
                'question_patterns': [pattern for pattern, count in common_question_patterns],
                'option_patterns': [list(pattern) for pattern, count in common_option_patterns],
                'sample_questions': questions[:3]  # Keep sample questions
            }
        
        return templates
    
    def _create_question_pattern(self, question: str) -> str:
        """Create a pattern from a question by replacing specific terms"""
        # Replace technical terms with placeholders
        pattern = question
        
        # Common technical terms to replace
        tech_terms = [
            'AWS', 'EC2', 'S3', 'Lambda', 'RDS', 'VPC', 'IAM', 'CloudFormation',
            'Python', 'Java', 'JavaScript', 'React', 'Angular', 'Node.js',
            'SQL', 'NoSQL', 'MongoDB', 'PostgreSQL', 'MySQL',
            'Docker', 'Kubernetes', 'Jenkins', 'Git', 'Linux'
        ]
        
        for term in tech_terms:
            pattern = re.sub(rf'\b{term}\b', '{TECH_TERM}', pattern, flags=re.IGNORECASE)
        
        # Replace numbers
        pattern = re.sub(r'\b\d+\b', '{NUMBER}', pattern)
        
        # Replace specific values
        pattern = re.sub(r'["\'][^"\']+["\']', '{VALUE}', pattern)
        
        return pattern
    
    def _extract_question_structures(self) -> List[Dict]:
        """Extract common question structures"""
        structures = []
        
        for q in self.questions:
            question_text = q.get('question', '')
            
            # Identify question type
            if question_text.startswith('What'):
                q_type = 'what'
            elif question_text.startswith('How'):
                q_type = 'how'
            elif question_text.startswith('Why'):
                q_type = 'why'
            elif question_text.startswith('Which'):
                q_type = 'which'
            elif question_text.startswith('When'):
                q_type = 'when'
            elif question_text.startswith('Where'):
                q_type = 'where'
            else:
                q_type = 'other'
            
            structures.append({
                'type': q_type,
                'length': len(question_text.split()),
                'has_examples': 'example' in question_text.lower(),
                'sample': question_text[:100] + '...' if len(question_text) > 100 else question_text
            })
        
        # Group by type and find common patterns
        by_type = defaultdict(list)
        for struct in structures:
            by_type[struct['type']].append(struct)
        
        summary = []
        for q_type, structs in by_type.items():
            avg_length = sum(s['length'] for s in structs) / len(structs)
            has_examples_ratio = sum(s['has_examples'] for s in structs) / len(structs)
            
            summary.append({
                'type': q_type,
                'count': len(structs),
                'avg_length': avg_length,
                'has_examples_ratio': has_examples_ratio,
                'samples': [s['sample'] for s in structs[:3]]
            })
        
        return summary
    
    def save_analysis(self, output_dir: str = "data"):
        """Save analysis results to files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save basic analysis
        analysis = self.analyze_question_structure()
        with open(os.path.join(output_dir, 'question_analysis.json'), 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        # Save templates
        templates = self.extract_templates()
        with open(os.path.join(output_dir, 'question_templates.json'), 'w', encoding='utf-8') as f:
            json.dump(templates, f, indent=2, ensure_ascii=False)
        
        # Save questions as CSV for easy analysis
        if self.questions:
            df = pd.DataFrame(self.questions)
            df.to_csv(os.path.join(output_dir, 'questions.csv'), index=False)
        
        print(f"Analysis saved to {output_dir}/")
        return analysis, templates


def main():
    """Main function to run the analysis"""
    # Path to the existing question bank
    question_bank_path = "../quizhive/app/question_bank"
    
    extractor = QuestionPatternExtractor(question_bank_path)
    
    # Load questions
    extractor.load_questions()
    
    # Analyze and extract patterns
    analysis = extractor.analyze_question_structure()
    templates = extractor.extract_templates()
    
    # Save results
    extractor.save_analysis()
    
    # Print summary
    print("\n" + "="*50)
    print("QUESTION BANK ANALYSIS SUMMARY")
    print("="*50)
    print(f"Total Questions: {analysis['total_questions']}")
    print(f"Topics: {list(analysis['topics'].keys())}")
    print(f"Levels: {list(analysis['levels'].keys())}")
    print(f"Core Types: {list(analysis['core_types'].keys())}")
    print(f"Average Question Length: {analysis['question_patterns']['avg_length']:.1f} words")
    print(f"Average Options per Question: {analysis['option_patterns']['avg_count']:.1f}")
    print(f"Average Explanation Length: {analysis['explanation_patterns']['avg_length']:.1f} words")
    
    print("\nTop 5 Question Starters:")
    for starter, count in list(analysis['question_patterns']['starters'].items())[:5]:
        print(f"  {starter}: {count}")
    
    print("\nQuestion Structure Types:")
    for struct in templates['question_structures']:
        print(f"  {struct['type']}: {struct['count']} questions (avg {struct['avg_length']:.1f} words)")


if __name__ == "__main__":
    main()

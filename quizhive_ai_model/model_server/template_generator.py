"""
Template-based Question Generator
Generates questions using templates and patterns extracted from existing questions
Optimized for CPU-based execution on laptops
"""

import json
import random
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class QuestionRequest:
    """Request structure for question generation"""
    topic: str
    level: str
    num_questions: int
    core_type: Optional[str] = None
    keywords: Optional[List[str]] = None


@dataclass
class GeneratedQuestion:
    """Structure for generated questions"""
    id: str
    core_type: str
    level: str
    topic: str
    question: str
    options: Dict[str, str]
    correct: str
    explanation: str


class TemplateQuestionGenerator:
    def __init__(self, templates_path: str = "data/question_templates.json"):
        self.templates_path = templates_path
        self.templates = {}
        self.question_id_counter = 1000  # Start from 1000 to avoid conflicts
        self.load_templates()
        
        # Predefined question templates for different topics and levels
        self.topic_templates = self._initialize_topic_templates()
        
        # Technical terms and concepts for different domains
        self.technical_concepts = self._initialize_technical_concepts()
        
        # Question starters and patterns
        self.question_starters = [
            "What is",
            "Which of the following",
            "How does",
            "Why is",
            "When should you",
            "Where can you",
            "What are the benefits of",
            "What is the purpose of",
            "How do you",
            "Which statement best describes"
        ]
        
        # Explanation templates
        self.explanation_templates = [
            "This is the correct answer because {reason}.",
            "The correct choice is {option} as it {reason}.",
            "{option} is the right answer because {reason}.",
            "This option correctly describes {reason}.",
            "The answer is {option} because it {reason}."
        ]
    
    def load_templates(self):
        """Load templates from JSON file"""
        try:
            with open(self.templates_path, 'r', encoding='utf-8') as f:
                self.templates = json.load(f)
            print(f"Loaded templates from {self.templates_path}")
        except FileNotFoundError:
            print(f"Template file not found: {self.templates_path}")
            self.templates = {}
        except Exception as e:
            print(f"Error loading templates: {e}")
            self.templates = {}
    
    def _initialize_topic_templates(self) -> Dict[str, Dict]:
        """Initialize predefined templates for common technical topics"""
        return {
            "AWS": {
                "beginner": [
                    "What is {service} used for in AWS?",
                    "Which of the following best describes {service}?",
                    "How does {service} work in the AWS cloud?",
                    "What is the primary purpose of {service}?",
                    "When should you use {service}?"
                ],
                "intermediate": [
                    "How do you configure {service} for {scenario}?",
                    "What are the key differences between {service1} and {service2}?",
                    "Which {service} feature would you use for {scenario}?",
                    "How does {service} integrate with other AWS services?",
                    "What is the best practice for implementing {service}?"
                ],
                "advanced": [
                    "How would you optimize {service} for {scenario}?",
                    "What are the security implications of using {service}?",
                    "Design a solution using {service} for {complex_scenario}.",
                    "How do you troubleshoot common issues with {service}?",
                    "What are the performance characteristics of {service}?"
                ]
            },
            "Python": {
                "beginner": [
                    "What is the purpose of {concept} in Python?",
                    "How do you use {function} in Python?",
                    "Which data type would you use for {scenario}?",
                    "What does the {keyword} keyword do in Python?",
                    "How do you create a {structure} in Python?"
                ],
                "intermediate": [
                    "How would you implement {pattern} in Python?",
                    "What is the difference between {concept1} and {concept2}?",
                    "How do you handle {scenario} using Python's {feature}?",
                    "Which Python module would you use for {task}?",
                    "How do you optimize {operation} in Python?"
                ],
                "advanced": [
                    "How does Python's {mechanism} work internally?",
                    "Design a {architecture} using Python's {feature}.",
                    "What are the performance implications of using {technique}?",
                    "How would you implement {advanced_pattern} in Python?",
                    "What are the memory considerations when using {feature}?"
                ]
            },
            "Docker": {
                "beginner": [
                    "What is a {docker_concept}?",
                    "How do you create a {docker_object}?",
                    "What is the purpose of {docker_instruction}?",
                    "Which Docker command would you use for {action}?",
                    "What is the difference between {concept1} and {concept2}?"
                ],
                "intermediate": [
                    "How do you optimize {docker_object} for {scenario}?",
                    "What is the best way to {action} using Docker?",
                    "How would you implement {pattern} with Docker?",
                    "What are the security considerations for {docker_feature}?",
                    "How do you troubleshoot {docker_issue}?"
                ],
                "advanced": [
                    "Design a {architecture} using Docker and {technology}.",
                    "How would you implement {advanced_pattern} with Docker?",
                    "What are the performance characteristics of {docker_feature}?",
                    "How do you scale {docker_object} for {scenario}?",
                    "What are the networking implications of {docker_setup}?"
                ]
            }
        }
    
    def _initialize_technical_concepts(self) -> Dict[str, Dict]:
        """Initialize technical concepts for different domains"""
        return {
            "AWS": {
                "services": ["EC2", "S3", "Lambda", "RDS", "VPC", "IAM", "CloudFormation", "API Gateway", "SQS", "SNS"],
                "concepts": ["scalability", "high availability", "security", "cost optimization", "performance", "durability"],
                "scenarios": ["web hosting", "data storage", "serverless computing", "database management", "networking", "monitoring"]
            },
            "Python": {
                "concepts": ["list comprehension", "decorator", "generator", "context manager", "metaclass", "async/await"],
                "functions": ["print", "len", "range", "enumerate", "zip", "map", "filter", "reduce"],
                "data_types": ["list", "tuple", "dict", "set", "str", "int", "float"],
                "keywords": ["def", "class", "import", "from", "if", "for", "while", "try", "except"],
                "structures": ["function", "class", "module", "package", "list", "dictionary"]
            },
            "Docker": {
                "concepts": ["container", "image", "volume", "network", "service", "stack"],
                "instructions": ["FROM", "RUN", "COPY", "ADD", "CMD", "ENTRYPOINT", "WORKDIR", "EXPOSE"],
                "objects": ["Dockerfile", "docker-compose.yml", "container", "image", "volume"],
                "commands": ["build", "run", "push", "pull", "exec", "logs", "ps", "stop"]
            }
        }
    
    def generate_questions(self, request: QuestionRequest) -> List[GeneratedQuestion]:
        """Generate questions based on the request"""
        questions = []
        
        # Get templates for the topic and level
        templates = self._get_templates_for_topic_and_level(request.topic, request.level)
        
        if not templates:
            # If no specific templates found, use generic templates
            templates = self._get_generic_templates(request.level)
        
        for i in range(request.num_questions):
            question = self._generate_single_question(request, templates, i)
            questions.append(question)
        
        return questions
    
    def _get_templates_for_topic_and_level(self, topic: str, level: str) -> List[str]:
        """Get templates for a specific topic and level"""
        topic_upper = topic.upper()
        
        if topic_upper in self.topic_templates and level in self.topic_templates[topic_upper]:
            return self.topic_templates[topic_upper][level]
        
        # Try to find partial matches
        for key in self.topic_templates:
            if topic.upper() in key.upper() or key.upper() in topic.upper():
                if level in self.topic_templates[key]:
                    return self.topic_templates[key][level]
        
        return []
    
    def _get_generic_templates(self, level: str) -> List[str]:
        """Get generic templates when no specific templates are found"""
        generic_templates = {
            "beginner": [
                "What is {concept}?",
                "How do you use {concept}?",
                "What is the purpose of {concept}?",
                "Which of the following describes {concept}?",
                "When would you use {concept}?"
            ],
            "intermediate": [
                "How does {concept} work?",
                "What are the benefits of {concept}?",
                "How would you implement {concept}?",
                "What is the difference between {concept} and {alternative}?",
                "What are the best practices for {concept}?"
            ],
            "advanced": [
                "How would you optimize {concept}?",
                "What are the advanced features of {concept}?",
                "Design a solution using {concept}.",
                "What are the trade-offs of using {concept}?",
                "How does {concept} compare to alternatives?"
            ]
        }
        
        return generic_templates.get(level, generic_templates["beginner"])
    
    def _generate_single_question(self, request: QuestionRequest, templates: List[str], index: int) -> GeneratedQuestion:
        """Generate a single question"""
        # Select a random template
        template = random.choice(templates)
        
        # Fill template with appropriate concepts
        question_text = self._fill_template(template, request.topic, request.level, request.keywords)
        
        # Generate options
        options = self._generate_options(request.topic, request.level)
        
        # Select correct answer
        correct_option = random.choice(list(options.keys()))
        
        # Generate explanation
        explanation = self._generate_explanation(correct_option, options[correct_option], request.topic)
        
        # Determine core type
        core_type = request.core_type or self._determine_core_type(request.level, index)
        
        return GeneratedQuestion(
            id=f"AI_GEN_{self.question_id_counter + index}",
            core_type=core_type,
            level=request.level,
            topic=request.topic,
            question=question_text,
            options=options,
            correct=correct_option,
            explanation=explanation
        )
    
    def _fill_template(self, template: str, topic: str, level: str, keywords: Optional[List[str]]) -> str:
        """Fill template with appropriate concepts"""
        topic_upper = topic.upper()
        
        # Get concepts for the topic
        concepts = self.technical_concepts.get(topic_upper, {})
        
        # Replace placeholders
        if "{service}" in template and "services" in concepts:
            template = template.replace("{service}", random.choice(concepts["services"]))
        
        if "{concept}" in template and "concepts" in concepts:
            template = template.replace("{concept}", random.choice(concepts["concepts"]))
        
        if "{scenario}" in template and "scenarios" in concepts:
            template = template.replace("{scenario}", random.choice(concepts["scenarios"]))
        
        # Generic replacements
        if "{function}" in template:
            template = template.replace("{function}", f"the {random.choice(['appropriate', 'correct', 'suitable'])} function")
        
        if "{pattern}" in template:
            template = template.replace("{pattern}", f"{random.choice(['design', 'implementation', 'coding'])} pattern")
        
        if "{feature}" in template:
            template = template.replace("{feature}", f"the {random.choice(['main', 'key', 'primary'])} feature")
        
        # Use keywords if provided
        if keywords:
            for keyword in keywords:
                if "{keyword}" in template:
                    template = template.replace("{keyword}", keyword)
        
        return template
    
    def _generate_options(self, topic: str, level: str) -> Dict[str, str]:
        """Generate multiple choice options"""
        options = {}
        
        # Generate one correct option
        correct_text = self._generate_correct_option(topic, level)
        
        # Generate incorrect options
        incorrect_texts = self._generate_incorrect_options(topic, level, correct_text)
        
        # Combine and shuffle
        all_options = [correct_text] + incorrect_texts
        random.shuffle(all_options)
        
        # Assign to letters A, B, C, D
        for i, option_text in enumerate(all_options[:4]):
            options[chr(65 + i)] = option_text  # A, B, C, D
        
        return options
    
    def _generate_correct_option(self, topic: str, level: str) -> str:
        """Generate a correct option"""
        topic_upper = topic.upper()
        concepts = self.technical_concepts.get(topic_upper, {})
        
        if topic_upper == "AWS":
            return random.choice([
                "Provides scalable virtual servers in the cloud",
                "Offers object storage with high durability",
                "Enables serverless computing without provisioning servers",
                "Manages relational databases with automated backups"
            ])
        elif topic_upper == "PYTHON":
            return random.choice([
                "A built-in function that performs the specified operation",
                "A data structure that stores multiple values in an ordered sequence",
                "A keyword that defines a reusable block of code",
                "A method that processes each item in an iterable"
            ])
        elif topic_upper == "DOCKER":
            return random.choice([
                "A lightweight, standalone executable package that includes everything needed to run the application",
                "A text file that contains instructions for building a Docker image",
                "A storage mechanism that persists data generated by Docker containers",
                "A virtual network that allows containers to communicate with each other"
            ])
        else:
            return f"The correct approach for {topic.lower()} at {level} level"
    
    def _generate_incorrect_options(self, topic: str, level: str, correct_text: str) -> List[str]:
        """Generate incorrect but plausible options"""
        incorrect_options = []
        
        topic_upper = topic.upper()
        
        if topic_upper == "AWS":
            incorrect_pool = [
                "Manages user authentication and authorization",
                "Provides content delivery network services",
                "Monitors application performance and logs",
                "Automates resource deployment and management"
            ]
        elif topic_upper == "PYTHON":
            incorrect_pool = [
                "Compiles Python code to machine language",
                "Manages memory allocation and garbage collection",
                "Provides syntax highlighting and code completion",
                "Handles network communication between services"
            ]
        elif topic_upper == "DOCKER":
            incorrect_pool = [
                "Replaces virtual machines completely",
                "Eliminates the need for operating systems",
                "Provides automatic code compilation",
                "Manages database transactions and queries"
            ]
        else:
            incorrect_pool = [
                "An outdated approach that is no longer recommended",
                "A complex solution that requires extensive configuration",
                "A temporary workaround with limited functionality",
                "An experimental feature with no production support"
            ]
        
        # Select options that are different from the correct one
        for option in incorrect_pool:
            if option != correct_text and len(incorrect_options) < 3:
                incorrect_options.append(option)
        
        # Ensure we have 3 incorrect options
        while len(incorrect_options) < 3:
            incorrect_options.append(f"An incorrect option about {topic.lower()}")
        
        return incorrect_options[:3]
    
    def _generate_explanation(self, correct_option: str, correct_text: str, topic: str) -> str:
        """Generate an explanation for the correct answer"""
        reasons = [
            f"it accurately describes the primary function of {topic.lower()}",
            f"it represents the correct way to implement {topic.lower()}",
            f"it provides the most accurate definition for {topic.lower()}",
            f"it correctly identifies the key characteristic of {topic.lower()}",
            f"it aligns with best practices for {topic.lower()}"
        ]
        
        reason = random.choice(reasons)
        template = random.choice(self.explanation_templates)
        
        return template.format(
            option=correct_option,
            reason=reason
        )
    
    def _determine_core_type(self, level: str, index: int) -> str:
        """Determine core type based on level and position"""
        # For beginner level, start with more baseline questions
        if level == "beginner":
            return "baseline" if index < 7 else "variable"
        elif level == "intermediate":
            return "baseline" if index < 5 else "variable"
        else:  # advanced
            return "baseline" if index < 3 else "variable"
    
    def generate_quiz(self, topic: str, level: str, num_questions: int, keywords: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate a complete quiz"""
        request = QuestionRequest(
            topic=topic,
            level=level,
            num_questions=num_questions,
            keywords=keywords
        )
        
        questions = self.generate_questions(request)
        
        return {
            "topic": topic,
            "level": level,
            "total_questions": len(questions),
            "generated_at": datetime.now().isoformat(),
            "questions": [self._question_to_dict(q) for q in questions]
        }
    
    def _question_to_dict(self, question: GeneratedQuestion) -> Dict[str, Any]:
        """Convert GeneratedQuestion to dictionary"""
        return {
            "id": question.id,
            "core_type": question.core_type,
            "level": question.level,
            "topic": question.topic,
            "question": question.question,
            "options": question.options,
            "correct": question.correct,
            "explanation": question.explanation
        }


def main():
    """Test the question generator"""
    generator = TemplateQuestionGenerator()
    
    # Test generation
    quiz = generator.generate_quiz(
        topic="AWS",
        level="beginner",
        num_questions=5,
        keywords=["EC2", "S3"]
    )
    
    print("Generated Quiz:")
    print(json.dumps(quiz, indent=2))


if __name__ == "__main__":
    main()

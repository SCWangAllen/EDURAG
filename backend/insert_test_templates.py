#!/usr/bin/env python3
"""
Script to insert English test templates into the database
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

# Test templates data
TEST_TEMPLATES = [
    {
        'name': 'Test: True/False Questions (English)',
        'subject': 'science',
        'content': '''Based on the following educational content, generate true/false questions suitable for elementary students.

Educational Content:
{context}

Please create true/false questions with the following requirements:
1. Use simple, clear statements that students can easily understand
2. Avoid ambiguous or trick questions
3. Base questions on factual information from the content
4. Balance the number of true and false answers
5. Each question should test important concepts

Please generate questions asking students to determine if statements are true or false. Return in JSON format:
[
  {
    "prompt": "Clear statement to evaluate",
    "answer": "true or false", 
    "explanation": "Simple explanation of why this answer is correct"
  }
]''',
        'params': '{"temperature": 0.7, "max_tokens": 3000}'
    },
    {
        'name': 'Test: Matching Questions (English)',
        'subject': 'history',
        'content': '''Based on the following educational content, create matching questions for elementary students.

Educational Content: 
{context}

Please create matching questions with these requirements:
1. Provide 3-5 pairs of items to match
2. Left side: concepts, people, objects, or terms
3. Right side: corresponding definitions, descriptions, or functions  
4. Each match should be clear and unambiguous
5. Use vocabulary appropriate for young learners

Generate matching questions where students match items from left and right columns. Return in JSON format:
[
  {
    "prompt": "Match the items from the left column with the correct descriptions from the right column",
    "question_data": {
      "left_items": ["Item 1", "Item 2", "Item 3"],
      "right_items": ["Description 1", "Description 2", "Description 3"]
    },
    "answer": "Item 1 matches Description 1, Item 2 matches Description 2, Item 3 matches Description 3",
    "explanation": "Brief explanation of the matching relationships"
  }
]''',
        'params': '{"temperature": 0.7, "max_tokens": 3000}'
    },
    {
        'name': 'Test: Multiple Choice Questions (English)',
        'subject': 'english',
        'content': '''Based on the following educational content, create multiple choice questions for elementary students.

Educational Content:
{context}

Please create multiple choice questions with these requirements:
1. Provide exactly 4 options (A, B, C, D) for each question
2. Only one correct answer per question
3. Make distractors plausible but clearly incorrect
4. Use simple language appropriate for young learners
5. Test important concepts from the material

Generate single choice questions with 4 options each. Return in JSON format:
[
  {
    "prompt": "Question asking about the content",
    "options": ["A. First option", "B. Second option", "C. Correct option", "D. Fourth option"],
    "answer": "C",
    "explanation": "Explanation of why this answer is correct"
  }
]''',
        'params': '{"temperature": 0.7, "max_tokens": 3000}'
    },
    {
        'name': 'Test: Fill in the Blanks (English)',
        'subject': 'science',
        'content': '''Based on the following educational content, create fill-in-the-blank questions for elementary students.

Educational Content:
{context}

Please create cloze questions with these requirements:
1. Use ______ to mark blank spaces
2. Each blank should test one key concept
3. Provide clear context clues in the sentence
4. Make blanks appropriate difficulty for young learners
5. Focus on important vocabulary and concepts

Generate fill-in-the-blank questions using blanks for missing words. Return in JSON format:
[
  {
    "prompt": "Sentence with ______ marking the blank space to fill",
    "answer": "correct word or phrase",
    "explanation": "Why this word fits in the context"
  }
]''',
        'params': '{"temperature": 0.7, "max_tokens": 3000}'
    },
    {
        'name': 'Test: Short Answer Questions (English)',
        'subject': 'health',
        'content': '''Based on the following educational content, create short answer questions for elementary students.

Educational Content:
{context}

Please create short answer questions with these requirements:
1. Ask for brief explanations or descriptions
2. Questions should be answerable in 1-3 sentences
3. Focus on understanding rather than memorization
4. Use simple, direct question wording
5. Test comprehension of main concepts

Generate short answer questions requiring brief explanations. Return in JSON format:
[
  {
    "prompt": "Clear question asking for explanation or description",
    "answer": "Sample complete answer in 1-3 sentences",
    "explanation": "Key points that should be included in a good answer"
  }
]''',
        'params': '{"temperature": 0.7, "max_tokens": 3000}'
    },
    {
        'name': 'Test: Smart Detection Mixed (English)',
        'subject': 'general',
        'content': '''Based on the educational content below, please intelligently create questions that test student understanding.

Educational Content:
{context}

Instructions: Analyze the content and create questions that best fit the material. You may use any appropriate question format including true/false statements for fact checking, matching exercises for relationships, multiple choice for concept testing, or other formats as suitable.

Create questions that effectively assess student comprehension. Return in JSON format:
[
  {
    "prompt": "Appropriate question based on content analysis",
    "options": ["Only if multiple choice format"],
    "question_data": {"Only if matching or special format"},
    "answer": "Correct answer in appropriate format",
    "explanation": "Clear explanation of the answer"
  }
]''',
        'params': '{"temperature": 0.7, "max_tokens": 3000}'
    }
]

async def insert_templates():
    """Insert test templates into the database"""
    try:
        # Build connection string
        db_url = os.getenv('DATABASE_URL', 'postgresql://edurag_user:edurag_password@localhost:5432/edurag')
        
        # Parse the URL to get connection parameters
        if db_url.startswith('postgresql+asyncpg://'):
            db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
        
        print("Connecting to database...")
        conn = await asyncpg.connect(db_url)
        
        print("Inserting test templates...")
        for template in TEST_TEMPLATES:
            await conn.execute(
                """
                INSERT INTO templates (name, subject, content, params, is_active)
                VALUES ($1, $2, $3, $4, $5)
                """,
                template['name'],
                template['subject'],
                template['content'],
                template['params'],
                True
            )
            print(f"✅ Inserted: {template['name']}")
        
        await conn.close()
        print(f"\n🎉 Successfully inserted {len(TEST_TEMPLATES)} test templates!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(insert_templates())
    if success:
        print("\n✅ All test templates are ready for testing!")
    else:
        print("\n❌ Failed to insert test templates")
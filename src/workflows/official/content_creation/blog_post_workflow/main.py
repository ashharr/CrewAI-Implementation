#!/usr/bin/env python
"""
Blog Post Generation Workflow

This workflow creates SEO-optimized blog posts using a multi-agent approach:
1. Research Agent: Gathers information about the topic
2. SEO Specialist: Optimizes content for search engines
3. Content Writer: Creates engaging, well-structured content
"""

from datetime import datetime
from .crew import BlogPostCrew

def run(inputs=None):
    """
    Run the blog post generation workflow.
    
    Args:
        inputs (dict): Optional input parameters
            - topic (str): The blog post topic
            - target_audience (str): Target audience description
            - keywords (list): SEO keywords to target
            - word_count (int): Desired word count
            - tone (str): Writing tone (professional, casual, etc.)
    
    Returns:
        CrewOutput: The generated blog post and metadata
    """
    default_inputs = {
        'topic': 'Latest AI Development Trends',
        'target_audience': 'Tech professionals and developers',
        'keywords': ['AI development', 'machine learning', 'artificial intelligence'],
        'word_count': 1500,
        'tone': 'professional yet accessible',
        'current_year': str(datetime.now().year)
    }
    
    # Merge default inputs with provided inputs
    if inputs:
        default_inputs.update(inputs)
    
    print(f"🚀 Starting blog post generation for: {default_inputs['topic']}")
    print(f"📊 Target audience: {default_inputs['target_audience']}")
    print(f"🎯 Keywords: {', '.join(default_inputs['keywords'])}")
    
    result = BlogPostCrew().crew().kickoff(inputs=default_inputs)
    
    print("✅ Blog post generation completed!")
    return result

def train(n_iterations=3, filename='blog_post_training.pkl'):
    """
    Train the blog post workflow for better performance.
    
    Args:
        n_iterations (int): Number of training iterations
        filename (str): Training data filename
    """
    inputs = {
        'topic': 'AI in Healthcare',
        'target_audience': 'Healthcare professionals',
        'keywords': ['AI healthcare', 'medical AI', 'healthcare technology'],
        'word_count': 1200,
        'tone': 'professional',
        'current_year': str(datetime.now().year)
    }
    
    try:
        print(f"🎓 Training blog post workflow for {n_iterations} iterations...")
        BlogPostCrew().crew().train(
            n_iterations=n_iterations,
            filename=filename,
            inputs=inputs
        )
        print("✅ Training completed successfully!")
    except Exception as e:
        raise Exception(f"Training failed: {e}")

if __name__ == "__main__":
    # Example usage
    sample_inputs = {
        'topic': 'The Future of Remote Work Technology',
        'target_audience': 'Business leaders and HR professionals',
        'keywords': ['remote work', 'digital transformation', 'workplace technology'],
        'word_count': 2000,
        'tone': 'professional and insightful'
    }
    
    run(sample_inputs) 
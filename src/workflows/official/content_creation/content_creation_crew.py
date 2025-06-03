#!/usr/bin/env python
"""
Content Creation Crew - A practical use case for marketing content generation.
This crew includes a researcher, content strategist, and content writer working together.
"""

from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool, FileReadTool
from datetime import datetime
import os

class ContentCreationCrew:
    """Content Creation crew for marketing material generation"""
    
    def __init__(self):
        # Initialize tools
        self.search_tool = SerperDevTool()
        self.file_tool = FileReadTool()
        
    def market_researcher(self):
        """Agent specialized in market research and trend analysis"""
        return Agent(
            role='Market Research Specialist',
            goal='Research market trends, competitor analysis, and target audience insights for content strategy',
            backstory="""You are an experienced market researcher with 10+ years in digital marketing.
            You excel at identifying target audiences, analyzing competitor strategies, and spotting
            emerging trends that can be leveraged for content marketing. Your research forms the
            foundation for all content creation decisions.""",
            verbose=True,
            tools=[self.search_tool],
            allow_delegation=False
        )
    
    def content_strategist(self):
        """Agent specialized in content strategy and planning"""
        return Agent(
            role='Content Strategy Expert',
            goal='Develop comprehensive content strategies based on research insights and business objectives',
            backstory="""You are a senior content strategist with expertise in creating data-driven
            content plans. You transform market research into actionable content strategies,
            including content pillars, messaging frameworks, and content calendars. You understand
            how to align content with business goals and audience needs.""",
            verbose=True,
            allow_delegation=False
        )
    
    def content_writer(self):
        """Agent specialized in writing engaging content"""
        return Agent(
            role='Senior Content Writer',
            goal='Create compelling, engaging, and conversion-focused content based on strategic guidelines',
            backstory="""You are an award-winning content writer with expertise in various formats
            including blog posts, social media content, email campaigns, and marketing copy.
            You have a talent for translating complex strategies into engaging narratives that
            resonate with target audiences and drive action.""",
            verbose=True,
            allow_delegation=False
        )
    
    def research_market_task(self, topic, target_audience, business_type):
        """Task for conducting market research"""
        return Task(
            description=f"""
            Conduct comprehensive market research for {business_type} targeting {target_audience} 
            around the topic: {topic}
            
            Your research should include:
            1. Current market trends related to {topic}
            2. Competitor analysis (identify 3-5 key competitors)
            3. Target audience pain points and interests
            4. Popular content formats and channels
            5. Keyword opportunities and search trends
            6. Industry challenges and opportunities
            
            Focus on actionable insights that can inform content strategy.
            """,
            expected_output="""
            A detailed market research report with:
            - Market trends summary (5-7 key trends)
            - Competitor analysis with specific examples
            - Target audience persona and pain points
            - Content format recommendations
            - Top 10 relevant keywords/topics
            - Strategic opportunities identified
            """,
            agent=self.market_researcher()
        )
    
    def develop_strategy_task(self):
        """Task for developing content strategy"""
        return Task(
            description="""
            Based on the market research findings, develop a comprehensive content strategy that includes:
            
            1. Content pillars (3-5 main themes)
            2. Messaging framework and brand voice guidelines
            3. Content format recommendations (blog, social, video, etc.)
            4. Content calendar structure (frequency and timing)
            5. Distribution channel strategy
            6. Success metrics and KPIs
            7. Content repurposing opportunities
            
            Ensure the strategy is practical and actionable for implementation.
            """,
            expected_output="""
            A strategic content plan document containing:
            - 3-5 content pillars with descriptions
            - Brand voice and messaging guidelines
            - Recommended content mix and formats
            - Monthly content calendar framework
            - Distribution strategy across channels
            - Success metrics and measurement plan
            - Implementation timeline and priorities
            """,
            agent=self.content_strategist()
        )
    
    def create_content_task(self, content_type="blog post"):
        """Task for creating actual content"""
        return Task(
            description=f"""
            Create a high-quality {content_type} based on the research insights and content strategy.
            
            The content should:
            1. Address the target audience's main pain points
            2. Follow the established brand voice and messaging
            3. Include relevant keywords naturally
            4. Have a compelling headline and introduction
            5. Provide actionable value to readers
            6. Include a clear call-to-action
            7. Be optimized for the chosen distribution channel
            
            Make it engaging, informative, and conversion-focused.
            """,
            expected_output=f"""
            A complete, ready-to-publish {content_type} including:
            - Compelling headline and subheadings
            - Well-structured content with clear sections
            - Natural keyword integration
            - Engaging introduction and conclusion
            - Clear call-to-action
            - Meta description and SEO recommendations
            - Social media promotion suggestions
            """,
            agent=self.content_writer(),
            output_file=f'content_output_{content_type.replace(" ", "_")}.md'
        )
    
    def create_crew(self, topic, target_audience, business_type, content_type="blog post"):
        """Create and return the content creation crew"""
        
        # Create tasks
        research_task = self.research_market_task(topic, target_audience, business_type)
        strategy_task = self.develop_strategy_task()
        content_task = self.create_content_task(content_type)
        
        # Set up task dependencies
        strategy_task.context = [research_task]
        content_task.context = [research_task, strategy_task]
        
        # Create and return crew
        return Crew(
            agents=[
                self.market_researcher(),
                self.content_strategist(),
                self.content_writer()
            ],
            tasks=[research_task, strategy_task, content_task],
            process=Process.sequential,
            verbose=True
        )

def run_content_crew_example():
    """Example function to run the content creation crew"""
    
    # Example inputs
    topic = "AI automation for small businesses"
    target_audience = "small business owners aged 30-50"
    business_type = "SaaS company offering AI automation tools"
    content_type = "blog post"
    
    print(f"🚀 Starting Content Creation Crew for: {topic}")
    print(f"📊 Target Audience: {target_audience}")
    print(f"🏢 Business Type: {business_type}")
    print(f"📝 Content Type: {content_type}")
    print("-" * 60)
    
    # Initialize crew
    content_crew = ContentCreationCrew()
    crew = content_crew.create_crew(topic, target_audience, business_type, content_type)
    
    # Run the crew
    result = crew.kickoff()
    
    print("\n" + "="*60)
    print("✅ Content Creation Crew Completed!")
    print("📄 Check the generated files for the complete content package.")
    print("="*60)
    
    return result

if __name__ == "__main__":
    run_content_crew_example() 
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, FileReadTool
from typing import List

@CrewBase
class BlogPostCrew():
    """Blog Post Generation Crew
    
    A sophisticated multi-agent system for creating high-quality,
    SEO-optimized blog posts with research-backed content.
    """

    @agent
    def research_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['research_agent'],
            verbose=True,
            tools=[SerperDevTool(), FileReadTool()],
            max_iter=3,
            memory=True
        )

    @agent
    def seo_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['seo_specialist'],
            verbose=True,
            tools=[SerperDevTool()],
            max_iter=2,
            memory=True
        )

    @agent
    def content_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['content_writer'],
            verbose=True,
            memory=True
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'],
            output_file='research_findings.md'
        )

    @task
    def seo_optimization_task(self) -> Task:
        return Task(
            config=self.tasks_config['seo_optimization_task'],
            output_file='seo_strategy.md'
        )

    @task
    def content_writing_task(self) -> Task:
        return Task(
            config=self.tasks_config['content_writing_task'],
            output_file='blog_post.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Blog Post Generation crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            max_rpm=10,  # Rate limiting for API calls
            memory=True,
            embedder={
                "provider": "openai",
                "config": {"model": "text-embedding-3-small"}
            }
        ) 
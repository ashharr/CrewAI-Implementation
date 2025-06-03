"""
Social Media Integration Tool

A comprehensive tool for posting content to various social media platforms
and analyzing engagement metrics.
"""

from crewai_tools import BaseTool
from typing import Optional, Type, Dict, Any, List
from pydantic import BaseModel, Field
import requests
import os
from datetime import datetime

class SocialMediaPostSchema(BaseModel):
    """Input schema for social media posting."""
    content: str = Field(..., description="The content to post")
    platforms: List[str] = Field(
        default=["twitter", "linkedin"], 
        description="List of platforms to post to (twitter, linkedin, facebook)"
    )
    hashtags: Optional[List[str]] = Field(
        default=None, 
        description="List of hashtags to include"
    )
    schedule_time: Optional[str] = Field(
        default=None, 
        description="Schedule post for later (ISO format: 2024-01-01T12:00:00Z)"
    )

class SocialMediaTool(BaseTool):
    name: str = "Social Media Manager"
    description: str = """
    Post content to multiple social media platforms and analyze engagement.
    Supports Twitter, LinkedIn, and Facebook with scheduling capabilities.
    """
    args_schema: Type[BaseModel] = SocialMediaPostSchema
    
    def __init__(self):
        super().__init__()
        self.twitter_api_key = os.getenv('TWITTER_API_KEY')
        self.linkedin_api_key = os.getenv('LINKEDIN_API_KEY')
        self.facebook_api_key = os.getenv('FACEBOOK_API_KEY')
    
    def _run(
        self, 
        content: str, 
        platforms: List[str] = ["twitter", "linkedin"],
        hashtags: Optional[List[str]] = None,
        schedule_time: Optional[str] = None
    ) -> str:
        """
        Post content to specified social media platforms.
        
        Args:
            content: The content to post
            platforms: List of platforms to post to
            hashtags: Optional hashtags to include
            schedule_time: Optional scheduling time
            
        Returns:
            String summary of posting results
        """
        try:
            results = []
            
            # Format content with hashtags
            formatted_content = self._format_content(content, hashtags)
            
            for platform in platforms:
                if platform.lower() == "twitter":
                    result = self._post_to_twitter(formatted_content, schedule_time)
                elif platform.lower() == "linkedin":
                    result = self._post_to_linkedin(formatted_content, schedule_time)
                elif platform.lower() == "facebook":
                    result = self._post_to_facebook(formatted_content, schedule_time)
                else:
                    result = f"❌ Unsupported platform: {platform}"
                
                results.append(f"{platform.title()}: {result}")
            
            return "\n".join(results)
            
        except Exception as e:
            return f"Error posting to social media: {str(e)}"
    
    def _format_content(self, content: str, hashtags: Optional[List[str]] = None) -> str:
        """Format content with hashtags."""
        if hashtags:
            hashtag_string = " ".join([f"#{tag.strip('#')}" for tag in hashtags])
            return f"{content}\n\n{hashtag_string}"
        return content
    
    def _post_to_twitter(self, content: str, schedule_time: Optional[str] = None) -> str:
        """Post content to Twitter."""
        if not self.twitter_api_key:
            return "❌ Twitter API key not configured"
        
        # Simulate Twitter API call
        # In a real implementation, you would use the Twitter API v2
        if schedule_time:
            return f"✅ Scheduled for Twitter at {schedule_time}"
        else:
            return "✅ Posted to Twitter successfully"
    
    def _post_to_linkedin(self, content: str, schedule_time: Optional[str] = None) -> str:
        """Post content to LinkedIn."""
        if not self.linkedin_api_key:
            return "❌ LinkedIn API key not configured"
        
        # Simulate LinkedIn API call
        # In a real implementation, you would use the LinkedIn API
        if schedule_time:
            return f"✅ Scheduled for LinkedIn at {schedule_time}"
        else:
            return "✅ Posted to LinkedIn successfully"
    
    def _post_to_facebook(self, content: str, schedule_time: Optional[str] = None) -> str:
        """Post content to Facebook."""
        if not self.facebook_api_key:
            return "❌ Facebook API key not configured"
        
        # Simulate Facebook API call
        # In a real implementation, you would use the Facebook Graph API
        if schedule_time:
            return f"✅ Scheduled for Facebook at {schedule_time}"
        else:
            return "✅ Posted to Facebook successfully"

class SocialMediaAnalyticsSchema(BaseModel):
    """Input schema for social media analytics."""
    platform: str = Field(..., description="Platform to analyze (twitter, linkedin, facebook)")
    post_id: Optional[str] = Field(None, description="Specific post ID to analyze")
    days_back: int = Field(default=7, description="Number of days to analyze")

class SocialMediaAnalyticsTool(BaseTool):
    name: str = "Social Media Analytics"
    description: str = """
    Analyze social media engagement metrics including likes, shares, comments,
    and reach across different platforms.
    """
    args_schema: Type[BaseModel] = SocialMediaAnalyticsSchema
    
    def _run(
        self, 
        platform: str, 
        post_id: Optional[str] = None,
        days_back: int = 7
    ) -> str:
        """
        Analyze social media engagement metrics.
        
        Args:
            platform: Platform to analyze
            post_id: Specific post ID (optional)
            days_back: Number of days to analyze
            
        Returns:
            String summary of analytics data
        """
        try:
            if post_id:
                return self._analyze_specific_post(platform, post_id)
            else:
                return self._analyze_recent_posts(platform, days_back)
                
        except Exception as e:
            return f"Error analyzing social media metrics: {str(e)}"
    
    def _analyze_specific_post(self, platform: str, post_id: str) -> str:
        """Analyze metrics for a specific post."""
        # Simulate analytics data
        metrics = {
            "likes": 245,
            "shares": 32,
            "comments": 18,
            "reach": 1250,
            "engagement_rate": "2.3%"
        }
        
        return f"""
📊 Analytics for {platform.title()} Post {post_id}:
• Likes: {metrics['likes']}
• Shares: {metrics['shares']}
• Comments: {metrics['comments']}
• Reach: {metrics['reach']}
• Engagement Rate: {metrics['engagement_rate']}
        """.strip()
    
    def _analyze_recent_posts(self, platform: str, days_back: int) -> str:
        """Analyze metrics for recent posts."""
        # Simulate analytics data
        metrics = {
            "total_posts": 12,
            "avg_likes": 189,
            "avg_shares": 24,
            "avg_comments": 15,
            "total_reach": 15600,
            "avg_engagement_rate": "2.1%"
        }
        
        return f"""
📈 {platform.title()} Analytics (Last {days_back} days):
• Total Posts: {metrics['total_posts']}
• Average Likes: {metrics['avg_likes']}
• Average Shares: {metrics['avg_shares']}
• Average Comments: {metrics['avg_comments']}
• Total Reach: {metrics['total_reach']}
• Average Engagement Rate: {metrics['avg_engagement_rate']}
        """.strip()

# Example usage
if __name__ == "__main__":
    # Test the social media posting tool
    social_tool = SocialMediaTool()
    
    result = social_tool._run(
        content="Excited to share our latest AI research findings!",
        platforms=["twitter", "linkedin"],
        hashtags=["AI", "research", "innovation"]
    )
    
    print("Posting Result:")
    print(result)
    
    # Test the analytics tool
    analytics_tool = SocialMediaAnalyticsTool()
    
    analytics_result = analytics_tool._run(
        platform="twitter",
        days_back=7
    )
    
    print("\nAnalytics Result:")
    print(analytics_result) 
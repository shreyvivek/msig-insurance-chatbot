"""
Instagram profile scraper with image analysis
Fetches public Instagram profile and analyzes posts/images
"""
import os
import logging
import re
from typing import Dict, List, Optional
from datetime import datetime

# Try to import dependencies, but don't fail if not available
try:
    import instaloader
    INSTALOADER_AVAILABLE = True
except ImportError:
    INSTALOADER_AVAILABLE = False
    instaloader = None

try:
    from PIL import Image
    from io import BytesIO
    import requests
    IMAGE_ANALYSIS_AVAILABLE = True
except ImportError:
    IMAGE_ANALYSIS_AVAILABLE = False
    Image = None
    BytesIO = None
    requests = None

logger = logging.getLogger(__name__)

class ProfileScraper:
    """Scrapes Instagram public profiles and analyzes images/posts"""
    
    def __init__(self):
        if not INSTALOADER_AVAILABLE:
            logger.warning("⚠️  instaloader not installed - Instagram scraping disabled")
            logger.warning("   Install with: pip install instaloader")
            self.instaloader = None
            return
        
        self.instaloader = instaloader.Instaloader(
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False
        )
        # Don't login - we only need public data
        logger.info("✅ ProfileScraper initialized")
    
    async def fetch_instagram_profile(self, username: str) -> Dict:
        """
        Scrape Instagram public profile and posts
        Analyzes images and captions for adventure/travel content
        
        Args:
            username: Instagram username (without @)
            
        Returns:
            Dictionary with profile data, posts, and analysis
        """
        if not INSTALOADER_AVAILABLE:
            return {
                "username": username,
                "error": "Instagram scraping not available - instaloader not installed",
                "posts_data": []
            }
        
        try:
            # Load profile
            profile = instaloader.Profile.from_username(self.instaloader.context, username)
            
            if profile.is_private:
                logger.warning(f"Profile @{username} is private - cannot fetch posts")
                return {
                    "username": username,
                    "is_private": True,
                    "posts_data": [],
                    "bio": profile.biography if profile.biography else None,
                    "error": "Profile is private"
                }
            
            # Fetch profile metadata
            profile_data = {
                "username": username,
                "full_name": profile.full_name,
                "bio": profile.biography,
                "posts_count": profile.mediacount,
                "follower_count": profile.followers,
                "following_count": profile.followees,
                "is_private": profile.is_private,
                "is_verified": profile.is_verified
            }
            
            # Fetch recent posts (up to 30)
            posts_data = []
            post_count = 0
            max_posts = 30
            
            logger.info(f"Fetching up to {max_posts} posts from @{username}...")
            
            for post in profile.get_posts():
                if post_count >= max_posts:
                    break
                
                try:
                    post_info = {
                        "post_id": post.shortcode,
                        "caption": post.caption or "",
                        "hashtags": self._extract_hashtags(post.caption or ""),
                        "timestamp": post.date_utc.isoformat() if post.date_utc else None,
                        "likes": post.likes,
                        "comments": post.comments,
                        "is_video": post.is_video,
                        "location": post.location.name if post.location else None
                    }
                    
                    # Download and analyze image if it's a photo
                    if not post.is_video:
                        try:
                            # Download image
                            image_url = post.url
                            image_analysis = await self._analyze_image(image_url)
                            post_info["image_analysis"] = image_analysis
                        except Exception as e:
                            logger.debug(f"Could not analyze image for post {post.shortcode}: {e}")
                            post_info["image_analysis"] = None
                    
                    posts_data.append(post_info)
                    post_count += 1
                    
                except Exception as e:
                    logger.warning(f"Error processing post: {e}")
                    continue
            
            logger.info(f"✅ Fetched {len(posts_data)} posts from @{username}")
            
            return {
                **profile_data,
                "posts_data": posts_data,
                "posts_fetched": len(posts_data)
            }
            
        except instaloader.exceptions.ProfileNotExistsException:
            logger.error(f"Profile @{username} does not exist")
            return {
                "username": username,
                "error": "Profile does not exist",
                "posts_data": []
            }
        except instaloader.exceptions.ConnectionException as e:
            logger.error(f"Connection error fetching @{username}: {e}")
            return {
                "username": username,
                "error": "Connection error - Instagram may be rate limiting",
                "posts_data": []
            }
        except Exception as e:
            logger.error(f"Error fetching Instagram profile @{username}: {e}", exc_info=True)
            return {
                "username": username,
                "error": str(e),
                "posts_data": []
            }
    
    async def _analyze_image(self, image_url: str) -> Optional[Dict]:
        """
        Analyze image for adventure/travel content
        Uses keyword-based analysis (can be enhanced with vision models)
        
        Args:
            image_url: URL of the image
            
        Returns:
            Dictionary with image analysis results
        """
        if not IMAGE_ANALYSIS_AVAILABLE:
            return None
        
        try:
            # Download image
            response = requests.get(image_url, timeout=10)
            if response.status_code != 200:
                return None
            
            image = Image.open(BytesIO(response.content))
            
            # Simple analysis - in production, could use vision models
            # For now, we'll rely on captions/hashtags which are more reliable
            
            return {
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "size_kb": len(response.content) / 1024,
                # Could add vision model analysis here
                "detected_scenes": []  # Placeholder for future vision model integration
            }
        except Exception as e:
            logger.debug(f"Image analysis failed: {e}")
            return None
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        if not text:
            return []
        hashtags = re.findall(r'#(\w+)', text)
        return [tag.lower() for tag in hashtags]
    
    def _extract_mentions(self, text: str) -> List[str]:
        """Extract @mentions from text"""
        if not text:
            return []
        mentions = re.findall(r'@(\w+)', text)
        return mentions
    
    async def get_profile_summary(self, username: str) -> Dict:
        """
        Quick summary of profile (lighter weight than full fetch)
        """
        if not INSTALOADER_AVAILABLE:
            return {
                "username": username,
                "error": "Instagram scraping not available"
            }
        
        try:
            profile = instaloader.Profile.from_username(self.instaloader.context, username)
            return {
                "username": username,
                "full_name": profile.full_name,
                "bio": profile.biography,
                "is_private": profile.is_private,
                "posts_count": profile.mediacount,
                "follower_count": profile.followers
            }
        except Exception as e:
            logger.error(f"Error getting profile summary: {e}")
            return {
                "username": username,
                "error": str(e)
            }


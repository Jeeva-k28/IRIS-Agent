from website_workflows.youtube.youtube_workflow import YouTubeWorkflow
from website_workflows.google.google_workflow import GoogleWorkflow
from website_workflows.github.github_workflow import GitHubWorkflow
from website_workflows.gmail.gmail_workflow import GmailWorkflow
from website_workflows.google_drive.google_drive_workflow import GoogleDriveWorkflow
from website_workflows.wikipedia.wikipedia_workflow import WikipediaWorkflow
from website_workflows.amazon.amazon_workflow import AmazonWorkflow
from website_workflows.flipkart.flipkart_workflow import FlipkartWorkflow
from website_workflows.linkedin.linkedin_workflow import LinkedInWorkflow
from website_workflows.instagram.instagram_workflow import InstagramWorkflow
from website_workflows.facebook.facebook_workflow import FacebookWorkflow
from website_workflows.x.x_workflow import XWorkflow
from website_workflows.reddit.reddit_workflow import RedditWorkflow
from website_workflows.chatgpt.chatgpt_workflow import ChatGPTWorkflow

WORKFLOW_REGISTRY = {
    "youtube.com": YouTubeWorkflow(),
    "google.com": GoogleWorkflow(),
    "github.com": GitHubWorkflow(),
    "mail.google.com": GmailWorkflow(),
    "gmail.com": GmailWorkflow(),
    "drive.google.com": GoogleDriveWorkflow(),
    "wikipedia.org": WikipediaWorkflow(),
    "amazon.com": AmazonWorkflow(),
    "amazon.in": AmazonWorkflow(),
    "flipkart.com": FlipkartWorkflow(),
    "linkedin.com": LinkedInWorkflow(),
    "instagram.com": InstagramWorkflow(),
    "facebook.com": FacebookWorkflow(),
    "x.com": XWorkflow(),
    "twitter.com": XWorkflow(),
    "reddit.com": RedditWorkflow(),
    "chatgpt.com": ChatGPTWorkflow()
}

def get_workflow_for_domain(domain_or_title: str):
    """Selects the correct website workflow automatically based on current domain or window title."""
    if not domain_or_title:
        return None

    target = domain_or_title.strip().lower()
    for domain, workflow in WORKFLOW_REGISTRY.items():
        if domain in target or workflow.can_handle(target):
            return workflow
    return None

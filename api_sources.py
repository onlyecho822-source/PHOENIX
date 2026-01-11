"""
API Sources Configuration
Defines the 20 critical APIs to monitor and their verification sources
"""

from typing import Dict, List

# Critical APIs to monitor
API_SOURCES = {
    "stripe": {
        "name": "Stripe API",
        "endpoint": "https://api.stripe.com/v1/charges",
        "method": "HEAD",
        "headers": {"Authorization": "Bearer sk_test_placeholder"},
        "timeout": 10,
        "success_codes": [200, 401],  # 401 means API is up, just needs valid key
        "verification_sources": [
            {
                "type": "official_status",
                "url": "https://status.stripe.com",
                "method": "scrape",
                "selector": ".component-status"
            },
            {
                "type": "third_party",
                "url": "https://www.isitdownrightnow.com/stripe.com.html",
                "method": "scrape",
                "selector": ".domain-status"
            }
        ]
    },
    
    "openai": {
        "name": "OpenAI API",
        "endpoint": "https://api.openai.com/v1/models",
        "method": "GET",
        "headers": {"Authorization": "Bearer sk-placeholder"},
        "timeout": 10,
        "success_codes": [200, 401],
        "verification_sources": [
            {
                "type": "official_status",
                "url": "https://status.openai.com",
                "method": "scrape",
                "selector": ".component-status"
            }
        ]
    },
    
    "github": {
        "name": "GitHub API",
        "endpoint": "https://api.github.com",
        "method": "GET",
        "headers": {},
        "timeout": 10,
        "success_codes": [200],
        "verification_sources": [
            {
                "type": "official_status",
                "url": "https://www.githubstatus.com",
                "method": "scrape",
                "selector": ".component-status"
            }
        ]
    },
    
    "aws": {
        "name": "AWS Status",
        "endpoint": "https://status.aws.amazon.com",
        "method": "GET",
        "headers": {},
        "timeout": 10,
        "success_codes": [200],
        "verification_sources": [
            {
                "type": "official_status",
                "url": "https://status.aws.amazon.com",
                "method": "scrape",
                "selector": ".RSS"
            }
        ]
    },
    
    "vercel": {
        "name": "Vercel Status",
        "endpoint": "https://api.vercel.com/v2/user",
        "method": "GET",
        "headers": {},
        "timeout": 10,
        "success_codes": [200, 401],
        "verification_sources": [
            {
                "type": "official_status",
                "url": "https://www.vercel-status.com",
                "method": "scrape",
                "selector": ".component-status"
            }
        ]
    },
    
    "cloudflare": {
        "name": "Cloudflare Status",
        "endpoint": "https://api.cloudflare.com/client/v4/user",
        "method": "GET",
        "headers": {},
        "timeout": 10,
        "success_codes": [200, 400, 401],
        "verification_sources": [
            {
                "type": "official_status",
                "url": "https://www.cloudflarestatus.com",
                "method": "scrape",
                "selector": ".component-status"
            }
        ]
    },
    
    "binance": {
        "name": "Binance API",
        "endpoint": "https://api.binance.com/api/v3/ping",
        "method": "GET",
        "headers": {},
        "timeout": 10,
        "success_codes": [200],
        "verification_sources": [
            {
                "type": "official_status",
                "url": "https://www.binance.com/en/support/announcement",
                "method": "scrape",
                "selector": ".status"
            }
        ]
    },
    
    "coingecko": {
        "name": "CoinGecko API",
        "endpoint": "https://api.coingecko.com/api/v3/ping",
        "method": "GET",
        "headers": {},
        "timeout": 10,
        "success_codes": [200],
        "verification_sources": [
            {
                "type": "third_party",
                "url": "https://www.isitdownrightnow.com/coingecko.com.html",
                "method": "scrape",
                "selector": ".domain-status"
            }
        ]
    },
    
    "alphavantage": {
        "name": "Alpha Vantage API",
        "endpoint": "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey=demo",
        "method": "GET",
        "headers": {},
        "timeout": 10,
        "success_codes": [200],
        "verification_sources": []
    },
    
    "iexcloud": {
        "name": "IEX Cloud API",
        "endpoint": "https://cloud.iexapis.com/stable/stock/aapl/quote?token=pk_placeholder",
        "method": "GET",
        "headers": {},
        "timeout": 10,
        "success_codes": [200, 401],
        "verification_sources": [
            {
                "type": "official_status",
                "url": "https://status.iexcloud.io",
                "method": "scrape",
                "selector": ".component-status"
            }
        ]
    },
    
    "finnhub": {
        "name": "Finnhub API",
        "endpoint": "https://finnhub.io/api/v1/quote?symbol=AAPL&token=placeholder",
        "method": "GET",
        "headers": {},
        "timeout": 10,
        "success_codes": [200, 401],
        "verification_sources": []
    },
    
    "twitter": {
        "name": "Twitter/X API",
        "endpoint": "https://api.twitter.com/2/tweets/20",
        "method": "GET",
        "headers": {"Authorization": "Bearer placeholder"},
        "timeout": 10,
        "success_codes": [200, 401],
        "verification_sources": [
            {
                "type": "official_status",
                "url": "https://api.twitterstat.us",
                "method": "scrape",
                "selector": ".component-status"
            }
        ]
    },
    
    "reddit": {
        "name": "Reddit API",
        "endpoint": "https://www.reddit.com/.json",
        "method": "GET",
        "headers": {},
        "timeout": 10,
        "success_codes": [200],
        "verification_sources": [
            {
                "type": "official_status",
                "url": "https://www.redditstatus.com",
                "method": "scrape",
                "selector": ".component-status"
            }
        ]
    },
    
    "google_cloud": {
        "name": "Google Cloud Status",
        "endpoint": "https://status.cloud.google.com",
        "method": "GET",
        "headers": {},
        "timeout": 10,
        "success_codes": [200],
        "verification_sources": [
            {
                "type": "official_status",
                "url": "https://status.cloud.google.com",
                "method": "scrape",
                "selector": ".service-status"
            }
        ]
    },
    
    "azure": {
        "name": "Azure Status",
        "endpoint": "https://status.azure.com/en-us/status",
        "method": "GET",
        "headers": {},
        "timeout": 10,
        "success_codes": [200],
        "verification_sources": [
            {
                "type": "official_status",
                "url": "https://status.azure.com/en-us/status",
                "method": "scrape",
                "selector": ".status"
            }
        ]
    },
    
    "heroku": {
        "name": "Heroku Status",
        "endpoint": "https://api.heroku.com/apps",
        "method": "GET",
        "headers": {"Accept": "application/vnd.heroku+json; version=3"},
        "timeout": 10,
        "success_codes": [200, 401],
        "verification_sources": [
            {
                "type": "official_status",
                "url": "https://status.heroku.com",
                "method": "scrape",
                "selector": ".component-status"
            }
        ]
    },
    
    "railway": {
        "name": "Railway Status",
        "endpoint": "https://backboard.railway.app/graphql/v2",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "timeout": 10,
        "success_codes": [200, 400],
        "verification_sources": [
            {
                "type": "official_status",
                "url": "https://railway.statuspage.io",
                "method": "scrape",
                "selector": ".component-status"
            }
        ]
    },
    
    "render": {
        "name": "Render Status",
        "endpoint": "https://api.render.com/v1/services",
        "method": "GET",
        "headers": {},
        "timeout": 10,
        "success_codes": [200, 401],
        "verification_sources": [
            {
                "type": "official_status",
                "url": "https://render.statuspage.io",
                "method": "scrape",
                "selector": ".component-status"
            }
        ]
    },
    
    "supabase": {
        "name": "Supabase Status",
        "endpoint": "https://api.supabase.com",
        "method": "GET",
        "headers": {},
        "timeout": 10,
        "success_codes": [200, 404],
        "verification_sources": [
            {
                "type": "official_status",
                "url": "https://status.supabase.com",
                "method": "scrape",
                "selector": ".component-status"
            }
        ]
    },
    
    "planetscale": {
        "name": "PlanetScale Status",
        "endpoint": "https://api.planetscale.com/v1/organizations",
        "method": "GET",
        "headers": {},
        "timeout": 10,
        "success_codes": [200, 401],
        "verification_sources": [
            {
                "type": "official_status",
                "url": "https://www.planetscalestatus.com",
                "method": "scrape",
                "selector": ".component-status"
            }
        ]
    }
}


def get_api_config(api_name: str) -> Dict:
    """Get configuration for a specific API"""
    return API_SOURCES.get(api_name, {})


def get_all_apis() -> List[str]:
    """Get list of all monitored API names"""
    return list(API_SOURCES.keys())


def get_priority_apis() -> List[str]:
    """Get high-priority APIs to check more frequently"""
    # Check these every 5 minutes
    return ["stripe", "openai", "github", "aws", "vercel", "cloudflare"]


def get_standard_apis() -> List[str]:
    """Get standard priority APIs (check hourly)"""
    all_apis = set(get_all_apis())
    priority = set(get_priority_apis())
    return list(all_apis - priority)

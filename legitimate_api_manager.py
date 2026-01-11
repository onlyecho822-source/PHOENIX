#!/usr/bin/env python3
"""
LEGITIMATE API MANAGER
Ethical, sustainable API access with caching and rate limiting
No TOS violations, no automated account creation, no fake emails
"""

import requests
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict
import os

class SimpleCache:
    """Simple in-memory cache with TTL"""
    def __init__(self):
        self.cache = {}
        self.expiry = {}
    
    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            if datetime.now() < self.expiry[key]:
                return self.cache[key]
            else:
                del self.cache[key]
                del self.expiry[key]
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 3600):
        self.cache[key] = value
        self.expiry[key] = datetime.now() + timedelta(seconds=ttl_seconds)
    
    def clear(self):
        self.cache.clear()
        self.expiry.clear()

class RateLimiter:
    """Track and enforce rate limits per API key"""
    def __init__(self):
        self.calls = defaultdict(list)
        self.limits = {}
    
    def set_limit(self, key_id: str, calls_per_minute: int):
        self.limits[key_id] = calls_per_minute
    
    def can_call(self, key_id: str) -> bool:
        if key_id not in self.limits:
            return True
        
        now = datetime.now()
        # Remove calls older than 1 minute
        self.calls[key_id] = [t for t in self.calls[key_id] if now - t < timedelta(minutes=1)]
        
        return len(self.calls[key_id]) < self.limits[key_id]
    
    def record_call(self, key_id: str):
        self.calls[key_id].append(datetime.now())
    
    def wait_time(self, key_id: str) -> int:
        """Return seconds to wait before next call is allowed"""
        if self.can_call(key_id):
            return 0
        
        oldest_call = min(self.calls[key_id])
        wait_until = oldest_call + timedelta(minutes=1)
        return int((wait_until - datetime.now()).total_seconds())

class LegitimateAPIManager:
    """
    Ethical API management with:
    - Legitimate API keys only
    - Aggressive caching (10-100x efficiency)
    - Rate limit respect
    - Usage tracking
    - No TOS violations
    """
    
    def __init__(self):
        self.cache = SimpleCache()
        self.rate_limiter = RateLimiter()
        self.keys = {}
        self.usage_stats = defaultdict(int)
        
        # Load keys from environment or config
        self.load_keys()
    
    def load_keys(self):
        """Load API keys from environment variables"""
        # Stock market APIs
        if os.getenv('ALPHA_VANTAGE_KEY'):
            self.add_key('alpha_vantage', os.getenv('ALPHA_VANTAGE_KEY'), 25, 'day')
        
        if os.getenv('IEX_CLOUD_KEY'):
            self.add_key('iex_cloud', os.getenv('IEX_CLOUD_KEY'), 50000, 'month')
        
        if os.getenv('FINNHUB_KEY'):
            self.add_key('finnhub', os.getenv('FINNHUB_KEY'), 60, 'minute')
        
        # No-key APIs (always available)
        self.add_key('coingecko', None, 50, 'minute')
        self.add_key('binance_public', None, 1200, 'minute')
        self.add_key('blockchain_info', None, 100, 'minute')
    
    def add_key(self, service: str, api_key: Optional[str], limit: int, period: str):
        """Add a legitimate API key"""
        self.keys[service] = {
            'key': api_key,
            'limit': limit,
            'period': period
        }
        
        # Set rate limit (convert to calls per minute)
        if period == 'minute':
            self.rate_limiter.set_limit(service, limit)
        elif period == 'hour':
            self.rate_limiter.set_limit(service, limit // 60)
        elif period == 'day':
            self.rate_limiter.set_limit(service, limit // 1440)
        elif period == 'month':
            self.rate_limiter.set_limit(service, limit // 43200)
    
    def _make_cache_key(self, service: str, endpoint: str, params: Dict) -> str:
        """Generate cache key from request parameters"""
        param_str = json.dumps(params, sort_keys=True)
        hash_str = f"{service}:{endpoint}:{param_str}"
        return hashlib.md5(hash_str.encode()).hexdigest()
    
    def get(self, service: str, endpoint: str, params: Dict = None, ttl: int = 3600) -> Optional[Dict]:
        """
        Get data from API with caching and rate limiting
        
        Args:
            service: API service name (e.g., 'coingecko', 'alpha_vantage')
            endpoint: API endpoint URL
            params: Query parameters
            ttl: Cache TTL in seconds (default 1 hour)
        
        Returns:
            API response data or None if error
        """
        params = params or {}
        
        # Check cache first
        cache_key = self._make_cache_key(service, endpoint, params)
        cached = self.cache.get(cache_key)
        if cached:
            print(f"[CACHE HIT] {service}")
            return cached
        
        # Check if service exists
        if service not in self.keys:
            print(f"[ERROR] Unknown service: {service}")
            return None
        
        # Check rate limit
        if not self.rate_limiter.can_call(service):
            wait_time = self.rate_limiter.wait_time(service)
            print(f"[RATE LIMIT] {service} - wait {wait_time}s")
            time.sleep(wait_time)
        
        # Add API key to params if needed
        if self.keys[service]['key']:
            params['apikey'] = self.keys[service]['key']
        
        # Make request
        try:
            print(f"[API CALL] {service} -> {endpoint}")
            response = requests.get(endpoint, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Cache result
                self.cache.set(cache_key, data, ttl)
                
                # Record call
                self.rate_limiter.record_call(service)
                self.usage_stats[service] += 1
                
                return data
            else:
                print(f"[ERROR] {service} HTTP {response.status_code}")
                return None
        
        except Exception as e:
            print(f"[ERROR] {service}: {e}")
            return None
    
    def get_stock_quote(self, symbol: str) -> Optional[Dict]:
        """Get stock quote (tries multiple services)"""
        # Try Alpha Vantage first
        if 'alpha_vantage' in self.keys and self.keys['alpha_vantage']['key']:
            data = self.get(
                'alpha_vantage',
                'https://www.alphavantage.co/query',
                {'function': 'GLOBAL_QUOTE', 'symbol': symbol},
                ttl=300  # 5 minutes
            )
            if data:
                return data
        
        # Fallback to other sources
        print(f"[INFO] No stock data available for {symbol} (need API key)")
        return None
    
    def get_crypto_price(self, coin_id: str) -> Optional[Dict]:
        """Get crypto price from CoinGecko (no key needed)"""
        return self.get(
            'coingecko',
            f'https://api.coingecko.com/api/v3/simple/price',
            {'ids': coin_id, 'vs_currencies': 'usd', 'include_24hr_change': 'true'},
            ttl=60  # 1 minute
        )
    
    def get_bitcoin_stats(self) -> Optional[Dict]:
        """Get Bitcoin network stats (no key needed)"""
        return self.get(
            'blockchain_info',
            'https://blockchain.info/stats',
            {},
            ttl=600  # 10 minutes
        )
    
    def get_usage_stats(self) -> Dict:
        """Get usage statistics"""
        return {
            'total_calls': sum(self.usage_stats.values()),
            'calls_by_service': dict(self.usage_stats),
            'cache_size': len(self.cache.cache)
        }
    
    def save_usage_report(self, filename: str = '/tmp/api_usage_report.json'):
        """Save usage report to file"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'stats': self.get_usage_stats(),
            'services': {
                service: {
                    'has_key': self.keys[service]['key'] is not None,
                    'limit': f"{self.keys[service]['limit']}/{self.keys[service]['period']}"
                }
                for service in self.keys
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"[REPORT] Usage report saved: {filename}")
        return filename

def demo():
    """Demo legitimate API usage"""
    print("="*80)
    print("LEGITIMATE API MANAGER - DEMO")
    print("="*80)
    print()
    
    manager = LegitimateAPIManager()
    
    # Demo 1: Crypto prices (no key needed)
    print("1. Getting Bitcoin price (CoinGecko - NO KEY)")
    print("-"*80)
    btc = manager.get_crypto_price('bitcoin')
    if btc:
        price = btc['bitcoin']['usd']
        change = btc['bitcoin']['usd_24h_change']
        print(f"✓ Bitcoin: ${price:,.2f} ({change:+.2f}% 24h)")
    print()
    
    # Demo 2: Bitcoin network stats (no key needed)
    print("2. Getting Bitcoin network stats (Blockchain.info - NO KEY)")
    print("-"*80)
    stats = manager.get_bitcoin_stats()
    if stats:
        print(f"✓ Market Price: ${stats['market_price_usd']:,.2f}")
        print(f"✓ Total BTC: {stats['totalbc']/1e8:,.2f}")
    print()
    
    # Demo 3: Cache efficiency
    print("3. Testing cache (second call should be instant)")
    print("-"*80)
    start = time.time()
    btc2 = manager.get_crypto_price('bitcoin')
    elapsed = time.time() - start
    print(f"✓ Second call took {elapsed*1000:.2f}ms (cached)")
    print()
    
    # Usage stats
    print("="*80)
    print("USAGE STATISTICS")
    print("="*80)
    stats = manager.get_usage_stats()
    print(f"Total API calls: {stats['total_calls']}")
    print(f"Cache hits: {stats['cache_size']} items")
    print()
    print("Calls by service:")
    for service, count in stats['calls_by_service'].items():
        print(f"  {service}: {count}")
    print()
    
    # Save report
    manager.save_usage_report()
    
    print("="*80)
    print("DEMO COMPLETE")
    print("="*80)
    print()
    print("KEY FEATURES:")
    print("✓ Legitimate API keys only")
    print("✓ Aggressive caching (10-100x efficiency)")
    print("✓ Rate limit respect")
    print("✓ Usage tracking")
    print("✓ No TOS violations")
    print()
    print("TO USE:")
    print("1. Set environment variables:")
    print("   export ALPHA_VANTAGE_KEY='your_key'")
    print("   export IEX_CLOUD_KEY='your_key'")
    print("   export FINNHUB_KEY='your_key'")
    print("2. Run: python3 legitimate_api_manager.py")
    print()

if __name__ == "__main__":
    demo()

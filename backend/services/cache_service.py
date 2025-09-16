import redis
import json
import hashlib
from datetime import datetime, timedelta

class CacheService:
    def __init__(self):
        try:
            self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            self.redis_available = True
        except:
            self.redis_available = False
            self.memory_cache = {}
    
    def get(self, key):
        if self.redis_available:
            try:
                data = self.redis_client.get(key)
                return json.loads(data) if data else None #type: ignore #VSCode_Hint
            except:
                return None
        else:
            return self.memory_cache.get(key)
    
    def set(self, key, value, ttl_seconds=3600):
        if self.redis_available:
            try:
                self.redis_client.setex(key, ttl_seconds, json.dumps(value))
            except:
                pass
        else:
            # Memory cache with expiration
            expiry = datetime.now() + timedelta(seconds=ttl_seconds)
            self.memory_cache[key] = {
                'data': value,
                'expires': expiry
            }
    
    def generate_key(self, server, endpoint, *args):
        """Genera una clave única para el cache"""
        key_data = f"{server}:{endpoint}:{':'.join(str(arg) for arg in args)}"
        return hashlib.md5(key_data.encode()).hexdigest()
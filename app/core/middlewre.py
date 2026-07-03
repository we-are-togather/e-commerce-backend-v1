from fastapi import  FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict
from typing import Dict, Tuple

app = FastAPI()

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.clients: Dict[str, Tuple[int, float]] = defaultdict(lambda: (0, time.time()))

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        request_count, last_request_time = self.clients[client_ip]

        current_time = time.time()
        if current_time - last_request_time > self.window_seconds:
            # Reset the count and timestamp if the window has passed
            request_count = 0
            last_request_time = current_time

        if request_count >= self.max_requests:
            return Response(content="Too Many Requests", status_code=429)

        # Update the count and timestamp for the client
        self.clients[client_ip] = (request_count + 1, last_request_time)
        
        # add custom header to response
        custom_headers = {"X-RateLimit-Limit": str(self.max_requests), "X-RateLimit-Remaining": str(self.max_requests - request_count - 1)}
        for header, value in custom_headers.items():
            response.headers.append(header, value)
        
        response = await call_next(request)
        return response

app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)



# from fastapi import FastAPI, Request, Response
# from starlette.middleware.base import BaseHTTPMiddleware
# import time
# import redis

# app = FastAPI()


# class AdvancedRateLimiter(BaseHTTPMiddleware):
#     def __init__(
#         self,
#         app: FastAPI,
#         redis_host="localhost",
#         redis_port=6379,

#         # Sliding Window
#         window_size=60,
#         max_requests=100,

#         # Token Bucket
#         bucket_capacity=50,
#         refill_rate=1,  # tokens per second

#         # Leaky Bucket
#         leak_rate=1  # requests per second
#     ):
#         super().__init__(app)

#         self.redis = redis.Redis(
#             host=redis_host,
#             port=redis_port,
#             decode_responses=True
#         )

#         self.window_size = window_size
#         self.max_requests = max_requests

#         self.bucket_capacity = bucket_capacity
#         self.refill_rate = refill_rate

#         self.leak_rate = leak_rate

#     # -----------------------------
#     # Identity key (IMPORTANT)
#     # -----------------------------
#     def get_client_key(self, request: Request):
#         user_id = request.headers.get("x-user-id")
#         session_id = request.cookies.get("session_id")
#         ip = request.headers.get("x-forwarded-for", request.client.host)

#         return f"rl:{user_id or session_id or ip}"

#     # -----------------------------
#     # Sliding Window
#     # -----------------------------
#     def sliding_window_check(self, key):
#         now = int(time.time())
#         window = now // self.window_size

#         redis_key = f"{key}:sw:{window}"

#         count = self.redis.incr(redis_key)
#         if count == 1:
#             self.redis.expire(redis_key, self.window_size)

#         return count <= self.max_requests

#     # -----------------------------
#     # Token Bucket
#     # -----------------------------
#     def token_bucket_check(self, key):
#         bucket_key = f"{key}:tb"

#         data = self.redis.hgetall(bucket_key)

#         tokens = float(data.get("tokens", self.bucket_capacity))
#         last = float(data.get("last", time.time()))

#         now = time.time()
#         delta = now - last

#         # refill tokens
#         tokens = min(
#             self.bucket_capacity,
#             tokens + delta * self.refill_rate
#         )

#         if tokens < 1:
#             return False

#         tokens -= 1

#         self.redis.hset(bucket_key, mapping={
#             "tokens": tokens,
#             "last": now
#         })

#         return True

#     # -----------------------------
#     # Leaky Bucket
#     # -----------------------------
#     def leaky_bucket_check(self, key):
#         bucket_key = f"{key}:lb"

#         data = self.redis.hgetall(bucket_key)

#         queue = int(data.get("queue", 0))
#         last = float(data.get("last", time.time()))

#         now = time.time()

#         leaked = int((now - last) * self.leak_rate)
#         queue = max(0, queue - leaked)

#         if queue >= self.bucket_capacity:
#             return False

#         queue += 1

#         self.redis.hset(bucket_key, mapping={
#             "queue": queue,
#             "last": now
#         })

#         return True

#     # -----------------------------
#     # Middleware
#     # -----------------------------
#     async def dispatch(self, request: Request, call_next):
#         key = self.get_client_key(request)

#         # 1. Sliding window check
#         if not self.sliding_window_check(key):
#             return Response(
#                 content="Too Many Requests (Sliding Window)",
#                 status_code=429
#             )

#         # 2. Token bucket check
#         if not self.token_bucket_check(key):
#             return Response(
#                 content="Too Many Requests (Token Bucket)",
#                 status_code=429
#             )

#         # 3. Leaky bucket check
#         if not self.leaky_bucket_check(key):
#             return Response(
#                 content="Too Many Requests (Leaky Bucket)",
#                 status_code=429
#             )

#         # Proceed request
#         response = await call_next(request)

#         # Optional headers
#         response.headers["X-RateLimit-Policy"] = "sliding+token+leaky"

#         return response


# app.add_middleware(
#     AdvancedRateLimiter,
#     max_requests=100,
#     window_size=60,
#     bucket_capacity=50,
#     refill_rate=1,
#     leak_rate=1
# )
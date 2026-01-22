# metrics.py
from prometheus_client import Counter, Gauge, generate_latest

# 1. TOKENS GENERATED (Input vs Output)
TOKENS_GENERATED = Counter(
    'tokens_generated_total',
    'Total tokens processed',
    ['token_type', 'model_name']  # token_type: 'input' or 'output'
)

# 2. GPU MEMORY USAGE (Optional - requires NVIDIA GPU)
GPU_MEMORY_USAGE = Gauge(
    'gpu_memory_usage_bytes',
    'GPU memory usage in bytes',
    ['gpu_index']
)

# 3. GUARDRAIL REJECTIONS
GUARDRAIL_REJECTIONS = Counter(
    'guardrail_rejections_total',
    'Total requests rejected by guardrails',
    ['guardrail_type', 'model_name']
)

# 4. REQUEST QUEUE SIZE
REQUEST_QUEUE_SIZE = Gauge(
    'request_queue_size',
    'Current number of requests waiting',
    ['model_name']
)

# 5. MODEL LOAD STATUS
MODEL_LOAD_STATUS = Gauge(
    'model_load_status',
    'Model load status (1=loaded, 0=error)',
    ['model_name']
)

# Additional useful metrics
REQUEST_DURATION = Gauge(
    'request_duration_seconds',
    'Request processing time',
    ['model_name', 'status']
)

ACTIVE_REQUESTS = Gauge(
    'active_requests',
    'Currently processing requests',
    ['model_name']
)

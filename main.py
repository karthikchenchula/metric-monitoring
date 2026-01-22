# app/main.py
from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import Response
import time
import asyncio

from metrics import (
    TOKENS_GENERATED, GPU_MEMORY_USAGE, GUARDRAIL_REJECTIONS,
    REQUEST_QUEUE_SIZE, MODEL_LOAD_STATUS, REQUEST_DURATION,
    ACTIVE_REQUESTS, generate_latest
)
from model_client import ModelClient
from guardrails import GuardrailSystem

app = FastAPI()
model_client = ModelClient(model_name="mistral")
guardrails = GuardrailSystem()

# Background task to update metrics
async def update_metrics_background():
    """Periodically update dynamic metrics"""
    while True:
        # Update queue size
        REQUEST_QUEUE_SIZE.labels(
            model_name=model_client.model_name
        ).set(len(model_client.request_queue))
        
        # Update active requests
        ACTIVE_REQUESTS.labels(
            model_name=model_client.model_name
        ).set(model_client.active_requests)
        
        # Update GPU metrics
        model_client.update_gpu_metrics()
        
        await asyncio.sleep(5)  # Update every 5 seconds

@app.on_event("startup")
async def startup():
    """Initialize on startup"""
    # Start background metrics updater
    asyncio.create_task(update_metrics_background())
    
    # Load model and set status
    try:
        await model_client.load_model()
        model_client.set_model_status(True)
    except:
        model_client.set_model_status(False)
        raise

@app.post("/v1/generate")
async def generate(request: Request):
    """Main generation endpoint with full metrics"""
    start_time = time.time()
    
    # 1. Check guardrails
    data = await request.json()
    prompt = data.get("prompt", "")
    
    if not guardrails.check_input(prompt, model_client.model_name):
        REQUEST_DURATION.labels(
            model_name=model_client.model_name,
            status="rejected"
        ).set(time.time() - start_time)
        return {"error": "Request rejected by guardrails"}
    
    # 2. Process request
    try:
        # Add to queue
        model_client.request_queue.append(request)
        
        # Generate response
        response = await model_client.generate(prompt)
        
        # Record success duration
        duration = time.time() - start_time
        REQUEST_DURATION.labels(
            model_name=model_client.model_name,
            status="success"
        ).set(duration)
        
        # Remove from queue
        if request in model_client.request_queue:
            model_client.request_queue.remove(request)
        
        return response
        
    except Exception as e:
        # Record error duration
        duration = time.time() - start_time
        REQUEST_DURATION.labels(
            model_name=model_client.model_name,
            status="error"
        ).set(duration)
        
        # Clean up queue
        if request in model_client.request_queue:
            model_client.request_queue.remove(request)
        
        return {"error": str(e)}

@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint - SAP Monitoring reads this"""
    # Force update before returning
    model_client.update_gpu_metrics()
    REQUEST_QUEUE_SIZE.labels(
        model_name=model_client.model_name
    ).set(len(model_client.request_queue))
    
    return Response(
        generate_latest(),
        media_type="text/plain"
    )

@app.get("/health")
async def health_check():
    """Health check for SAP AI Core"""
    is_healthy = await model_client.is_ready()
    model_client.set_model_status(is_healthy)
    
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "model_loaded": is_healthy
    }

# model_client.py
import time
import asyncio
from typing import Dict, Any
from metrics import TOKENS_GENERATED, MODEL_LOAD_STATUS, GPU_MEMORY_USAGE

class ModelClient:
    def __init__(self, model_name="llama2"):
        self.model_name = model_name
        self.request_queue = []
        self.active_requests = 0
        self.model_loaded = False
        
        # Initialize GPU monitoring if available
        self.gpu_available = False
        self.pynvml = None
        self._init_gpu_monitoring()
    
    def _init_gpu_monitoring(self):
        """Initialize GPU metrics if NVIDIA GPU is present"""
        try:
            import pynvml
            pynvml.nvmlInit()
            self.pynvml = pynvml
            self.gpu_available = True
            print(f"GPU monitoring enabled: {pynvml.nvmlDeviceGetCount()} GPUs")
        except:
            print("GPU monitoring not available")
            self.gpu_available = False
    
    def update_gpu_metrics(self):
        """Update GPU memory usage metrics"""
        if not self.gpu_available or not self.pynvml:
            return
            
        try:
            device_count = self.pynvml.nvmlDeviceGetCount()
            for i in range(device_count):
                handle = self.pynvml.nvmlDeviceGetHandleByIndex(i)
                mem_info = self.pynvml.nvmlDeviceGetMemoryInfo(handle)
                GPU_MEMORY_USAGE.labels(gpu_index=str(i)).set(mem_info.used)
        except:
            pass
    
    async def load_model(self):
        """Load the model"""
        try:
            print(f"Loading model: {self.model_name}")
            await asyncio.sleep(0.1)
            self.model_loaded = True
            print(f"Model {self.model_name} loaded successfully")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model_loaded = False
            raise
    
    async def is_ready(self) -> bool:
        """Check if model is ready to serve requests"""
        return self.model_loaded
    
    async def _call_model(self, prompt: str) -> Dict[str, Any]:
        """
        Call the actual model (STUB IMPLEMENTATION - REPLACE THIS)
        
        WARNING: This is placeholder code for testing!
        The 'output_tokens = input_tokens * 2' is NOT real logic.
        
        To connect to your actual AI model:
        
        FOR OLLAMA:
        ------------
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'http://localhost:11434/api/generate',
                json={'model': self.model_name, 'prompt': prompt, 'stream': False}
            ) as resp:
                result = await resp.json()
                return {
                    'text': result['response'],
                    'input_tokens': result.get('prompt_eval_count', 0),  # Real count
                    'output_tokens': result.get('eval_count', 0),        # Real count
                    'model': self.model_name
                }
        
        FOR vLLM:
        ---------
        from vllm import LLM, SamplingParams
        # In __init__: self.llm = LLM(model=self.model_name)
        outputs = self.llm.generate([prompt], SamplingParams(temperature=0.7))
        output = outputs[0]
        return {
            'text': output.outputs[0].text,
            'input_tokens': len(output.prompt_token_ids),      # Real count
            'output_tokens': len(output.outputs[0].token_ids), # Real count
            'model': self.model_name
        }
        """
        # STUB CODE - Replace with real model call above
        input_tokens = len(prompt.split())
        output_tokens = input_tokens * 2  # FAKE: Just for testing
        await asyncio.sleep(0.1)
        
        return {
            'text': f"Generated response for: {prompt[:50]}...",
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'model': self.model_name
        }
    
    async def generate(self, prompt: str):
        """Generate response with metrics tracking"""
        start_time = time.time()
        self.active_requests += 1
        
        try:
            # Your existing generation logic
            response = await self._call_model(prompt)
            
            # TRACK TOKENS
            if 'input_tokens' in response:
                TOKENS_GENERATED.labels(
                    token_type='input',
                    model_name=self.model_name
                ).inc(response['input_tokens'])
            
            if 'output_tokens' in response:
                TOKENS_GENERATED.labels(
                    token_type='output',
                    model_name=self.model_name
                ).inc(response['output_tokens'])
            
            # UPDATE GPU METRICS
            self.update_gpu_metrics()
            
            return response
            
        finally:
            self.active_requests -= 1
    
    def set_model_status(self, is_loaded: bool):
        """Update model load status metric"""
        status_value = 1 if is_loaded else 0
        MODEL_LOAD_STATUS.labels(model_name=self.model_name).set(status_value)
        self.model_loaded = is_loaded

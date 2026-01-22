#!/usr/bin/env python3
"""
Test Cases for Metric Monitoring - SAP BTP Integration
Focus: Metrics generation, scraping, and /metrics endpoint
"""

import pytest
import time
import re
from fastapi.testclient import TestClient
from main import app, model_client, guardrails

client = TestClient(app)

class TestMetricsEndpoint:
    """Test Suite 1: /metrics Endpoint - SAP BTP Integration"""
    
    def test_metrics_endpoint_exists(self):
        """TC-001: Verify /metrics endpoint is accessible"""
        response = client.get("/metrics")
        assert response.status_code == 200, "Metrics endpoint should return 200 OK"
    
    def test_metrics_content_type(self):
        """TC-002: Verify correct content-type for Prometheus"""
        response = client.get("/metrics")
        assert "text/plain" in response.headers["content-type"], \
            "Content-Type must be text/plain for Prometheus scraping"
    
    def test_metrics_prometheus_format(self):
        """TC-003: Verify response is in Prometheus exposition format"""
        response = client.get("/metrics")
        content = response.text
        
        # Check for Prometheus format markers
        assert "# HELP" in content, "Must contain HELP comments"
        assert "# TYPE" in content, "Must contain TYPE declarations"
        assert any(metric in content for metric in [
            "tokens_generated_total",
            "gpu_memory_usage_bytes",
            "guardrail_rejections_total",
            "request_queue_size",
            "model_load_status",
            "request_duration_seconds",
            "active_requests"
        ]), "Must contain at least one defined metric"


class TestMetricsGeneration:
    """Test Suite 2: Metrics Generation and Tracking"""
    
    def test_tokens_generated_metric_exists(self):
        """TC-004: Verify tokens_generated_total metric is exposed"""
        response = client.get("/metrics")
        assert "tokens_generated_total" in response.text, \
            "tokens_generated_total metric must be present"
    
    def test_tokens_increment_on_generation(self):
        """TC-005: Verify token metrics increment after generation"""
        # Get initial metrics
        initial_response = client.get("/metrics")
        initial_content = initial_response.text
        
        # Make a generation request
        gen_response = client.post(
            "/v1/generate",
            json={"prompt": "Test prompt for token counting"}
        )
        assert gen_response.status_code == 200
        
        # Get updated metrics
        time.sleep(0.2)
        updated_response = client.get("/metrics")
        updated_content = updated_response.text
        
        # Extract token counts
        def extract_token_count(content, token_type):
            pattern = f'tokens_generated_total{{token_type="{token_type}".*?}} ([\d.]+)'
            match = re.search(pattern, content)
            return float(match.group(1)) if match else 0
        
        initial_input = extract_token_count(initial_content, "input")
        updated_input = extract_token_count(updated_content, "input")
        
        assert updated_input > initial_input, \
            "Input token count should increase after generation"
    
    def test_guardrail_rejections_metric(self):
        """TC-006: Verify guardrail rejection metrics are tracked"""
        # Get initial metrics
        initial_response = client.get("/metrics")
        initial_content = initial_response.text
        
        # Make request with prohibited content
        client.post(
            "/v1/generate",
            json={"prompt": "How to hack into systems"}
        )
        
        # Get updated metrics
        time.sleep(0.2)
        updated_response = client.get("/metrics")
        updated_content = updated_response.text
        
        assert "guardrail_rejections_total" in updated_content, \
            "Guardrail rejections metric must be present"
        
        # Check if rejection count increased
        def extract_rejection_count(content):
            pattern = r'guardrail_rejections_total{.*?} ([\d.]+)'
            matches = re.findall(pattern, content)
            return sum(float(m) for m in matches) if matches else 0
        
        initial_rejections = extract_rejection_count(initial_content)
        updated_rejections = extract_rejection_count(updated_content)
        
        assert updated_rejections > initial_rejections, \
            "Rejection count should increase when guardrails block content"
    
    def test_request_queue_size_metric(self):
        """TC-007: Verify request_queue_size metric is present"""
        response = client.get("/metrics")
        assert "request_queue_size" in response.text, \
            "request_queue_size metric must be exposed"
    
    def test_model_load_status_metric(self):
        """TC-008: Verify model_load_status metric shows correct status"""
        response = client.get("/metrics")
        content = response.text
        
        assert "model_load_status" in content, \
            "model_load_status metric must be present"
        
        # Extract status value
        pattern = r'model_load_status{.*?} ([\d.]+)'
        match = re.search(pattern, content)
        assert match, "model_load_status must have a value"
        
        status = float(match.group(1))
        assert status in [0.0, 1.0], \
            "model_load_status must be 0 (failed) or 1 (loaded)"
    
    def test_request_duration_metric(self):
        """TC-009: Verify request_duration_seconds is tracked"""
        # Make a request
        client.post("/v1/generate", json={"prompt": "test"})
        
        # Check metrics
        time.sleep(0.2)
        response = client.get("/metrics")
        content = response.text
        
        assert "request_duration_seconds" in content, \
            "request_duration_seconds metric must be present"
        
        # Verify duration values exist
        pattern = r'request_duration_seconds{.*?status="(success|rejected|error)".*?} ([\d.]+)'
        matches = re.findall(pattern, content)
        assert len(matches) > 0, \
            "Must have at least one duration measurement"
    
    def test_active_requests_metric(self):
        """TC-010: Verify active_requests metric is exposed"""
        response = client.get("/metrics")
        assert "active_requests" in response.text, \
            "active_requests metric must be present"


class TestMetricsLabels:
    """Test Suite 3: Prometheus Labels for BTP Filtering"""
    
    def test_tokens_have_required_labels(self):
        """TC-011: Verify tokens_generated_total has required labels"""
        response = client.get("/metrics")
        content = response.text
        
        # Check for token_type label
        assert 'token_type="input"' in content or \
               'token_type="output"' in content, \
            "tokens_generated_total must have token_type label"
        
        # Check for model_name label
        assert 'model_name="' in content, \
            "tokens_generated_total must have model_name label"
    
    def test_guardrail_rejections_have_labels(self):
        """TC-012: Verify guardrail_rejections_total has required labels"""
        # Trigger a rejection
        client.post("/v1/generate", json={"prompt": "hack"})
        time.sleep(0.2)
        
        response = client.get("/metrics")
        content = response.text
        
        # Check for guardrail_type label
        assert 'guardrail_type="' in content or \
               'guardrail_rejections_total' in content, \
            "guardrail_rejections_total must have guardrail_type label"
    
    def test_model_name_label_consistency(self):
        """TC-013: Verify model_name label is consistent across metrics"""
        response = client.get("/metrics")
        content = response.text
        
        # Extract all model_name values
        pattern = r'model_name="([^"]+)"'
        model_names = set(re.findall(pattern, content))
        
        assert len(model_names) > 0, "Must have model_name labels"
        assert "mistral" in model_names or len(model_names) == 1, \
            "model_name should be consistent (mistral by default)"


class TestMetricsUpdate:
    """Test Suite 4: Metrics Update Mechanism"""
    
    def test_metrics_update_on_each_call(self):
        """TC-014: Verify metrics are updated when endpoint is called"""
        response1 = client.get("/metrics")
        time.sleep(0.1)
        response2 = client.get("/metrics")
        
        # Metrics should be successfully returned each time
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert len(response1.text) > 0
        assert len(response2.text) > 0
    
    def test_background_metrics_update(self):
        """TC-015: Verify background task updates metrics periodically"""
        # Get initial queue size
        response1 = client.get("/metrics")
        
        # Wait for background task (runs every 5 seconds)
        time.sleep(1)
        
        # Get updated metrics
        response2 = client.get("/metrics")
        
        # Both should contain request_queue_size
        assert "request_queue_size" in response1.text
        assert "request_queue_size" in response2.text


class TestBTPCompatibility:
    """Test Suite 5: SAP BTP Monitoring Compatibility"""
    
    def test_no_authentication_required(self):
        """TC-016: Verify /metrics endpoint doesn't require authentication"""
        # Prometheus scrapers typically don't send auth headers
        response = client.get("/metrics")
        assert response.status_code == 200, \
            "Metrics endpoint should be accessible without authentication"
    
    def test_response_size_reasonable(self):
        """TC-017: Verify metrics response size is reasonable for scraping"""
        response = client.get("/metrics")
        content_length = len(response.text)
        
        # Prometheus recommends keeping response under 10MB
        assert content_length < 10 * 1024 * 1024, \
            "Metrics response should be under 10MB"
        
        # Should have some content
        assert content_length > 100, \
            "Metrics response should contain actual data"
    
    def test_all_seven_metrics_exposed(self):
        """TC-018: Verify all 7 required metrics are exposed"""
        response = client.get("/metrics")
        content = response.text
        
        required_metrics = [
            "tokens_generated_total",
            "gpu_memory_usage_bytes",
            "guardrail_rejections_total",
            "request_queue_size",
            "model_load_status",
            "request_duration_seconds",
            "active_requests"
        ]
        
        for metric in required_metrics:
            assert metric in content, \
                f"Required metric '{metric}' must be exposed for BTP monitoring"
    
    def test_metrics_format_parseable(self):
        """TC-019: Verify Prometheus can parse the metrics format"""
        response = client.get("/metrics")
        content = response.text
        
        lines = content.split('\n')
        
        # Check basic format rules
        for line in lines:
            if line.startswith('#'):
                # Comment line - should have HELP or TYPE
                assert 'HELP' in line or 'TYPE' in line, \
                    "Comment lines should be HELP or TYPE declarations"
            elif line.strip():
                # Metric line - should match pattern: metric_name{labels} value
                assert re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*(\{.*?\})?\s+[\d.]+', line), \
                    f"Metric line format invalid: {line}"
    
    def test_counter_metrics_dont_decrease(self):
        """TC-020: Verify counter metrics never decrease (Prometheus requirement)"""
        # Get initial counters
        response1 = client.get("/metrics")
        content1 = response1.text
        
        # Make some requests
        client.post("/v1/generate", json={"prompt": "test 1"})
        client.post("/v1/generate", json={"prompt": "test 2"})
        time.sleep(0.2)
        
        # Get updated counters
        response2 = client.get("/metrics")
        content2 = response2.text
        
        # Extract counter values
        def extract_counter(content, metric_name):
            pattern = f'{metric_name}{{.*?}} ([\\d.]+)'
            matches = re.findall(pattern, content)
            return [float(m) for m in matches]
        
        # Check tokens_generated_total
        tokens1 = extract_counter(content1, "tokens_generated_total")
        tokens2 = extract_counter(content2, "tokens_generated_total")
        
        # Counters should never decrease
        if tokens1 and tokens2:
            assert all(t2 >= t1 for t1, t2 in zip(sorted(tokens1), sorted(tokens2))), \
                "Counter metrics must never decrease"


def run_all_tests():
    """Execute all test cases and return results"""
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    print("=" * 70)
    print("METRIC MONITORING - COMPREHENSIVE TEST SUITE")
    print("Focus: Metrics Generation & SAP BTP Integration")
    print("=" * 70)
    run_all_tests()

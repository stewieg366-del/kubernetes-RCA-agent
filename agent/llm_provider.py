import os
import json
import time
from tenacity import retry, stop_after_attempt, wait_exponential_jitter, retry_if_exception
from langchain_google_genai import ChatGoogleGenerativeAI

GEMINI_MIN_CALL_INTERVAL_SECONDS = float(os.environ.get("GEMINI_MIN_CALL_INTERVAL_SECONDS", "12"))

LAST_LLM_CALL_TIME = 0.0

def enforce_llm_rate_limit():
    global LAST_LLM_CALL_TIME
    now = time.time()
    elapsed = now - LAST_LLM_CALL_TIME
    if elapsed < GEMINI_MIN_CALL_INTERVAL_SECONDS:
        time.sleep(GEMINI_MIN_CALL_INTERVAL_SECONDS - elapsed)
    LAST_LLM_CALL_TIME = time.time()

def is_transient_error(exception):
    err_str = str(exception).lower()
    transient_keywords = ["429", "503", "500", "resourceexhausted", "quota", "rate limit", "timeout", "service unavailable"]
    return any(kw in err_str for kw in transient_keywords)

class MockLLM:
    """A mock LLM for local deterministic testing."""
    def invoke(self, messages):
        content = json.dumps({
            "action": "CONCLUDE", "reasoning": "Mocking conclusion", "tool_calls": [],
            "hypotheses_updates": [], "observed_facts_updates": ["Mock fact"], "uncertainties": [], "alternative_explanations": [],
            "root_cause": "Mock root cause due to offline test", "confidence": 0.5
        })
        class MockMsg:
            def __init__(self, c): self.content = c
        return MockMsg(content)

class GeminiModelProvider:
    def __init__(self, use_mock=False):
        self.use_mock = use_mock
        if self.use_mock:
            self.primary_llm = MockLLM()
            self.fallback_llm = None
            return

        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing. Cannot use real Gemini model.")
        
        self.primary_model_name = os.environ.get("GEMINI_PRIMARY_MODEL", "gemini-3.6-flash")
        self.fallback_model_name = os.environ.get("GEMINI_FALLBACK_MODEL", "gemini-3.5-flash")

        self.primary_llm = ChatGoogleGenerativeAI(
            model=self.primary_model_name,
            temperature=0.0,
            max_retries=0, # Let tenacity handle retries
            api_key=api_key
        )
        
        self.fallback_llm = ChatGoogleGenerativeAI(
            model=self.fallback_model_name,
            temperature=0.0,
            max_retries=0,
            api_key=api_key
        )

    def invoke_with_fallback(self, messages):
        if self.use_mock:
            return self.primary_llm.invoke(messages), {"model": "mock-llm", "fallback_info": None}
            
        try:
            res = self._invoke_primary(messages)
            return res, {"model": self.primary_model_name, "fallback_info": None}
        except Exception as e:
            if is_transient_error(e):
                # Fallback logic
                safe_err_str = str(e)
                api_key = os.environ.get("GEMINI_API_KEY")
                if api_key and api_key in safe_err_str:
                    safe_err_str = safe_err_str.replace(api_key, "[REDACTED_API_KEY]")
                
                res = self._invoke_fallback(messages)
                fallback_info = f"Primary model: {self.primary_model_name}\nFallback: {self.fallback_model_name}\nReason: temporary rate limit / service unavailable ({safe_err_str})"
                return res, {"model": self.fallback_model_name, "fallback_info": fallback_info}
            else:
                raise

    @retry(
        stop=stop_after_attempt(3), 
        wait=wait_exponential_jitter(initial=2, max=20),
        retry=retry_if_exception(is_transient_error),
        reraise=True
    )
    def _invoke_primary(self, messages):
        enforce_llm_rate_limit()
        try:
            res = self.primary_llm.invoke(messages)
            global LAST_LLM_CALL_TIME
            LAST_LLM_CALL_TIME = time.time()
            return res
        except Exception as e:
            LAST_LLM_CALL_TIME = time.time()
            raise

    @retry(
        stop=stop_after_attempt(3), 
        wait=wait_exponential_jitter(initial=2, max=20),
        retry=retry_if_exception(is_transient_error),
        reraise=True
    )
    def _invoke_fallback(self, messages):
        enforce_llm_rate_limit()
        try:
            res = self.fallback_llm.invoke(messages)
            global LAST_LLM_CALL_TIME
            LAST_LLM_CALL_TIME = time.time()
            return res
        except Exception as e:
            LAST_LLM_CALL_TIME = time.time()
            raise

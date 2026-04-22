import time
import random
from utils.schema import validate_schema

def run_with_retry(func, schema, agent_name, max_retries, base_delay, *args, repair_hint=None, **kwargs):
    last_err = None
    for attempt in range(max_retries + 1):
        try:
            result = func(*args, **kwargs)
            validate_schema(result, schema, agent_name)
            return result
        except Exception as e:
            last_err = e
            print(f"⚠️ {agent_name} Attempt {attempt+1} failed: {e}")
            
            if attempt < max_retries:
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                if any(k in str(e).lower() for k in ["503", "rate", "quota"]):
                    delay *= 2
                time.sleep(delay)
            else:
                raise last_err
"""Bounded, local-only Ollama client for an 8 GB Windows computer."""
import json
import os
import re
import socket
import urllib.error
import urllib.request

ENDPOINT = "http://127.0.0.1:11434"
PRIMARY = "llama3.2:3b"
FALLBACK = "llama3.2:1b"

class LocalAIError(RuntimeError):
    pass

def _clean_json(value):
    if isinstance(value, dict):
        return value
    if not isinstance(value, str):
        raise LocalAIError("Model did not return an object")
    try:
        result = json.loads(value)
    except ValueError:
        match = re.search(r"\{.*\}", value, flags=re.S)
        if not match:
            raise LocalAIError("No JSON object in model response")
        try: result = json.loads(match.group())
        except ValueError as exc: raise LocalAIError("Invalid JSON from model") from exc
    if not isinstance(result, dict):
        raise LocalAIError("Expected a JSON object")
    return result

def generate_json(prompt, *, model=PRIMARY, timeout=None):
    if model not in (PRIMARY, FALLBACK):
        raise ValueError("Only the configured local Ollama models are allowed")
    timeout = float(timeout or os.environ.get("ARA_OLLAMA_TIMEOUT", "180"))
    timeout = max(10, min(300, timeout))
    payload = json.dumps({"model":model,"prompt":prompt[:10000],"stream":False,"format":"json", "options":{"num_ctx":2048,"num_predict":650,"temperature":0.2},"keep_alive":"2m"}).encode("utf-8")
    request = urllib.request.Request(ENDPOINT+"/api/generate",data=payload,headers={"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw=response.read(160000)
        return _clean_json(json.loads(raw).get("response", ""))
    except (TimeoutError, socket.timeout) as exc:
        raise LocalAIError("Ollama timed out. Try the 1B fallback model or close other large programs.") from exc
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise LocalAIError("Ollama unavailable or response invalid: "+str(exc)) from exc

def query_with_fallback(prompt):
    errors=[]
    for model in (PRIMARY,FALLBACK):
        try: return generate_json(prompt,model=model),model
        except LocalAIError as exc: errors.append(f"{model}: {exc}")
    raise LocalAIError("; ".join(errors))

def clean_strings(data, limit=15):
    if not isinstance(data,list): return []
    values=[]
    for value in data[:40]:
        if not isinstance(value,str):continue
        value=' '.join(value.split())[:95]
        if 2 <= len(value) <= 95 and value.casefold() not in [v.casefold() for v in values]: values.append(value)
        if len(values)>=limit:break
    return values

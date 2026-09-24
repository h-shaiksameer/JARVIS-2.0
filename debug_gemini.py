import importlib.util
import os

print('HAS_GOOGLE', importlib.util.find_spec('google') is not None)
print('HAS_GOOGLE_GENAI', importlib.util.find_spec('google.genai') is not None)
print('HAS_GOOGLE_GENERATIVEAI', importlib.util.find_spec('google.generativeai') is not None)
print('API_KEY_SET', bool(os.getenv('API_KEY')))

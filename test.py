from litellm import completion

response = completion(
    model="ollama/hf.co/elyza/Llama-3-ELYZA-JP-8B-GGUF", 
    messages=[{ "content": "transformerについて解説して","role": "user"}], 
    api_base="http://localhost:11434"
)
print(response)


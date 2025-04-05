import ollama

def query_llm(prompt, model_name="mistral"):
    # Use the ollama package to query the specified LLM model
    response = ollama.run(model=model_name, messages=[{"role": "user", "content": prompt}])
    return response

if __name__ == "__main__":
    prompt = "Explain what Agent AI is in simple words."
    response = query_llm(prompt)
    print("LLM Response:")
    print(response)

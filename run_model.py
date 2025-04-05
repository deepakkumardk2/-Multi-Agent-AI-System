import ollama

# Define the model name (using a lightweight model like "mistral")
model_name = "mistral"

# Define the user input prompt
prompt = "Explain what Agent AI is in simple words."

# Run the model using the appropriate function (assuming it's 'chat')
response = ollama.chat(model=model_name, messages=[{"role": "user", "content": prompt}])

# Print the response (this should be free of any database results)
print("AI Response:", response)

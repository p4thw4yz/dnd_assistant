import requests
import pandas as pd
import re
import json

LOG_FILE = "openrouter.log"

def extract_size(description):
    """Extract model size in billions from description (e.g., '671B parameters')."""
    match = re.search(r'(\d+(\.\d+)?)\s*(B|billion)\s*(parameter|params|param)?', description, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return None
    
class OpenRouterInterface:
    def __init__(self, api_key, system_prompt):
        """Initialize the wrapper with an API key, system prompt, and fetch free models into a DataFrame."""
        self.api_key = api_key
        self.system_prompt = system_prompt
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.free_models = self.get_free_models()
        if self.free_models.empty:
            print("Warning: No free models available at initialization.")
        
        print(f"Initialized OpenRouter Interface with prompt '{system_prompt}'.")

    def set_system_prompt(self, prompt: str):
        """Update the system prompt for the interface."""
        self.system_prompt = prompt
        print(f"Updated system prompt to: '{prompt}'")
        
    def get_free_models(self):
        """Fetch free models and return a DataFrame with name, id, size, and free status."""
        try:
            response = requests.get(f"{self.base_url}/models", headers=self.headers)
            response.raise_for_status()
            models = response.json().get("data", [])
            model_data = []
            for model in models:
                prompt_price = model["pricing"]["prompt"]
                completion_price = model["pricing"]["completion"]
                is_free = prompt_price == "0" and completion_price == "0"
                name = model["name"]
                model_id = model["id"]
                size = extract_size(model['description'])
                model_data.append({
                    "name": name,
                    "id": model_id,
                    "size": size,
                    "free": is_free
                })
            models_df = pd.DataFrame(model_data)
            free_models_df = models_df[models_df["free"]].sort_values(by="size", ascending=False, na_position='last')
            return free_models_df
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch models: {e}")
            return pd.DataFrame()

    def send_input(self, prompt: str, context: str = "") -> str:
        """Send a prompt and optional context to OpenRouter and return the response string."""
        try:
            messages = []
            if self.system_prompt:
                messages.append({"role": "system", "content": self.system_prompt})
            if context:
                messages.append({"role": "system", "content": context})
            messages.append({"role": "user", "content": prompt})

            if self.free_models.empty:
                return "Error: No free models available"
            
            model_id = self.free_models.iloc[0]['id']
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": model_id,
                    "messages": messages
                }
            )
            response.raise_for_status()
            
            with open(LOG_FILE, "a") as log_file:
                log_file.write(f"Model: {model_id}\n")
                log_file.write(f"Input: {prompt}\n")
                if context:
                    log_file.write(f"Context: {context}\n")
                log_file.write(f"Output: {response.json()['choices'][0]['message']['content']}\n")
                log_file.write("-" * 40 + "\n")
            
            content = json.loads(response.content)
            return content['choices'][0]['message']['content']
        except Exception as e:
            return f"Error: {e}"


# Interactive session
if __name__ == "__main__":
    api_key = "API_KEY" # ADD OpenRouter API Key
    system_prompt = "You think you are a pirate. Answer all question like a Pirate." # Add System Prompt as required
    wrapper = OpenRouterInterface(api_key, system_prompt)

    if wrapper.free_models.empty:
        print("No free models available. Exiting.")
        exit(1)

    print("Welcome to the OpenRouter interactive session!")
    print("Available free models:")
    for index, row in wrapper.free_models.iterrows():
        size_str = f"{row['size']}B" if pd.notna(row['size']) else "Unknown size"
        print(f"- {row['name']} ({size_str})")
    print("\nType your prompt and press Enter to get a response.")
    print("To provide context, use 'context||prompt'. Otherwise, just type the prompt.")
    print("Type 'exit' to quit.")
    print("Type 'list models' to see the current list of available models.")

    while True:
        user_input = input("You (context||prompt): ")
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        elif user_input.lower() == 'list models':
            print("Current free models:")
            for index, row in wrapper.free_models.iterrows():
                size_str = f"{row['size']}B" if pd.notna(row['size']) else "Unknown size"
                print(f"- {row['name']} ({size_str})")
        else:
            parts = user_input.split("||", 1)
            if len(parts) == 2:
                context, prompt = parts
            else:
                context, prompt = None, user_input
            response = wrapper.send_input(prompt, context)
            if response:
                print(f"Assistant: {response}")
            else:
                print("An error occurred or no models are available. Please try again.")
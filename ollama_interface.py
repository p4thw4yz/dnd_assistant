import ollama

class OllamaInterface:
    def __init__(self, model_name: str, ai_prompt: str = ""):
        """Initialize the OllamaInterface with a specific model name and optional AI prompt."""
        self.model_name = model_name
        self.client = ollama.Client()
        self.ai_prompt = ai_prompt
        print(f"Initialized OllamaInterface with model '{model_name}'.")
        print(f"Initialized OllamaInterface with prompt '{ai_prompt}'.")

    def set_system_prompt(self, prompt: str):
        """Update the system prompt for the interface."""
        self.ai_prompt = prompt
        print(f"Updated system prompt to: '{prompt}'")
        
    def send_input(self, prompt: str, context: str = "") -> str:
        """Send a prompt and optional context to the Ollama model and return the response."""
        try:
            messages = []
            if self.ai_prompt:
                messages.append({'role': 'system', 'content': self.ai_prompt})
            if context:
                messages.append({'role': 'system', 'content': context})
            messages.append({'role': 'user', 'content': prompt})
            
            response = self.client.chat(model=self.model_name, messages=messages)
            return response['message']['content']
        except Exception as e:
            return f"Error: {e}"

    def run_interactive(self):
        """Start an interactive session where the user can input text and receive responses from the model."""
        print("Starting interactive session. Type 'exit' to quit.")
        context = input("Enter additional context (or press Enter to skip): ")
        while True:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                print("Exiting interactive session.")
                break
            print(f"Ollama: {self.send_input(user_input, context)}")

# Example usage:
# handler = OllamaInterface('your-model-name', ai_prompt='You are a helpful assistant.')
# handler.run_interactive()

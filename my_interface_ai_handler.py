# interface_ai_handler.py
print("Loaded NEW interface_ai_handler.py with OpenAI integration!")


from openai import OpenAI, APIError

class InterfaceAI:
    def __init__(self, api_key, model, endpoint):
        self.client = OpenAI(
            api_key=api_key,
            base_url=endpoint
        )
        self.model = model

    def chat(self, prompt, system_message=None):
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        # Prompt can be str or list; handle both
        if isinstance(prompt, list):
            messages.extend(prompt)
        else:
            messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=300,
            )
            return response.choices[0].message.content
        except APIError as e:
            return f"[Error in interface AI]: {str(e)}"
        except Exception as e:
            return f"[Error in interface AI]: {str(e)}"

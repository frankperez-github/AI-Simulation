from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

class PLN_Model:
    def __init__(self, model_name: str):
        self.model = ChatGoogleGenerativeAI(model=model_name)
        self.prompt_template = PromptTemplate(input_variables=["input"], template="{input}")

    def get_response(self, prompt):
        try:
            # Format the prompt explicitly
            formatted_prompt = self.prompt_template.format(input=prompt)
            # Use invoke and access .content directly
            response = self.model.invoke(formatted_prompt)
            return response.content  # Access content attribute directly

        except Exception as e:
            return f"Error: {str(e)}"

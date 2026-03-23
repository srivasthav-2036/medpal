from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

def get_chat_response(query: str) -> str:
    template = """
    Based on the user query {query}, give him a proper diet plan.
    Include the food items which he/she has to consume along with the nutritional value.
    Explain in detail why these foods have to be consumed. Explain the benefits.
    Also provide any lifestyle related advice if asked in the query.
    """

    
    prompt_template = PromptTemplate(
        template=template,
        input_variables=["query"]
    )

    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.7
    )

    
    chain = prompt_template | llm

    
    res = chain.invoke({"query": query})

    response_text = res.content if hasattr(res, "content") else str(res)

    return response_text




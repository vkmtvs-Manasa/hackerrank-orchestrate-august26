# # import pandas as pd

# # from context.context_builder import ContextBuilder
# # from retrieval.evidence_retriever import EvidenceRetriever

# # # Load one sample message
# # messages = pd.read_csv("data/messages_features.csv")

# # # Take the first message
# # message_row = messages.iloc[0]

# # # Retrieve evidence
# # retriever = EvidenceRetriever()
# # evidence = retriever.retrieve(message_row)

# # # Build context
# # builder = ContextBuilder()
# # context = builder.build_context(message_row, evidence)

# # # Print results
# # print(context.keys())
# # print(context["evidence_summary"])
# from pathlib import Path

# import pandas as pd

# from context.context_builder import ContextBuilder
# from retrieval.evidence_retriever import EvidenceRetriever

# # Path to code directory
# code_dir = Path(__file__).resolve().parent

# # Load sample messages
# messages = pd.read_csv(code_dir / "data" / "messages_features.csv")

# # Take first message
# message_row = messages.iloc[0]

# # Retrieve evidence
# retriever = EvidenceRetriever()
# evidence = retriever.retrieve(message_row)

# # Build context
# builder = ContextBuilder()
# context = builder.build_context(message_row, evidence)

# print(context.keys())
# print(context["evidence_summary"])

# from google import genai
# from dotenv import load_dotenv
# import os

# load_dotenv()

# client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# response = client.models.generate_content(
#     model="gemini-3.5-flash",
#     contents="Hello"
# )

# print(response.text)

from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("Groq_API_KEY"))

response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[
        {"role": "user", "content": "Say Hello"}
    ]
)

print(response.choices[0].message.content)
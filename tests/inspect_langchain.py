
import langchain
import os
print(f"LangChain file: {langchain.__file__}")
print(f"LangChain version: {langchain.__version__}")
print(f"LangChain dir: {dir(langchain)}")

try:
    import langchain.memory
    print("Imported langchain.memory")
except ImportError as e:
    print(f"Failed to import memory: {e}")

try:
    from langchain.memory import ConversationBufferMemory
    print("Success: ConversationBufferMemory")
except Exception as e:
    print(f"Failed ConversationBufferMemory: {e}")

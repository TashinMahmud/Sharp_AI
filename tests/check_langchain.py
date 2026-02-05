
try:
    import langchain
    print(f"LangChain version: {langchain.__version__}")
    from langchain.memory import ConversationBufferMemory
    print("Successfully imported ConversationBufferMemory")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")

from dotenv import load_dotenv
import os

load_dotenv()

print("DeepSeek API Key:", os.getenv("DEEPSEEK_API_KEY"))

import subprocess
import sys
import os


os.chdir(os.path.dirname(os.path.abspath(__file__)))


print("📦 Step 1: Installing dependencies...")
result = subprocess.run(
    [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"],
    cwd=os.path.dirname(os.path.abspath(__file__))
)
if result.returncode != 0:
    print("❌ Failed to install dependencies. Check your internet connection.")
    sys.exit(1)
print("   ✅ Done!\n")


env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if not os.path.exists(env_path):
    print("   ❌ .env file not found!")
  
 
    print("   DATABASE_URL=postgresql+psycopg://postgres:yourpassword@localhost:5432/civicmind")
    sys.exit(1)

from dotenv import load_dotenv
load_dotenv(env_path)




subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])

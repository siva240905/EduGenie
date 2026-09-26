import sys
import os

# Add root project path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mangum import Mangum
from app import app

# Serverless handler for Netlify Functions
handler = Mangum(app, lifespan="off")

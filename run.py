import os
import sys

# Add the src directory to Python path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.append(src_path)

# Import and run the main CLI
from main import cli

if __name__ == "__main__":
    cli()
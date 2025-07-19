import subprocess
import sys
import os

def main():
    # Get Poetry's Python path
    result = subprocess.run(['poetry', 'env', 'info', '--path'], 
                          capture_output=True, 
                          text=True)
    poetry_env_path = result.stdout.strip()
    python_path = os.path.join(poetry_env_path, 'bin', 'python')

    # Run uvicorn using Poetry's Python
    cmd = [
        python_path,
        '-m',
        'uvicorn',
        'tech_challenge_02.main:app',
        '--reload',
        '--port',
        '8000'
    ]
    
    process = subprocess.run(cmd)
    sys.exit(process.returncode)

if __name__ == '__main__':
    main() 
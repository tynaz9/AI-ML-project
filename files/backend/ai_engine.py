import requests
import json

def get_response_from_ollama(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "tinyllama", "prompt": prompt},
            stream=True
        )

        output = ""
        buffer = ""

        for line in response.iter_lines():
            if line:
                decoded = line.decode('utf-8')
                buffer += decoded.strip()

                try:
                    # Try to load a valid JSON line from the accumulated buffer
                    json_data = json.loads(buffer)
                    output += json_data.get('response', '')
                    buffer = ""  # Reset after success
                except json.JSONDecodeError:
                    continue  # Keep buffering until it's valid JSON

        return output.strip() if output.strip() else "No meaningful response returned."

    except requests.exceptions.ConnectionError:
        return "Could not connect to Ollama. Is it running?"

    except Exception as e:
        return f"Error talking to Ollama: {str(e)}"

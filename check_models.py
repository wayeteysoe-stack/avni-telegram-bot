from google import genai

client = genai.Client(api_key="AQ.Ab8RN6KtwOTo4-XBvEisgVxt_69rJ2HkHMV7Gk6wyMIkvrCe8A")

try:
    for model in client.models.list():
        print(model.name)
except Exception as e:
    print(e)
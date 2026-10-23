from dotenv import load_dotenv
import anthropic

load_dotenv()                    # reads .env and makes ANTHROPIC_API_KEY available
client = anthropic.Anthropic()   # finds the key 

response = client.messages.create(
    model="claude-haiku-5-5",    # which model to use
    max_tokens=50,               # upper limit on the length of the reply
    messages=[
        {"role": "user", "content": "Reply with just the word: connected"}
    ],
)

print(response.content[0].text)  # the reply text
print(response.usage)            # tokens used
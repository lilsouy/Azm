from openai import OpenAI

client = OpenAI(
    api_key="sk-oAlqOh_ZKXokKIJ08lt9Pw",  
    base_url="https://elmodels.ngrok.app/v1"
)

def ask_nuha(prompt, use_streaming=True):
    response = client.chat.completions.create(
        model="nuha-2.0",
        messages=[{"role": "user", "content": prompt}],
        stream=use_streaming
    )
    if use_streaming:
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                print(content, end="", flush=True)
        print()
    else:
        print(response.choices[0].message.content)

ask_nuha("كيف حالك؟", use_streaming=True)
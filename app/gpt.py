import openai


def generate_prompt(prompt):
# Set up your OpenAI API key
    openai.api_key = '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'

    
    # Generate response
    response = openai.Completion.create(
        engine='gpt-3.5-turbo-instruct',
        prompt=prompt,
        max_tokens=400,
        temperature=0.7,
    )

    # Extract the generated text from the response
    generated_text = response.choices[0].text.strip()

    # Print the generated text
    
    return generated_text
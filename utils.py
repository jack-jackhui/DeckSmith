def clean_response(response):
    # Extract the 'response' field if it's a dictionary
    if isinstance(response, dict):
        response = response.get('response', '')

    # Ensure response is a string
    if not isinstance(response, str):
       response = str(response)

    # Remove unwanted characters
    response = response.replace("{", "").replace("}", "").replace("\"", "")

    # Remove special characters and unnecessary line breaks
    response = response.replace("\n\n", "\n")
    response = response.replace("•", "-")
    response = response.replace("➢", "-")
    response = response.replace("  ", " ")
    response = response.replace("{", "").replace("}", "").replace("\"", "")

    # Add Markdown formatting
    lines = response.split("\n")
    formatted_lines = []
    for line in lines:
        if line.startswith("-"):
            formatted_lines.append(f"- {line[1:].strip()}")
        else:
            formatted_lines.append(line)

    return "\n\n".join(formatted_lines)
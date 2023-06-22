import tiktoken

def _count_tokens(self,content, model="gpt-3.5-turbo-0301"):
    """
    Returns the number of tokens used by a list of messages.

    Args:
        content (str): The content of the message.
        model (str, optional): The name of the language model. Defaults to "gpt-3.5-turbo-0301".

    Returns:
        int: The number of tokens used by the messages.

    Raises:
        NotImplementedError: If the specified model is not implemented.
    """
    messages = [
        {
            "role": "user",
            "content": content,
        },
    ]
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        return self._count_tokens(messages, model="gpt-3.5-turbo-0301")
    elif model == "gpt-4":
        return self._count_tokens(messages, model="gpt-4-0314")
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  
        tokens_per_name = -1  
    elif model == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError("error")
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  
    return num_tokens


s = "s"
model = "gpt-3.5-turbo"
ans = _count_tokens(s,model)
print(ans)
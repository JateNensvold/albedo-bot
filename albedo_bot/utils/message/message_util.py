def wrap_message(message: str,
                 max_message_length: int = 2000,
                 wrapper: str = "",
                 header: str = ""):
    """
    Wrap a message string to be under the `max_message_length`

    Args:
        message (str): message getting wrapped
        max_message_length (int, optional): Maximum message length for a 
            message. Defaults to 2000.
        wrapper (str, optional): Wrapper text to put around each end of the
            message. Defaults to "".
        header (str, optional): A header to add to each message. Defaults to "".

    Returns:
        list[str]: a list of messages generated from wrapping `message`
    """
    max_message_length = max_message_length - len(wrapper) - len(header)
    message_list: list[str] = []
    message_itr_index = 0
    while message_itr_index < len(message):

        new_message = message[message_itr_index:message_itr_index +
                              max_message_length]
        newline_index = new_message.rfind("\n")

        if newline_index not in [0, -1] and (
                message_itr_index + len(new_message)) < len(message):
            new_message = message[message_itr_index:
                                  message_itr_index + newline_index+1]

        if wrapper != "":
            new_message = wrapper.format(
                new_message)
        message_list.append(f"{header}{new_message}")
        message_itr_index += len(new_message)
    return message_list

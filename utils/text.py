def word_wrap(input_string, max_length):
    input_string = input_string.encode("ascii", "ignore")
    input_string = input_string.decode()
    words = str(input_string).split()
    result = []
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + len(result) <= max_length:
            current_line += (word + " ")
        else:
            result.append(current_line.strip())
            current_line = (word + " ")

    if current_line:
        result.append(current_line.strip())

    return "\n".join(result)

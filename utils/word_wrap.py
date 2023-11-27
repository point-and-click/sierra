class WordWrap:

    @staticmethod
    def word_wrap(input_string, max_length):
        result = WordWrap.split_string_by_length(input_string, max_length)

        return "\n".join(result)

    @staticmethod
    def split_string_by_length(input_string, max_length):
        input_string = input_string.encode("ascii", "ignore")
        input_string = input_string.decode()
        words = input_string.split()
        lines = []
        current_line = ''

        for word in words:
            if len(current_line + word) <= max_length:
                current_line += word + ' '
            else:
                lines.append(current_line.rstrip())
                current_line = word + ' '

        if current_line:
            lines.append(current_line.rstrip())

        return lines

_set_graphics_mode = 'm'


def color(hex_value):
    return _control_sequence(
        f'38;2;{int(hex_value[0:2], 16)};{int(hex_value[2:4], 16)};{int(hex_value[4:6], 16)};20',
        _set_graphics_mode
    )


def reset():
    return _control_sequence('0', _set_graphics_mode)


def _control_sequence(numbers, mode):
    return f'\x1b[{numbers}{mode}'

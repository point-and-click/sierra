from windows.animation import Animation


class RotateAnimation(Animation):
    def __init__(self, animation_settings):
        super().__init__(animation_settings)
        self.angle_max = self._settings.angle_max

        self._amplitude_max = 0.00000001
        self._previous = 0

    def render(self, amplitude):
        _ = super().render(amplitude)
        if amplitude > self._amplitude_max:
            self._amplitude_max = amplitude

        target_angle = (amplitude / self._amplitude_max) * self.angle_max

        self._previous = max(-self.angle_max, min(self.angle_max, target_angle))

        return self._previous

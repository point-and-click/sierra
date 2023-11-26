import os

import pygame


class Animation:
    def __init__(self, name):
        self.name = name
        self.max_angle = 35
        self.max_rotation = 3
        self.max_amplitude = 1000
        self.prev_angle = 0
        self.image = None

    def animate_frame(self, amplitude, screen):
        if self.image is None:
            file_name = f"config/characters/images/{self.name}.png"
            if os.path.isfile(file_name):
                self.image = pygame.image.load(file_name).convert_alpha()
        if amplitude > self.max_amplitude:
            self.max_amplitude = amplitude

        scaled_amplitude = min(amplitude, self.max_amplitude) / self.max_amplitude
        target_angle = scaled_amplitude * self.max_angle
        target_rotation_amount = target_angle - self.prev_angle
        actual_rotation_amount = max(-self.max_rotation, min(self.max_rotation, target_rotation_amount))
        new_angle = max(-self.max_angle, min(self.max_angle, actual_rotation_amount + self.prev_angle))
        rotated_image = pygame.transform.rotate(self.image, new_angle)
        rotated_rect = rotated_image.get_rect(center=self.image.get_rect().center)
        self.prev_angle = new_angle

        pygame.event.get()
        screen.fill((0, 255, 0))
        screen.blit(rotated_image, rotated_rect)
        pygame.display.update()
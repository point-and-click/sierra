from datetime import timedelta


class Subtitles:
    def __init__(self, segments):
        self.segments = [SubtitleSegment(segment[0], segment[1], segment[2]) for segment in segments]

    def __repr__(self):
        return ' '.join([segment.text for segment in self.segments])

    def reconstitute(self, original_text):
        words = original_text.split()
        for segment in self.segments:
            new_text = []
            for word in segment.text.split():
                if words:
                    new_text.append(words.pop(0))
            segment.text = ' '.join(new_text)
        self.segments[-1].text += ' '.join(words)


class SubtitleSegment:
    def __init__(self, text, start, end):
        # Silence is handled weirdly by segments.
        self.text = text
        self.start = start
        self.end = end
        self.duration = self.end - self.start

    def complete(self, start_time, time):
        return start_time + timedelta(seconds=self.start) + timedelta(seconds=self.duration) <= time

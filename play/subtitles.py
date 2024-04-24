from datetime import timedelta

from utils.format import divide


class Subtitles:
    """
    Subtitles class to represent a subtitle file.
    :param timestamp: str
    """
    def __init__(self, timestamp):
        self.timestamp = timestamp
        self.path = None
        self.transcript = None
        self.segments = None

    def __repr__(self):
        return self.path

    def set(self, transcript):
        self.path = f'temp/{self.timestamp}.srt'
        self.transcript = transcript
        self.segments = [Segment(segment) for segment in self.transcript.get('segments')]
        self._save()

    def _save(self):
        with open(self.path, 'w') as subtitle_file:
            subtitle_file.write(str(self.transcript))

    def reconstitute(self, original_text):
        words = original_text.split()
        for segment in self.transcript.get('segments'):
            new_text = []
            for word in segment.get('text').split():
                if words:
                    new_text.append(words.pop(0))
            segment['text'] = ' '.join(new_text)
        self.transcript.get('segments')[-1]['text'] += ' '.join(words)
        self.segments = [Segment(segment) for segment in self.transcript.get('segments')]
        self._save()

    def __iter__(self):
        return iter(self.segments)


class Segment:
    def __init__(self, segment):
        # Silence is handled weirdly by segments.
        self.text = segment.get('text', '')
        self.start = segment.get('start', 0)
        self.end = segment.get('end', 0)
        self.duration = self.end - self.start

    def complete(self, start_time, time):
        return start_time + timedelta(seconds=self.start) + timedelta(seconds=self.duration) <= time


def transcript_from_text(text, time, segments):
    return {
        'text': text,
        'segments': [
            {
                'id': segment,
                'seek': segment,
                'text': divide(text, segments)[segment],
                'start': segment * (time / segments),
                'end': (segment + 1) * (time / segments)
            } for segment in range(segments)
        ]
    }

from yaml import safe_load


class SierraSettings:
    def __init__(self, file_name):
        with open(file_name, 'r') as file:
            yaml = safe_load(file)

        self.characters = yaml.get('characters')
        self.tasks = yaml.get('tasks')
        self.chat = self._ChatSettings(yaml.get('chat'))
        self.speech = self._SpeechSettings(yaml.get('speech'))
        self.transcribe = self._TranscribeSettings(yaml.get('transcribe'))
        self.visual = self._VisualSettings(yaml.get('visual'))
        self.history = self._HistorySettings(yaml.get('history'))
        self.summary = self._SummarySettings(yaml.get('summary'))

    class _ChatSettings:
        def __init__(self, chat_settings):
            self.model = chat_settings.get('model')
            self.module = chat_settings.get('module')

    class _SpeechSettings:
        def __init__(self, speech_settings):
            self.enabled = speech_settings.get('enabled')
            self.model = speech_settings.get('model')
            self.module = speech_settings.get('module')
            self.channels = speech_settings.get('channels')
            self.sample_rate = speech_settings.get('sample_rate')
            self.chunk_size = speech_settings.get('chunk_size')

    class _TranscribeSettings:
        def __init__(self, transcribe_settings):
            self.model = transcribe_settings.get('model')
            self.module = transcribe_settings.get('module')

    class _VisualSettings:
        def __init__(self, visual_settings):
            self.enabled = visual_settings.get('enabled')
            self.chroma_key = tuple([int(v) for v in visual_settings.get('chroma_key').split(',')])
            self.animation = self._AnimationSettings(visual_settings.get('animation'))
            self.subtitles = self._SubtitleSettings(visual_settings.get('subtitles'))

        class _AnimationSettings:
            def __init__(self, animation_settings):
                self.angle_max = animation_settings.get('angle_max')

        class _SubtitleSettings:
            def __init__(self, subtitle_settings):
                self.max = subtitle_settings.get('max')
                self.font = self._FontSettings(subtitle_settings.get('font'))

            class _FontSettings:
                def __init__(self, font_settings):
                    self.name = font_settings.get('name')
                    self.size = font_settings.get('size')
                    self.bold = font_settings.get('bold')

    class _HistorySettings:
        def __init__(self, history_settings):
            self.max = history_settings.get('max')

    class _SummarySettings:
        def __init__(self, summary_settings):
            self.user = summary_settings.get('user')
            self.assistant = summary_settings.get('assistant')
            self.max_words = summary_settings.get('max_words')
            self.review = summary_settings.get('review')


sierra_settings = SierraSettings('sierra.yaml')

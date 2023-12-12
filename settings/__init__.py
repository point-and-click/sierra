from yaml import safe_load


class SierraSettings:
    def __init__(self, file_name):
        with open(file_name, 'r') as file:
            yaml = safe_load(file)

        self.characters = yaml.get('characters')
        self.tasks = yaml.get('tasks')
        self.history = self._HistorySettings(yaml.get('history'))
        self.summary = self._SummarySettings(yaml.get('summary'))
        self.subtitles = self._SubtitleSettings(yaml.get('subtitles'))
        self.ui = self._UserInterfaceSettings(yaml.get('ui'))

    class _UserInterfaceSettings:
        def __init__(self, ui_settings):
            chroma_key = ui_settings.get('chroma_key')
            self.chroma_key = (
                chroma_key.get('r'),
                chroma_key.get('g'),
                chroma_key.get('b')
            )

    class _HistorySettings:
        def __init__(self, history_settings):
            self.max = history_settings.get('max')

    class _SummarySettings:
        def __init__(self, summary_settings):
            self.max_words = summary_settings.get('max_words')
            self.review = summary_settings.get('review')

    class _SubtitleSettings:
        def __init__(self, subtitle_settings):
            self.max = subtitle_settings.get('max')
            self.font = self._FontSettings(subtitle_settings.get('font'))

        class _FontSettings:
            def __init__(self, font_settings):
                self.name = font_settings.get('name')
                self.size = font_settings.get('size')
                self.bold = font_settings.get('bold')


sierra_settings = SierraSettings('sierra.yaml')

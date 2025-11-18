class ChoiceWidgetOptionDataMixin:
    def __init__(self, attrs=None, choices=(), option_data={}):
        self._option_data = option_data
        super().__init__(attrs, choices)

    @property
    def option_data(self):
        return self._option_data

    @option_data.setter
    def option_data(self, value):
        self._option_data = value

    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        if self._option_data:
            try:
                attrs.update(self._option_data.get(value))
            except Exception:
                raise Exception(
                    "option_data should be in a format of { value: { 'dat_key' : 'data_value' } }"
                )
        return super().create_option(
            name, value, label, selected, index, subindex=subindex, attrs=attrs
        )

from django import forms


class BootstrapFormMixin:
    """
    Applies consistent Bootstrap-friendly styling to Django forms.
    """

    input_class = "form-control"
    select_class = "form-select"
    checkbox_class = "form-check-input"
    textarea_class = "form-control"
    multiselect_class = "form-select"

    def apply_bootstrap(self):
        for name, field in self.fields.items():
            widget = field.widget

            if isinstance(widget, forms.CheckboxInput):
                css_class = self.checkbox_class
            elif isinstance(widget, forms.SelectMultiple):
                css_class = self.multiselect_class
            elif isinstance(widget, forms.Select):
                css_class = self.select_class
            elif isinstance(widget, forms.Textarea):
                css_class = self.textarea_class
                widget.attrs.setdefault("rows", 4)
            else:
                css_class = self.input_class

            current_classes = widget.attrs.get("class", "")
            widget.attrs["class"] = f"{current_classes} {css_class}".strip()

            if isinstance(widget, forms.DateInput):
                widget.attrs.setdefault("type", "date")

            if not isinstance(widget, (forms.CheckboxInput, forms.SelectMultiple)):
                widget.attrs.setdefault("placeholder", field.label)

            if field.required:
                widget.attrs.setdefault("required", True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()

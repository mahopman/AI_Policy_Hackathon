null_values = [None, "n/a", "none"]

class Attribute:

    def __init__(self, name, description, example_values):
        self.name = name
        self.description = description
        self.example_values = example_values
        self.previous_values = []
        self.value = ""

    def __str__(self):
        return self.observer_prompt + " " + self.value
    
    def get_observer_prompt(self):
        example_values_text = f" Example values: {', '.join(self.example_values)}" if self.example_values else ""
        previous_values_text = f" Previous values: {', '.join(self.previous_values)}" if self.example_values else ""
        return f'"{self.name}": [{self.description}{example_values_text}{previous_values_text}]'

    def set_value(self, value):
        if value is None:
            value = ""
        value = value.lower()
        if value in null_values:
            value = ""
        self.value = value
        self.previous_values.append(value)
    
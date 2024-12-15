null_values = [None, "n/a", "none"]

class Attribute:

    def __init__(self, name, description, possible_values):
        self.name = name
        self.description = description
        self.possible_values = possible_values
        values_text = f" Example values: {', '.join(self.possible_values)}" if self.possible_values else ""
        self.observer_prompt = f'"{self.name}": [{self.description}{values_text}]'
        
        self.value = ""

    def __str__(self):
        return self.observer_prompt + " " + self.value

    def set_value(self, value):
        if value is None:
            value = ""
        value = value.lower()
        if value in null_values:
            value = ""
        self.value = value
    
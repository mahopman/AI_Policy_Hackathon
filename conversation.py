import os

class Conversation:
    def __init__(self, filename = None):
        self.user_inputs = []
        self.assistant_responses = []
        if filename and os.path.exists(filename):
            self.load_from_file(filename)

    def add_user_input(self, user_input):
        self.user_inputs.append(user_input)

    def add_assistant_response(self, assistant_response):
        self.assistant_responses.append(assistant_response)

    def get_user_input(self, conversation_index):
        return self.user_inputs[conversation_index]
    
    def get_assistant_response(self, conversation_index):
        return self.assistant_responses[conversation_index]
    
    def get_conversation_at_step(self, step):
        full_conversation = ""
        for i in range(step):
            full_conversation += "USER: " + self.get_user_input(i) + "\n"
            full_conversation += "ASSISTANT: " + self.get_assistant_response(i) + "\n"
        return full_conversation 
    
    def save_to_file(self, filename):
        with open(filename, "w") as file:
            file.write(self.get_conversation_at_step(len(self.assistant_responses)))

    def load_from_file(self, filename):
        with open(filename, "r") as file:
            self.load_from_string(file.read())

    def load_from_string(self, string):
        lines = string.split('\n')
        current_speaker = None

        for line in lines:
            line = line.strip()
            if line.startswith("USER:"):
                current_speaker = "USER"
                self.user_inputs.append(line[5:].strip())
            elif line.startswith("ASSISTANT:"):
                current_speaker = "ASSISTANT"
                self.assistant_responses.append(line[10:].strip())
            elif current_speaker == "USER":
                self.user_inputs[-1] += f" {line.strip()}"
            elif current_speaker == "ASSISTANT":
                self.assistant_responses[-1] += f" {line.strip()}"
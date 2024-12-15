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
            lines = file.readlines()
            for line in lines:
                if line.startswith("USER"):
                    self.user_inputs.append(line[6:])
                elif line.startswith("ASSISTANT"):
                    self.assistant_responses.append(line[11:])

    def load_from_string(self, string):
        self.user_inputs = []
        self.assistant_responses = []
        for line in string.split("\n"):
            if line.startswith("USER"):
                self.user_inputs.append(line[6:])
            elif line.startswith("ASSISTANT"):
                self.assistant_responses.append(line[11:])

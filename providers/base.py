class BaseProvider:
    def __init__(self, name, prefix):
        self.name = name
        self.prefix = prefix

    @staticmethod
    def is_configured():
        return False

    def is_command(self, text):
        return text.startswith(self.prefix)

    def extract_command(self, text):
        # Removes the prefix and takes the first word as command
        return text[len(self.prefix):].split()[0].lower()

    def send_message(self, recipient, text):
        raise NotImplementedError
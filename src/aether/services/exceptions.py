class UnauthorizedSensorError(Exception):
    pass


class InvalidReadingError(Exception):
    def __init__(self, errors: list[str]):
        super().__init__("Invalid reading")
        self.errors = errors

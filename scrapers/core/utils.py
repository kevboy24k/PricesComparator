import logging


class utils:
    @staticmethod
    def report_error(message: str, *args) -> None:
        """Punto común de registro de validaciones de la ingesta Python."""
        logging.warning(message, *args)

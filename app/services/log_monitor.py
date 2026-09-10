import time
from pathlib import Path


class LogMonitor:

    def __init__(self, file_path, interval=1):

        self.file_path = Path(file_path)
        self.interval = interval
        self._running = False

    def start(self):
        """
        Continuously monitor a log file.

        Only newly appended lines are returned.
        Existing lines are ignored when monitoring starts.

        The file is opened and closed for each read cycle so that
        Windows can safely allow another process to append to the file.
        """

        # ----------------------------------------------------
        # Validate file path
        # ----------------------------------------------------

        if not self.file_path.exists():
            raise FileNotFoundError(
                f"Log file not found: {self.file_path}"
            )

        if not self.file_path.is_file():
            raise ValueError(
                f"Provided path is not a file: {self.file_path}"
            )

        # ----------------------------------------------------
        # Validate interval
        # ----------------------------------------------------

        if isinstance(self.interval, bool):
            raise ValueError(
                "Monitoring interval must be a number."
            )

        if not isinstance(self.interval, (int, float)):
            raise ValueError(
                "Monitoring interval must be a number."
            )

        if self.interval <= 0:
            raise ValueError(
                "Monitoring interval must be greater than 0."
            )

        self._running = True

        try:

            # ------------------------------------------------
            # Get current file position.
            #
            # Existing content will be ignored.
            # ------------------------------------------------

            try:
                current_position = self.file_path.stat().st_size
            except OSError as error:
                raise OSError(
                    f"Unable to access log file: {error}"
                ) from error

            while self._running:

                try:
                    # ----------------------------------------
                    # Open only for a short read operation.
                    #
                    # This prevents Windows from keeping the
                    # file locked continuously.
                    # ----------------------------------------

                    with self.file_path.open(
                        "r",
                        encoding="utf-8"
                    ) as file:

                        file.seek(current_position)

                        while self._running:

                            line = file.readline()

                            if not line:
                                break

                            current_position = file.tell()

                            line = line.strip()

                            if not line:
                                continue

                            yield line

                except UnicodeDecodeError as error:

                    raise ValueError(
                        f"Unable to read log file encoding: {error}"
                    ) from error

                except FileNotFoundError as error:

                    raise FileNotFoundError(
                        f"Log file not found: {self.file_path}"
                    ) from error

                except PermissionError as error:

                    raise PermissionError(
                        f"Permission denied while reading log file: "
                        f"{self.file_path}"
                    ) from error

                except OSError as error:

                    raise OSError(
                        f"Unable to monitor log file: {error}"
                    ) from error

                # --------------------------------------------
                # Wait before checking for newly appended data.
                # --------------------------------------------

                if self._running:
                    time.sleep(self.interval)

        finally:

            self._running = False

    def stop(self):

        self._running = False
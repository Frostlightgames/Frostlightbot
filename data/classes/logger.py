import sys
import datetime
import traceback
import discord

from pathlib import Path

LOG_PATH = Path("data/logs")
DATE_TIME_FORMAT = "%d.%m.%y %H-%M-%S"

class COLOR:
    """
    ANSI color codes for formatting terminal output.
    """

    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    GRAY = '\033[90m'
    RESET = '\033[0m'
    CRITICAL = '\033[91m\033[1m\033[4m'

class Logger:
    def __init__(self) -> None:
        """
        Initializes the logger:
        - Ensures the log directory exists.
        - Creates a new 'latest.log' file.
        - Rotates the existing 'latest.log' file if it exists.
        """

        # Creating log directory if not existent 
        LOG_PATH.mkdir(parents=True, exist_ok=True)
        latest_log = LOG_PATH / "latest.log"

        # If 'latest.log' exists, rotate it using its first line timestamp
        if latest_log.exists():
            
            # Get timestamp of last log
            with latest_log.open("r") as file:
                first_line = file.readline().strip()

            # Rename old latest.log file to timestamp logfile
            if first_line.startswith("[LOG START] "):
                timestamp = first_line.replace("[LOG START] ", "")
                rotated_name = LOG_PATH / f"log-{timestamp}.log"
                try:
                    latest_log.rename(rotated_name)
                except Exception:
                    timestamp = datetime.datetime.now().strftime(DATE_TIME_FORMAT)
                    ex_type, ex_value, _ = sys.exc_info()
                    if ex_type is not None:
                        print(f"{COLOR.CRITICAL} [{timestamp}] [CRITICAL] Could not rotate log file: {ex_type.__name__}: {ex_value}{COLOR.RESET}")

        # Create a new latest.log file
        with latest_log.open("w+") as file:
            file.write(f"[LOG START] {datetime.datetime.now().strftime(DATE_TIME_FORMAT)}\n")

    def _log(self, level: str, message: str):
        """
        Internal method to format and output a log messages.

        Args:
            level (str): The log level ('INFO', 'WARNING', or 'ERROR').
            message (str): The log message.
        """

        timestamp = datetime.datetime.now().strftime(DATE_TIME_FORMAT)
        log_line = f"[{timestamp}] [{level.upper()}] {message}\n"

        # Write to log file
        try:
            with (LOG_PATH / "latest.log").open("a") as file:
                file.write(log_line)
        except PermissionError:
            ex_type, ex_value, _ = sys.exc_info()
            if ex_type is not None:
                print(f"{COLOR.CRITICAL} [{timestamp}] [CRITICAL] Cannot log to logfile: {ex_type.__name__}: {ex_value}{COLOR.RESET}")

        # Color mapping for log levels
        color_map = {
            "INFO": COLOR.RESET,
            "WARNING": COLOR.YELLOW,
            "ERROR": COLOR.RED,
        }

        # Format output
        log_data = log_line.strip().split(" ", 2)
        timestamp = " ".join(log_data[:2])
        log_message = " ".join(log_data[2:])

        # Print to console with color-coded formatting
        print(f"{COLOR.GRAY}{timestamp} {color_map.get(level, COLOR.RESET)}{log_message}{COLOR.RESET}")

    async def _log_embed(self,title: str, message:str, color:int, bot: discord.Client = None):
        if bot:
            try:
                timestamp = datetime.datetime.now().strftime(DATE_TIME_FORMAT)
                embed = discord.Embed(title=title, color=color)
                embed.add_field(name=message, value="")
                embed.set_footer(text=f'[{timestamp}]')
                await bot.log_text_channel.send(embed=embed)
            except Exception as e:
                await self.error("Cannot log embed")
        

    async def info(self, message: str, bot: discord.Client = None):
        """
        Logs an info message.

        Args:
            message (str): The message to log.
        """

        self._log("INFO", message)
        await self._log_embed("Info", message, 0x0090ff, bot)

    async def warning(self, message: str, bot: discord.Client = None):
        """
        Logs a warning message.

        Args:
            message (str): The message to log.
        """

        self._log("WARNING", message)
        await self._log_embed("Warning", message, 0x00, bot)

    async def error(self, message: str, bot: discord.Client = None):
        """
        Logs an error message with exception traceback information, if available. It automatically gets the latest exception.

        Args:
            message (str): An optional message to include alongside the traceback.
        """

        ex_type, ex_value, ex_traceback = sys.exc_info()

        if ex_type is not None and ex_traceback is not None:
            trace = traceback.extract_tb(ex_traceback)[-1]
            filename = Path(trace.filename).name
            line_number = trace.lineno
            function = trace.name
            error_message = (f"Exception: {ex_type.__name__} | {ex_value} | File: {filename}, Line: {line_number}, Function: {function} | {message}")
        else:
            error_message = f"Error: {message}"

        self._log("ERROR", error_message)
        await self._log_embed("Error", error_message, 0xff0000, bot)
        
LOGGER = Logger()
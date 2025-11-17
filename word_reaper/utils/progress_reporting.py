"""
Enhanced progress reporting for WordReaper.

This module provides improved progress reporting functionality, especially
for generators and iterators of unknown length.
"""

import sys
import time
import threading
import os
from contextlib import contextmanager
from tqdm import tqdm

# Try to import psutil for memory reporting
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# ANSI colors
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
RESET = '\033[0m'

class StreamingProgressBar:
    """
    Progress bar for streaming operations where total is unknown.
    
    This class provides a progress indicator for operations where
    the total number of items is not known in advance, such as
    when processing generators or iterators.
    """
    
    def __init__(self, description="Processing", unit="items", 
                update_interval=0.5, file=sys.stdout, 
                show_memory=True, show_speed=True, ncols=80,
                color=RED):
        """
        Initialize the streaming progress bar.
        
        Args:
            description: Operation description
            unit: Unit name for items being processed
            update_interval: Update frequency in seconds
            file: Output file (default: stdout)
            show_memory: Whether to show memory usage
            show_speed: Whether to show processing speed
            ncols: Number of columns for the progress bar
            color: ANSI color code for the progress bar
        """
        self.description = description
        self.unit = unit
        self.update_interval = update_interval
        self.file = file
        self.show_memory = show_memory and PSUTIL_AVAILABLE
        self.show_speed = show_speed
        self.ncols = ncols
        self.color = color
        
        self.count = 0
        self.start_time = None
        self.last_update_time = None
        self.running = False
        self.thread = None
        self.last_count = 0
        self.speed = 0
    
    def __enter__(self):
        """Start the progress bar when entering a context."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop the progress bar when exiting a context."""
        self.stop()
    
    def start(self):
        """Start the progress bar and timer thread."""
        if self.running:
            return
        
        self.count = 0
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.running = True
        self.last_count = 0
        
        # Start update thread
        self.thread = threading.Thread(target=self._update_thread, daemon=True)
        self.thread.start()
        
        return self
    
    def stop(self):
        """Stop the progress bar and timer thread."""
        if not self.running:
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        
        self._update_display(final=True)
        print(file=self.file)  # Final newline
    
    def update(self, n=1):
        """Update the progress counter."""
        if not self.running:
            return
        
        self.count += n
    
    def _update_thread(self):
        """Thread that updates the display at regular intervals."""
        while self.running:
            self._update_display()
            time.sleep(self.update_interval)
    
    def _update_display(self, final=False):
        """Update the progress display."""
        now = time.time()
        elapsed = now - self.start_time
        
        # Calculate processing speed
        if self.show_speed and elapsed > 0:
            interval = now - self.last_update_time
            if interval > 0:
                interval_count = self.count - self.last_count
                self.speed = interval_count / interval
                self.last_count = self.count
                self.last_update_time = now
        
        # Create spinner
        spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        spinner = spinner_chars[int(now * 5) % len(spinner_chars)]
        
        # Create bar
        bar_size = 20
        if final:
            bar = self.color + "█" * bar_size + RESET
        else:
            filled_size = int((now * 5) % bar_size)
            bar = self.color + "█" * filled_size + "░" * (bar_size - filled_size) + RESET
        
        # Format count and elapsed time
        count_str = f"{self.count:,}"
        elapsed_str = self._format_time(elapsed)
        
        # Get memory usage if available
        memory_str = ""
        if self.show_memory and PSUTIL_AVAILABLE:
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / (1024 * 1024)
            memory_str = f" | {memory_mb:.1f} MB"
        
        # Get speed if available
        speed_str = ""
        if self.show_speed and elapsed > 0:
            speed_str = f" | {self.speed:.1f} {self.unit}/s"
            if self.speed > 0:
                # Estimate time remaining
                eta_str = ""
                if not final:
                    eta_str = f" | ~{self._format_time(self.count / self.speed)} total"
                speed_str += eta_str
        
        # Build status line
        if final:
            status = f"{self.description}: {count_str} {self.unit} in {elapsed_str}"
        else:
            status = f"{spinner} {self.description}: {count_str} {self.unit} | {elapsed_str}{memory_str}{speed_str}"
        
        # Ensure status line fits in terminal
        term_width = self.ncols
        if len(status) > term_width:
            status = status[:term_width-3] + "..."
        
        # Clear line and print status
        print(f"\r{' ' * term_width}\r{status}", end="", file=self.file)
        self.file.flush()
    
    def _format_time(self, seconds):
        """Format time in seconds to a human-readable string."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"

def iterate_with_progress(iterator, description="Processing", unit="items", 
                         show_memory=True, silent=False, color=RED):
    """
    Iterate through an iterator with progress reporting.
    
    This function wraps an iterator with a progress bar to provide
    visual feedback during processing.
    
    Args:
        iterator: Input iterator
        description: Operation description
        unit: Unit name for items being processed
        show_memory: Whether to show memory usage
        silent: Whether to suppress output
        color: ANSI color code for the progress bar
        
    Yields:
        Items from the iterator
    """
    if silent:
        # When silent, just yield items without progress
        yield from iterator
        return
    
    with StreamingProgressBar(description=description, unit=unit, 
                             show_memory=show_memory, color=color) as progress:
        for item in iterator:
            progress.update()
            yield item

class TqdmWithMemory(tqdm):
    """
    Enhanced tqdm progress bar with memory usage reporting.
    
    This class extends tqdm to include memory usage information
    in the progress bar.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize the progress bar with memory reporting."""
        # Extract memory reporting options
        self.show_memory = kwargs.pop('show_memory', True) and PSUTIL_AVAILABLE
        self.show_memory_warning = kwargs.pop('show_memory_warning', True) and PSUTIL_AVAILABLE
        self.memory_warning_threshold = kwargs.pop('memory_warning_threshold', 80)  # Percent
        
        # Initialize base tqdm
        super().__init__(*args, **kwargs)
        
        # Store initial memory usage
        if self.show_memory and PSUTIL_AVAILABLE:
            process = psutil.Process(os.getpid())
            self.initial_memory = process.memory_info().rss / (1024 * 1024)
        else:
            self.initial_memory = 0
    
    def display(self, *args, **kwargs):
        """Override display to include memory usage."""
        if self.show_memory and PSUTIL_AVAILABLE:
            # Get current memory usage
            process = psutil.Process(os.getpid())
            current_memory = process.memory_info().rss / (1024 * 1024)
            delta_memory = current_memory - self.initial_memory
            
            # Check system memory usage
            system_memory = psutil.virtual_memory()
            
            # Add memory info to postfix
            if not hasattr(self, 'postfix') or self.postfix is None:
                self.postfix = {}
            
            self.postfix['mem'] = f"{current_memory:.1f}MB"
            self.postfix['Δmem'] = f"{delta_memory:+.1f}MB"
            
            # Add warning if system memory is high
            if self.show_memory_warning and system_memory.percent > self.memory_warning_threshold:
                self.postfix['warning'] = f"High memory: {system_memory.percent}%"
        
        # Call original display
        super().display(*args, **kwargs)

def progress_bar_wrapper(func):
    """
    Decorator to add progress reporting to functions that return iterators.
    
    This decorator wraps the output of a function with a progress bar
    if it returns an iterator.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function with progress reporting
    """
    def wrapper(*args, **kwargs):
        # Extract progress bar options
        description = kwargs.pop('progress_description', func.__name__)
        unit = kwargs.pop('progress_unit', 'items')
        show_memory = kwargs.pop('progress_memory', True)
        silent = kwargs.pop('silent', False)
        
        # Call the function
        result = func(*args, **kwargs)
        
        # If result is an iterator and not silent, wrap with progress bar
        if hasattr(result, '__iter__') and not hasattr(result, '__len__') and not silent:
            return iterate_with_progress(
                result, 
                description=description,
                unit=unit,
                show_memory=show_memory,
                silent=silent
            )
        
        return result
    
    return wrapper

def get_progress_bar(iterable=None, desc="Processing", total=None, 
                    unit="it", ncols=80, colour="red", 
                    show_memory=True, massive=False, silent=False):
    """
    Get an appropriate progress bar based on context.
    
    This function returns either a TqdmWithMemory instance for known
    length iterables, or a StreamingProgressBar for unknown length
    iterables or streaming operations.
    
    Args:
        iterable: Input iterable
        desc: Operation description
        total: Total number of items
        unit: Unit name for items being processed
        ncols: Number of columns for the progress bar
        colour: Color for the progress bar
        show_memory: Whether to show memory usage
        massive: Whether in streaming mode
        silent: Whether to suppress output
        
    Returns:
        Progress bar instance
    """
    if silent:
        # When silent, return a dummy context manager
        @contextmanager
        def dummy_progress_bar():
            yield None
        return dummy_progress_bar()
    
    # Convert color name to ANSI code
    colors = {
        "red": RED,
        "green": GREEN,
        "yellow": YELLOW,
        "blue": BLUE,
        "cyan": CYAN,
        "magenta": MAGENTA
    }
    color_code = colors.get(colour.lower(), RED)
    
    # If iterable has known length or total is provided, use tqdm
    if (hasattr(iterable, '__len__') or total is not None) and not massive:
        return TqdmWithMemory(
            iterable,
            desc=desc,
            total=total,
            unit=unit,
            ncols=ncols,
            colour=colour,
            show_memory=show_memory,
            ascii=(" ", "#"),
            bar_format="{l_bar}" + color_code + "{bar}" + RESET + "| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]"
        )
    
    # Otherwise, use StreamingProgressBar
    return StreamingProgressBar(
        description=desc,
        unit=unit,
        update_interval=0.5,
        show_memory=show_memory,
        ncols=ncols,
        color=color_code
    )

def iter_with_progress(iterable, desc="Processing", unit="it", 
                      show_memory=True, massive=False, silent=False):
    """
    Iterate through an iterable with progress reporting.
    
    This function is a convenience wrapper for iterating through
    an iterable with appropriate progress reporting.
    
    Args:
        iterable: Input iterable
        desc: Operation description
        unit: Unit name for items being processed
        show_memory: Whether to show memory usage
        massive: Whether in streaming mode
        silent: Whether to suppress output
        
    Yields:
        Items from the iterable
    """
    if silent:
        # When silent, just yield items without progress
        for item in iterable:
            yield item
        return
    
    # If iterable has known length and not in massive mode, use tqdm
    if hasattr(iterable, '__len__') and not massive:
        for item in TqdmWithMemory(
            iterable,
            desc=desc,
            unit=unit,
            show_memory=show_memory,
            ascii=(" ", "#"),
            bar_format="{l_bar}" + RED + "{bar}" + RESET + "| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]"
        ):
            yield item
    else:
        # Otherwise, use StreamingProgressBar
        with StreamingProgressBar(description=desc, unit=unit, show_memory=show_memory) as progress:
            for item in iterable:
                progress.update()
                yield item
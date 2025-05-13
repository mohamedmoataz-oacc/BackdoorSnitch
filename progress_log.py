import logging
import logging.handlers
import multiprocessing as mp
import time
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

def worker(log_queue):
    """
    Worker process function.
    Configures the logger to use QueueHandler to send messages to log_queue.
    Logs some messages to simulate background work.
    """
    # Configure logger for this process
    logger = logging.getLogger("WorkerLogger")
    logger.setLevel(logging.DEBUG)
    
    # Use the built-in QueueHandler, which sends log records to log_queue.
    queue_handler = logging.handlers.QueueHandler(log_queue)
    logger.addHandler(queue_handler)
    
    # Optionally, you can add your own formatter here.
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    queue_handler.setFormatter(formatter)
    
    # Log some messages over time
    for i in range(10):
        logger.info(f"Worker log message {i}")
        time.sleep(1)
    
    # Log a final message
    logger.info("Worker process completed.")

def poll_log_queue(root, text_widget, log_queue):
    """
    Periodically poll the log_queue and append any log messages to the text_widget in the GUI.
    """
    while True:
        try:
            # Retrieve any available log record (non-blocking)
            record = log_queue.get_nowait()
        except Exception:
            # If no more messages are available, break out of the loop
            break
        else:
            # Append the log message to the text widget
            text_widget.insert(tk.END, record.getMessage() + "\n")
            text_widget.see(tk.END)
    
    # Schedule next poll after 100 milliseconds
    root.after(100, poll_log_queue, root, text_widget, log_queue)

def main():
    # Create a multiprocessing queue for logging.
    log_queue = mp.Queue()
    
    # Start the worker process that writes logs into the queue.
    process = mp.Process(target=worker, args=(log_queue,))
    process.start()
    
    # Set up a simple Tkinter GUI to display log messages.
    root = tk.Tk()
    root.title("Logging Monitor")
    
    text_area = ScrolledText(root, width=80, height=20)
    text_area.pack(padx=10, pady=10)
    
    # Start polling the log queue and updating the text_area.
    root.after(100, poll_log_queue, root, text_area, log_queue)
    
    # Start the GUI event loop.
    root.mainloop()

if __name__ == '__main__':
    main()

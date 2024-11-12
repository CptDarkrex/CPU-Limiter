import time
import psutil

class CPU_Limiter:
    def __init__(self):
        self.games = ['FortniteClient-Win64-Shipping.exe', 'RocketLeague.exe', 'cs2.exe']

    def limit_cpu_usage(self, process_name, process, cpu_limit_percentage, interval=0.5):
        """
        Limits the CPU usage of a specific process by suspending and resuming it.

        Args:
            process_name (str): Name of the process to limit (e.g., 'game.exe').
            process (process): feed the process into the function.
            cpu_limit_percentage (float): Desired CPU usage limit as a percentage (0-100).
            interval (float): Time interval (in seconds) to check and control the CPU usage.
        """
        # Calculate the ratio of sleep to active time
        active_time_ratio = cpu_limit_percentage / 100.0

        print(f"Limiting CPU usage for '{process_name}' to {cpu_limit_percentage}%...")

        try:
            while True:
                # Suspend the process to reduce CPU usage
                process.suspend()
                time.sleep(interval * (1 - active_time_ratio))

                # Resume the process to allow some CPU usage
                process.resume()
                time.sleep(interval * active_time_ratio)
        except psutil.NoSuchProcess:
            print(f"Process '{process_name}' has exited.")
        except psutil.AccessDenied:
            print(f"Process '{process_name}' is inaccessible")
        except KeyboardInterrupt:
            print("\nCPU limiter stopped.")

    def run(self):
        # Get the target process by name
        process = None
        process_name = None
        for p in psutil.process_iter(['name']):
            if p.info['name'] in self.games:
                process = p
                process_name = p.info['name']
                break

        if not process:
            print(f"No targets running")
            return

        print(f"Target found! {process_name}")

        self.limit_cpu_usage(process_name=process_name, process=process, cpu_limit_percentage=50, interval=1.0)



# Example usage
if __name__ == "__main__":
    limiter = CPU_Limiter()
    limiter.run()
    # Replace 'game.exe' with the actual process name of the game or app
    # limit_cpu_usage('cs2.exe', cpu_limit_percentage=50, interval=1.0)

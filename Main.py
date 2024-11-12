import time
import psutil

class CPU_Limiter:
    def __init__(self):
        self.gamesToSuspend = ['RocketLeague.exe']
        self.gamesToTerminate = ['FortniteClient-Win64-Shipping.exe', 'cs2.exe']
        self.sequences = {"terminate": self.terminateGame, "suspend": self.limit_cpu_usage}

    def checkSequence(self, process):
        if process.info['name'] in self.gamesToSuspend:
            return "suspend"
        return "terminate"

    def terminateGame(self, process, process_name):
        """
        Terminates a given process.

        Args:
            process: feed the process into the function.
            process_name: Name of the process to limit (e.g., 'game.exe').

        """
        try:
            process.terminate()  # Attempt graceful termination
            process.wait(timeout=3)  # Wait for termination (optional)
            print(f"Process {process_name} terminated.")
        except psutil.TimeoutExpired:
            print(f"{process_name} did not terminate in time; trying kill()...")
            process.kill()  # Forcefully kill the process if terminate() fails
        except Exception as e:
            print(f"An error occurred while trying to terminate {process_name}: {e}")

    def limit_cpu_usage(self, process_name, process, cpu_limit_percentage=50, interval=0.5):
        """
        Limits the CPU usage of a specific process by suspending and resuming it.

        Args:
            process_name (str): Name of the process to limit (e.g., 'game.exe').
            process (process): feed the process into the function.
            cpu_limit_percentage (float): Desired CPU usage limit as a percentage (0-100).
            interval (float): Time interval (in seconds) to check and control the CPU usage.
        """
        print(f"Limiting CPU usage for '{process_name}' to {cpu_limit_percentage}%...")

        # Calculate the ratio of sleep to active time
        active_time_ratio = cpu_limit_percentage / 100.0

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

        while True:
            for p in psutil.process_iter(['name']):
                if p.info['name'] in self.gamesToSuspend or p.info['name'] in self.gamesToTerminate:
                    process = p
                    process_name = p.info['name']
                    break

            if not process:
                print("No targets running")
            else:
                break



        print(f"Target found! {process_name}")

        sequence = self.checkSequence(process=process)

        # If suspending, specify a CPU limit, e.g., 50%
        if sequence == "suspend":
            self.sequences[sequence](process_name=process_name, process=process, cpu_limit_percentage=50)
        else:
            self.sequences[sequence](process=process, process_name=process_name)

# Example usage
if __name__ == "__main__":
    limiter = CPU_Limiter()
    limiter.run()

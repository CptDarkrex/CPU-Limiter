import time
import psutil

class CPU_Limiter:
    def __init__(self):
        self.gamesToSuspend = ['RocketLeague.exe', 'valorant.exe', 'minecraftlauncher.exe',]
        self.gamesToTerminate = ['FortniteClient-Win64-Shipping.exe', 'cs2.exe',
                                 'eldenring.exe', 'fallguys_client.exe', ]
        self.sequences = {"terminate": self.terminateGame, "suspend": self.limit_cpu_usage}

    def checkSequence(self, process):
        if process.info['name'] in self.gamesToSuspend:
            return "suspend"
        return "terminate"

    def terminateGame(self, process, process_name):
        try:
            process.terminate()
            process.wait(timeout=3)
            print(f"Process {process_name} terminated.")
        except psutil.TimeoutExpired:
            print(f"{process_name} did not terminate in time; trying kill()...")
            process.kill()
        except Exception as e:
            print(f"An error occurred while trying to terminate {process_name}: {e}")

    def limit_cpu_usage(self, process_name, process, cpu_limit_percentage=50, interval=1.0):
        print(f"Limiting CPU usage for '{process_name}' to {cpu_limit_percentage}%...")
        active_time_ratio = cpu_limit_percentage / 100.0

        try:
            while True:
                process.suspend()
                time.sleep(interval * (1 - active_time_ratio))
                process.resume()
                time.sleep(interval * active_time_ratio)
        except psutil.NoSuchProcess:
            print(f"Process '{process_name}' has exited.")
        except psutil.AccessDenied:
            print(f"Process '{process_name}' is inaccessible")
        except KeyboardInterrupt:
            print("\nCPU limiter stopped.")

    def run(self):
        process = None
        process_name = None

        while True:
            for p in psutil.process_iter(['name']):
                if p.info['name'] in self.gamesToSuspend or p.info['name'] in self.gamesToTerminate:
                    process = p
                    process_name = p.info['name']
                    break

            if not process:
                print("No targets running. Retrying in 3 seconds...")
                time.sleep(5)  # Reduce CPU usage by adding a delay
            else:
                break

        print(f"Target found! {process_name}")

        sequence = self.checkSequence(process=process)

        if sequence == "suspend":
            self.sequences[sequence](process_name=process_name, process=process, cpu_limit_percentage=50)
        else:
            self.sequences[sequence](process=process, process_name=process_name)

# Example usage
if __name__ == "__main__":
    limiter = CPU_Limiter()
    while True:
        limiter.run()

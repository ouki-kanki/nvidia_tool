import subprocess
import re

class NvidiaGPU:
    def __init__(self, index=0):
        self.index = index

    def get_name(self):
        return self._run_query("gpu_name")

    def get_temp(self):
        return self._run_query("temperature.gpu")

    def get_fan_speed_percent(self):
        return self._run_query("fan.speed")

    def get_power_draw(self):
        return self._run_query("power.draw")

    def get_current_power_limit(self):
        try:
            result = subprocess.run(
                ["nvidia-smi", "-q", "-d", "POWER"],
                capture_output=True, text=True, check=True
            )
            match = re.search(r"Current Power Limit\s*:\s*([\d.]+) W", result.stdout)
            if match:
                return float(match.group(1))
            else:
                return "Current Power limit not found"
        except Exception as e:
            return f"Error: {e}"

    def get_memory_used(self):
        return self._run_query("memory.used")

    def _run_query(self, field):
        try:
            result = subprocess.run(
                ["nvidia-smi", f"--query-gpu={field}", "--format=csv,noheader,nounits"],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip().split("\n")[self.index]
        except Exception as e:
            return f"Error: {e}"

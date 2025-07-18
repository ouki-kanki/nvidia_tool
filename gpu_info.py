from pynvml import (
    nvmlInit,
    nvmlDeviceGetHandleByIndex,
    nvmlDeviceGetTemperature,
    nvmlDeviceGetTemperatureThreshold,
    nvmlDeviceGetPowerUsage,
    nvmlDeviceGetName,
    nvmlDeviceGetFanSpeed,
    nvmlDeviceGetPowerManagementLimit,
    nvmlShutdown,
    NVMLError,
    NVML_TEMPERATURE_THRESHOLD_SLOWDOWN,
    NVML_TEMPERATURE_THRESHOLD_SHUTDOWN,
    NVML_TEMPERATURE_GPU
)


class NvidiaGPU:
    def __init__(self, index=0):
        nvmlInit()
        # grabs the first gpu in the system
        self.handle = nvmlDeviceGetHandleByIndex(index)

    def get_temp(self):
        return nvmlDeviceGetTemperature(self.handle, NVML_TEMPERATURE_GPU)

    def get_temp_threshold_slowdown(self):
        return nvmlDeviceGetTemperatureThreshold(
            self.handle,
            NVML_TEMPERATURE_THRESHOLD_SLOWDOWN)

    def get_temp_threshold_shutdown(self):
        return nvmlDeviceGetTemperatureThreshold(
            self.handle,
            NVML_TEMPERATURE_THRESHOLD_SHUTDOWN)

    def get_power_draw(self):
        return nvmlDeviceGetPowerUsage(self.handle) / 1000

    def get_name(self):
        return nvmlDeviceGetName(self.handle).decode()

    def get_fan_speed_percent(self):
        return nvmlDeviceGetFanSpeed(self.handle)

    def get_current_power_limit(self):
        try:
            power_limit = nvmlDeviceGetPowerManagementLimit(self.handle)
            return power_limit / 1000
        except NVMLError as e:
            return f"nvml error: {e}"

    def shutdown(self):
        """ always run shutdown on application close to release resources """
        nvmlShutdown()


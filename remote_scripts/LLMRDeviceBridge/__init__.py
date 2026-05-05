from .LLMRDeviceBridge import LLMRDeviceBridge


def create_instance(c_instance):
    return LLMRDeviceBridge(c_instance)

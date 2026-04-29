#include <stdint.h>

#if defined(__cplusplus)
extern "C" {
#endif

typedef void *SMTGPluginFactory;

__attribute__((visibility("default"))) int32_t bundleEntry(void *shared_library_handle)
{
    (void)shared_library_handle;
    return 1;
}

__attribute__((visibility("default"))) int32_t bundleExit(void)
{
    return 1;
}

__attribute__((visibility("default"))) SMTGPluginFactory GetPluginFactory(void)
{
    return 0;
}

#if defined(__cplusplus)
}
#endif

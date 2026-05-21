#include <atomic>
#include <arpa/inet.h>
#include <cstdint>
#include <cstring>
#include <netdb.h>
#include <sys/socket.h>
#include <unistd.h>

#define LLMR_VERSION "0.6.9"

#if defined(__APPLE__)
#import <Cocoa/Cocoa.h>

enum LlmrEditorAction : NSInteger {
    kLlmrEditorActionPlan = 1,
    kLlmrEditorActionExecute = 2,
    kLlmrEditorActionSaveSettings = 3,
    kLlmrEditorActionOpenSettings = 4,
    kLlmrEditorActionCloseSettings = 5,
    kLlmrEditorActionOllamaStart = 6,
    kLlmrEditorActionOllamaStop = 7,
    kLlmrEditorActionOllamaInstall = 8,
    kLlmrEditorActionOllamaListModels = 9,
    kLlmrEditorActionOllamaDownloadModel = 10,
    kLlmrEditorActionShowChatTab = 11,
    kLlmrEditorActionShowRawTab = 12,
    kLlmrEditorActionOpenAdvancedSettings = 13,
    kLlmrEditorActionCloseAdvancedSettings = 14,
    kLlmrEditorActionOllamaServeModel = 15,
    kLlmrEditorActionOllamaStopServingModel = 16,
    kLlmrEditorActionOpenHelp = 17,
    kLlmrEditorActionCancelSettings = 18,
    kLlmrEditorActionOllamaRefreshOnlineModels = 19,
    kLlmrEditorActionProviderChanged = 20,
    kLlmrEditorActionOllamaTestModel = 21,
    kLlmrEditorActionPreview = 22,
    kLlmrEditorActionDeviceBridgeStatus = 23,
    kLlmrEditorActionAutoApproveChanged = 24,
    kLlmrEditorActionOpenBridgeHelp = 25,
    kLlmrEditorActionCopyBridgeInstallPath = 26,
    kLlmrEditorActionInstallBridge = 27,
    kLlmrEditorActionTestReadiness = 28,
    kLlmrEditorActionChooseBridgeUserLibrary = 29,
    kLlmrEditorActionRevealInstalledBridge = 30,
    kLlmrEditorActionUseDetectedBridgeLibrary = 31,
    kLlmrEditorActionOpenSystemPrompts = 32,
    kLlmrEditorActionSaveSystemPrompt = 33,
    kLlmrEditorActionCancelSystemPrompt = 34,
    kLlmrEditorActionSaveSystemPromptAs = 35,
    kLlmrEditorActionLoadSystemPrompt = 36,
    kLlmrEditorActionResetSystemPrompt = 37,
    kLlmrEditorActionSystemPromptPresetChanged = 38,
    kLlmrEditorActionCancelOperation = 39,
};

static void llmrEditorHandleAction(void *owner, NSInteger action);

@interface LlmrEditorTarget : NSObject {
    void *_owner;
    NSInteger _action;
}
- (instancetype)initWithOwner:(void *)owner action:(NSInteger)action;
- (void)performAction:(id)sender;
@end

@interface LlmrCopyTextView : NSTextView
@end

@interface LlmrPromptTextView : NSTextView {
    NSTextField *_llmrPlaceholderLabel;
}
- (void)setLlmrPlaceholderLabel:(NSTextField *)label;
- (void)updateLlmrPlaceholder;
@end

@interface LlmrTextField : NSTextField
@end

@interface FullClickComboBox : NSPopUpButton
@end
#endif

namespace Steinberg {

using char8 = char;
using char16 = char16_t;
using int16 = int16_t;
using int32 = int32_t;
using uint32 = uint32_t;
using uint64 = uint64_t;
using TBool = uint8_t;
using tresult = int32;
using FIDString = const char8 *;
using TUID = char[16];
using SpeakerArrangement = uint64;

class FUnknown;
class IBStream;

constexpr tresult kNoInterface = -1;
constexpr tresult kResultOk = 0;
constexpr tresult kResultTrue = kResultOk;
constexpr tresult kResultFalse = 1;
constexpr tresult kInvalidArgument = 2;
constexpr tresult kNotImplemented = 3;
constexpr uint32 kManyInstances = 0x7FFFFFFF;

constexpr TUID kFUnknownIID = {
    0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00,
    static_cast<char>(0xC0), 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x46,
};
constexpr TUID kIPluginBaseIID = {
    0x22, static_cast<char>(0x88), static_cast<char>(0x8D), static_cast<char>(0xDB),
    0x15, 0x6E, 0x45, static_cast<char>(0xAE),
    static_cast<char>(0x83), 0x58, static_cast<char>(0xB3), 0x48,
    0x08, 0x19, 0x06, 0x25,
};
constexpr TUID kIPluginFactoryIID = {
    0x7A, 0x4D, static_cast<char>(0x81), 0x1C,
    0x52, 0x11, 0x4A, 0x1F,
    static_cast<char>(0xAE), static_cast<char>(0xD9), static_cast<char>(0xD2),
    static_cast<char>(0xEE),
    0x0B, 0x43, static_cast<char>(0xBF), static_cast<char>(0x9F),
};
constexpr TUID kIPluginFactory2IID = {
    0x00, 0x07, static_cast<char>(0xB6), 0x50,
    static_cast<char>(0xF2), 0x4B, 0x4C, 0x0B,
    static_cast<char>(0xA4), 0x64, static_cast<char>(0xED), static_cast<char>(0xB9),
    static_cast<char>(0xF0), 0x0B, 0x2A, static_cast<char>(0xBB),
};
constexpr TUID kIPluginFactory3IID = {
    0x45, 0x55, static_cast<char>(0xA2), static_cast<char>(0xAB),
    static_cast<char>(0xC1), 0x23, 0x4E, 0x57,
    static_cast<char>(0x9B), 0x12, 0x29, 0x10,
    0x36, static_cast<char>(0x87), static_cast<char>(0x89), 0x31,
};
constexpr TUID kIEditControllerIID = {
    static_cast<char>(0xDC), static_cast<char>(0xD7), static_cast<char>(0xBB),
    static_cast<char>(0xE3),
    0x77, 0x42, 0x44, static_cast<char>(0x8D),
    static_cast<char>(0xA8), 0x74, static_cast<char>(0xAA), static_cast<char>(0xCC),
    static_cast<char>(0x97), static_cast<char>(0x9C), 0x75, static_cast<char>(0x9E),
};
constexpr TUID kIPlugViewIID = {
    0x5B, static_cast<char>(0xC3), 0x25, 0x07,
    static_cast<char>(0xD0), 0x60, 0x49, static_cast<char>(0xEA),
    static_cast<char>(0xA6), 0x15, 0x1B, 0x52,
    0x2B, 0x75, 0x5B, 0x29,
};

inline bool iidEqual(const TUID a, const TUID b)
{
    return std::memcmp(a, b, 16) == 0;
}

inline void copyTuid(TUID dst, const TUID src)
{
    std::memcpy(dst, src, 16);
}

template <size_t N>
void copyString(char (&dst)[N], const char *src)
{
    std::memset(dst, 0, N);
    if (src) {
        std::strncpy(dst, src, N - 1);
    }
}

template <size_t N>
void copyString16(char16_t (&dst)[N], const char *src)
{
    std::memset(dst, 0, sizeof(dst));
    if (!src) {
        return;
    }
    size_t i = 0;
    for (; i + 1 < N && src[i] != '\0'; ++i) {
        dst[i] = static_cast<char16_t>(src[i]);
    }
    dst[i] = 0;
}

class FUnknown {
public:
    virtual tresult queryInterface(const TUID iid, void **obj) = 0;
    virtual uint32 addRef() = 0;
    virtual uint32 release() = 0;
};

class IPluginBase : public FUnknown {
public:
    virtual tresult initialize(FUnknown *context) = 0;
    virtual tresult terminate() = 0;
};

struct PFactoryInfo {
    enum FactoryFlags {
        kNoFlags = 0,
        kClassesDiscardable = 1 << 0,
        kLicenseCheck = 1 << 1,
        kComponentNonDiscardable = 1 << 3,
        kUnicode = 1 << 4,
    };

    char8 vendor[64];
    char8 url[256];
    char8 email[128];
    int32 flags;
};

struct PClassInfo {
    TUID cid;
    int32 cardinality;
    char8 category[32];
    char8 name[64];
};

struct PClassInfo2 {
    TUID cid;
    int32 cardinality;
    char8 category[32];
    char8 name[64];
    uint32 classFlags;
    char8 subCategories[128];
    char8 vendor[64];
    char8 version[64];
    char8 sdkVersion[64];
};

struct PClassInfoW {
    TUID cid;
    int32 cardinality;
    char8 category[32];
    char16 name[64];
    uint32 classFlags;
    char8 subCategories[128];
    char16 vendor[64];
    char16 version[64];
    char16 sdkVersion[64];
};

class IPluginFactory : public FUnknown {
public:
    virtual tresult getFactoryInfo(PFactoryInfo *info) = 0;
    virtual int32 countClasses() = 0;
    virtual tresult getClassInfo(int32 index, PClassInfo *info) = 0;
    virtual tresult createInstance(FIDString cid, FIDString iid, void **obj) = 0;
};

class IPluginFactory2 : public IPluginFactory {
public:
    virtual tresult getClassInfo2(int32 index, PClassInfo2 *info) = 0;
};

class IPluginFactory3 : public IPluginFactory2 {
public:
    virtual tresult getClassInfoUnicode(int32 index, PClassInfoW *info) = 0;
    virtual tresult setHostContext(FUnknown *context) = 0;
};

struct ViewRect {
    int32 left;
    int32 top;
    int32 right;
    int32 bottom;
};

class IPlugView;

class IPlugFrame : public FUnknown {
public:
    virtual tresult resizeView(IPlugView *view, ViewRect *newSize) = 0;
};

class IPlugView : public FUnknown {
public:
    virtual tresult isPlatformTypeSupported(FIDString type) = 0;
    virtual tresult attached(void *parent, FIDString type) = 0;
    virtual tresult removed() = 0;
    virtual tresult onWheel(float distance) = 0;
    virtual tresult onKeyDown(char16 key, int16 keyCode, int16 modifiers) = 0;
    virtual tresult onKeyUp(char16 key, int16 keyCode, int16 modifiers) = 0;
    virtual tresult getSize(ViewRect *size) = 0;
    virtual tresult onSize(ViewRect *newSize) = 0;
    virtual tresult onFocus(TBool state) = 0;
    virtual tresult setFrame(IPlugFrame *frame) = 0;
    virtual tresult canResize() = 0;
    virtual tresult checkSizeConstraint(ViewRect *rect) = 0;
};

constexpr FIDString kPlatformTypeNSView = "NSView";

constexpr TUID kLlmrProcessorCID = {
    0x4C, 0x4C, 0x4D, 0x52,
    0x54, 0x4F, 0x4D, 0x41,
    0x53, 0x4C, 0x41, 0x55,
    0x52, 0x45, 0x4E, 0x5A,
};
constexpr TUID kLlmrControllerCID = {
    0x4C, 0x4C, 0x4D, 0x52,
    0x43, 0x54, 0x52, 0x4C,
    0x54, 0x4F, 0x4D, 0x41,
    0x53, 0x4C, 0x41, 0x55,
};

namespace Vst {

constexpr TUID kIComponentIID = {
    static_cast<char>(0xE8), 0x31, static_cast<char>(0xFF), 0x31,
    static_cast<char>(0xF2), static_cast<char>(0xD5), 0x43, 0x01,
    static_cast<char>(0x92), static_cast<char>(0x8E), static_cast<char>(0xBB),
    static_cast<char>(0xEE),
    0x25, 0x69, 0x78, 0x02,
};
constexpr TUID kIAudioProcessorIID = {
    0x42, 0x04, 0x3F, static_cast<char>(0x99),
    static_cast<char>(0xB7), static_cast<char>(0xDA), 0x45, 0x3C,
    static_cast<char>(0xA5), 0x69, static_cast<char>(0xE7), static_cast<char>(0x9D),
    static_cast<char>(0x9A), static_cast<char>(0xAE), static_cast<char>(0xC3), 0x3D,
};

using MediaType = int32;
using BusDirection = int32;
using BusType = int32;
using IoMode = int32;
using String128 = char16_t[128];
using ParamID = uint32;
using ParamValue = double;
using UnitID = int32;
using TChar = char16_t;

constexpr MediaType kAudio = 0;
constexpr MediaType kEvent = 1;
constexpr BusDirection kInput = 0;
constexpr BusDirection kOutput = 1;
constexpr BusType kMain = 0;
constexpr uint32 kDefaultActive = 1 << 0;
constexpr SpeakerArrangement kStereo = 0x03;
constexpr int32 kSample32 = 0;
constexpr int32 kSample64 = 1;
constexpr uint32 kNoTail = 0;

struct BusInfo {
    MediaType mediaType;
    BusDirection direction;
    int32 channelCount;
    String128 name;
    BusType busType;
    uint32 flags;
};

struct RoutingInfo {
    MediaType mediaType;
    int32 busIndex;
    int32 channel;
};

struct ProcessSetup;
struct ProcessData;
class IComponentHandler;

struct ParameterInfo {
    ParamID id;
    String128 title;
    String128 shortTitle;
    String128 units;
    int32 stepCount;
    ParamValue defaultNormalizedValue;
    UnitID unitId;
    int32 flags;
};

class IComponent : public IPluginBase {
public:
    virtual tresult getControllerClassId(TUID classId) = 0;
    virtual tresult setIoMode(IoMode mode) = 0;
    virtual int32 getBusCount(MediaType type, BusDirection dir) = 0;
    virtual tresult getBusInfo(MediaType type, BusDirection dir, int32 index, BusInfo &bus) = 0;
    virtual tresult getRoutingInfo(RoutingInfo &inInfo, RoutingInfo &outInfo) = 0;
    virtual tresult activateBus(MediaType type, BusDirection dir, int32 index, TBool state) = 0;
    virtual tresult setActive(TBool state) = 0;
    virtual tresult setState(IBStream *state) = 0;
    virtual tresult getState(IBStream *state) = 0;
};

class IAudioProcessor : public FUnknown {
public:
    virtual tresult setBusArrangements(SpeakerArrangement *inputs, int32 numIns,
                                       SpeakerArrangement *outputs, int32 numOuts) = 0;
    virtual tresult getBusArrangement(BusDirection dir, int32 index, SpeakerArrangement &arr) = 0;
    virtual tresult canProcessSampleSize(int32 symbolicSampleSize) = 0;
    virtual uint32 getLatencySamples() = 0;
    virtual tresult setupProcessing(ProcessSetup &setup) = 0;
    virtual tresult setProcessing(TBool state) = 0;
    virtual tresult process(ProcessData &data) = 0;
    virtual uint32 getTailSamples() = 0;
};

class IEditController : public IPluginBase {
public:
    virtual tresult setComponentState(IBStream *state) = 0;
    virtual tresult setState(IBStream *state) = 0;
    virtual tresult getState(IBStream *state) = 0;
    virtual int32 getParameterCount() = 0;
    virtual tresult getParameterInfo(int32 paramIndex, ParameterInfo &info) = 0;
    virtual tresult getParamStringByValue(ParamID id, ParamValue valueNormalized,
                                          String128 string) = 0;
    virtual tresult getParamValueByString(ParamID id, TChar *string,
                                          ParamValue &valueNormalized) = 0;
    virtual ParamValue normalizedParamToPlain(ParamID id, ParamValue valueNormalized) = 0;
    virtual ParamValue plainParamToNormalized(ParamID id, ParamValue plainValue) = 0;
    virtual ParamValue getParamNormalized(ParamID id) = 0;
    virtual tresult setParamNormalized(ParamID id, ParamValue value) = 0;
    virtual tresult setComponentHandler(IComponentHandler *handler) = 0;
    virtual IPlugView *createView(FIDString name) = 0;
};

class LlmrComponent final : public IComponent, public IAudioProcessor {
public:
    LlmrComponent() = default;

    tresult queryInterface(const TUID iid, void **obj) override
    {
        if (!obj) {
            return kInvalidArgument;
        }
        if (iidEqual(iid, kFUnknownIID) || iidEqual(iid, kIPluginBaseIID) ||
            iidEqual(iid, kIComponentIID)) {
            addRef();
            *obj = static_cast<IComponent *>(this);
            return kResultOk;
        }
        if (iidEqual(iid, kIAudioProcessorIID)) {
            addRef();
            *obj = static_cast<IAudioProcessor *>(this);
            return kResultOk;
        }
        *obj = nullptr;
        return kNoInterface;
    }

    uint32 addRef() override { return ++refCount_; }
    uint32 release() override
    {
        const auto count = --refCount_;
        if (count == 0) {
            delete this;
        }
        return count;
    }

    tresult initialize(FUnknown *context) override
    {
        (void)context;
        return kResultOk;
    }
    tresult terminate() override { return kResultOk; }

    tresult getControllerClassId(TUID classId) override
    {
        if (classId) {
            copyTuid(classId, kLlmrControllerCID);
        }
        return kResultOk;
    }

    tresult setIoMode(IoMode mode) override
    {
        (void)mode;
        return kResultOk;
    }

    int32 getBusCount(MediaType type, BusDirection dir) override
    {
        if (type == kAudio && dir == kOutput) {
            return 1;
        }
        if (type == kEvent && dir == kInput) {
            return 1;
        }
        return 0;
    }

    tresult getBusInfo(MediaType type, BusDirection dir, int32 index, BusInfo &bus) override
    {
        if (index != 0) {
            return kInvalidArgument;
        }
        std::memset(&bus, 0, sizeof(bus));
        bus.mediaType = type;
        bus.direction = dir;
        bus.busType = kMain;
        bus.flags = kDefaultActive;

        if (type == kAudio && dir == kOutput) {
            bus.channelCount = 2;
            copyString16(bus.name, "Stereo Out");
            return kResultOk;
        }
        if (type == kEvent && dir == kInput) {
            bus.channelCount = 16;
            copyString16(bus.name, "MIDI In");
            return kResultOk;
        }
        return kInvalidArgument;
    }

    tresult getRoutingInfo(RoutingInfo &inInfo, RoutingInfo &outInfo) override
    {
        outInfo = inInfo;
        return kResultOk;
    }

    tresult activateBus(MediaType type, BusDirection dir, int32 index, TBool state) override
    {
        (void)type;
        (void)dir;
        (void)index;
        (void)state;
        return kResultOk;
    }

    tresult setActive(TBool state) override
    {
        (void)state;
        return kResultOk;
    }

    tresult setState(IBStream *state) override
    {
        (void)state;
        return kResultOk;
    }

    tresult getState(IBStream *state) override
    {
        (void)state;
        return kResultOk;
    }

    tresult setBusArrangements(SpeakerArrangement *inputs, int32 numIns,
                               SpeakerArrangement *outputs, int32 numOuts) override
    {
        (void)inputs;
        (void)outputs;
        return (numIns == 0 && numOuts == 1) ? kResultTrue : kResultFalse;
    }

    tresult getBusArrangement(BusDirection dir, int32 index, SpeakerArrangement &arr) override
    {
        if (index != 0 || dir != kOutput) {
            return kInvalidArgument;
        }
        arr = kStereo;
        return kResultOk;
    }

    tresult canProcessSampleSize(int32 symbolicSampleSize) override
    {
        return (symbolicSampleSize == kSample32 || symbolicSampleSize == kSample64) ? kResultTrue
                                                                                   : kResultFalse;
    }

    uint32 getLatencySamples() override { return 0; }

    tresult setupProcessing(ProcessSetup &setup) override
    {
        (void)setup;
        return kResultOk;
    }

    tresult setProcessing(TBool state) override
    {
        (void)state;
        return kResultOk;
    }

    tresult process(ProcessData &data) override
    {
        (void)data;
        return kResultOk;
    }

    uint32 getTailSamples() override { return kNoTail; }

private:
    std::atomic<uint32> refCount_{1};
};

class LlmrEditorView final : public IPlugView {
public:
    LlmrEditorView() = default;
    ~LlmrEditorView()
    {
        removed();
#if defined(__APPLE__)
        [chatHistory_ release];
        chatHistory_ = nullptr;
        [lastRawResponse_ release];
        lastRawResponse_ = nullptr;
#endif
    }

    tresult queryInterface(const TUID iid, void **obj) override
    {
        if (!obj) {
            return kInvalidArgument;
        }
        if (iidEqual(iid, kFUnknownIID) || iidEqual(iid, kIPlugViewIID)) {
            addRef();
            *obj = static_cast<IPlugView *>(this);
            return kResultOk;
        }
        *obj = nullptr;
        return kNoInterface;
    }

    uint32 addRef() override { return ++refCount_; }
    uint32 release() override
    {
        const auto count = --refCount_;
        if (count == 0) {
            delete this;
        }
        return count;
    }

    tresult isPlatformTypeSupported(FIDString type) override
    {
        return isNsViewType(type) ? kResultTrue : kResultFalse;
    }

    tresult attached(void *parent, FIDString type) override
    {
        if (!parent || !isNsViewType(type)) {
            return kInvalidArgument;
        }

#if defined(__APPLE__)
        @autoreleasepool {
            auto *parentView = static_cast<NSView *>(parent);
            removed();

            const CGFloat width = static_cast<CGFloat>(rect_.right - rect_.left);
            const CGFloat height = static_cast<CGFloat>(rect_.bottom - rect_.top);
            NSRect frame = NSMakeRect(0.0, 0.0, width, height);

            view_ = [[NSView alloc] initWithFrame:frame];
            [view_ setAutoresizingMask:(NSViewWidthSizable | NSViewHeightSizable)];
            [view_ setWantsLayer:YES];
            view_.layer.backgroundColor = [NSColor colorWithCalibratedRed:0.10
                                                                    green:0.11
                                                                     blue:0.12
                                                                    alpha:1.0]
                                             .CGColor;
            buildEditor(width, height);

            [parentView addSubview:view_];
        }
        return kResultOk;
#else
        return kNotImplemented;
#endif
    }

    tresult removed() override
    {
#if defined(__APPLE__)
        if (view_) {
            [view_ removeFromSuperview];
            [view_ release];
            view_ = nullptr;
        }
        [targets_ release];
        targets_ = nullptr;
        [lastActions_ release];
        lastActions_ = nullptr;
        chatView_ = nullptr;
        settingsView_ = nullptr;
        chatHistoryView_ = nullptr;
        rawResponseView_ = nullptr;
        chatInputView_ = nullptr;
        chatInputScrollView_ = nullptr;
        chatPromptPlaceholderLabel_ = nullptr;
        chatStatusLabel_ = nullptr;
        chatModelLabel_ = nullptr;
        chatOscLabel_ = nullptr;
        chatBridgeLabel_ = nullptr;
        chatDryRunLabel_ = nullptr;
        chatSendButton_ = nullptr;
        chatCancelButton_ = nullptr;
        chatExecuteButton_ = nullptr;
        chatPreviewButton_ = nullptr;
        chatAutoApproveButton_ = nullptr;
        chatSettingsButton_ = nullptr;
        chatTabButton_ = nullptr;
        rawTabButton_ = nullptr;
        settingsProviderCombo_ = nullptr;
        settingsModelField_ = nullptr;
        settingsEndpointField_ = nullptr;
        settingsApiKeyField_ = nullptr;
        settingsOscHostField_ = nullptr;
        settingsOscPortField_ = nullptr;
        settingsExtraPromptButton_ = nullptr;
        settingsDestructiveButton_ = nullptr;
        settingsDryRunButton_ = nullptr;
        settingsAutoApproveButton_ = nullptr;
        settingsMainView_ = nullptr;
        settingsAdvancedView_ = nullptr;
        settingsCustomModelField_ = nullptr;
        settingsModelStatusLabel_ = nullptr;
        settingsBridgeHostField_ = nullptr;
        settingsBridgePortField_ = nullptr;
        settingsBridgeLibraryCandidatesCombo_ = nullptr;
        settingsBridgeLibraryLabel_ = nullptr;
        settingsBridgeInstallTargetLabel_ = nullptr;
        settingsBridgeInstallButton_ = nullptr;
        settingsBridgeRevealButton_ = nullptr;
        ollamaStatusLabel_ = nullptr;
        deviceBridgeStatusLabel_ = nullptr;
        ollamaModelField_ = nullptr;
        ollamaModelsCombo_ = nullptr;
        [bridgeUserLibraryPath_ release];
        bridgeUserLibraryPath_ = nullptr;
        if (systemPromptsWindow_) {
            [systemPromptsWindow_ close];
            [systemPromptsWindow_ release];
            systemPromptsWindow_ = nullptr;
        }
        if (settingsWindow_) {
            NSWindow *parent = [settingsWindow_ sheetParent];
            if (parent) {
                [parent endSheet:settingsWindow_];
            }
            [settingsWindow_ close];
            [settingsWindow_ release];
            settingsWindow_ = nullptr;
        }
        systemPromptPresetCombo_ = nullptr;
        systemPromptEditor_ = nullptr;
        operationCancelRequested_.store(true);
        operationBusy_.store(false);
#endif
        return kResultOk;
    }

    tresult onWheel(float distance) override
    {
        (void)distance;
        return kResultFalse;
    }

    tresult onKeyDown(char16 key, int16 keyCode, int16 modifiers) override
    {
        (void)key;
        (void)keyCode;
        (void)modifiers;
        return kResultFalse;
    }

    tresult onKeyUp(char16 key, int16 keyCode, int16 modifiers) override
    {
        (void)key;
        (void)keyCode;
        (void)modifiers;
        return kResultFalse;
    }

    tresult getSize(ViewRect *size) override
    {
        if (!size) {
            return kInvalidArgument;
        }
        *size = rect_;
        return kResultOk;
    }

    tresult onSize(ViewRect *newSize) override
    {
        if (!newSize) {
            return kInvalidArgument;
        }
        rect_ = *newSize;
#if defined(__APPLE__)
        if (view_) {
            const CGFloat width = static_cast<CGFloat>(rect_.right - rect_.left);
            const CGFloat height = static_cast<CGFloat>(rect_.bottom - rect_.top);
            [view_ setFrame:NSMakeRect(0.0, 0.0, width, height)];
        }
#endif
        return kResultOk;
    }

    tresult onFocus(TBool state) override
    {
        (void)state;
        return kResultOk;
    }

    tresult setFrame(IPlugFrame *frame) override
    {
        plugFrame_ = frame;
        return kResultOk;
    }

    tresult canResize() override { return kResultFalse; }

    tresult checkSizeConstraint(ViewRect *rect) override
    {
        if (!rect) {
            return kInvalidArgument;
        }
        constexpr int kFixedW = 960, kFixedH = 720;
        rect->right = rect->left + kFixedW;
        rect->bottom = rect->top + kFixedH;
        return kResultOk;
    }

#if defined(__APPLE__)
    void handleEditorAction(NSInteger action)
    {
        switch (action) {
        case kLlmrEditorActionPlan:          planFromPrompt(); break;
        case kLlmrEditorActionExecute:       executeFromMainButton(); break;
        case kLlmrEditorActionPreview:       executeLastPlan(true); break;
        case kLlmrEditorActionSaveSettings:  saveSettings(); hideSettings(); break;
        case kLlmrEditorActionOpenSettings:  showSettings(); break;
        case kLlmrEditorActionCloseSettings: cancelSettings(); break;
        case kLlmrEditorActionOllamaStart:   ollamaStart(); break;
        case kLlmrEditorActionOllamaStop:    ollamaStop(); break;
        case kLlmrEditorActionOllamaInstall: ollamaInstall(); break;
        case kLlmrEditorActionOllamaListModels:    ollamaListModels(); break;
        case kLlmrEditorActionOllamaDownloadModel: ollamaDownloadModel(); break;
        case kLlmrEditorActionShowChatTab:    showResponseTab(false); break;
        case kLlmrEditorActionShowRawTab:     showResponseTab(true); break;
        case kLlmrEditorActionOpenAdvancedSettings:  showSettings(); break;
        case kLlmrEditorActionCloseAdvancedSettings: showSettings(); break;
        case kLlmrEditorActionOllamaServeModel:      ollamaServeModel(); break;
        case kLlmrEditorActionOllamaStopServingModel: ollamaStopServingModel(); break;
        case kLlmrEditorActionOpenHelp:       openHelp(); break;
        case kLlmrEditorActionCancelSettings: cancelSettings(); break;
        case kLlmrEditorActionOllamaRefreshOnlineModels: ollamaRefreshOnlineModels(true); break;
        case kLlmrEditorActionProviderChanged: providerChanged(); break;
        case kLlmrEditorActionOllamaTestModel: ollamaTestModel(); break;
        case kLlmrEditorActionDeviceBridgeStatus: checkDeviceBridgeStatus(); break;
        case kLlmrEditorActionAutoApproveChanged: saveAutoApproveSetting(); break;
        case kLlmrEditorActionOpenBridgeHelp: openBridgeSetupHelp(); break;
        case kLlmrEditorActionCopyBridgeInstallPath: copyBridgeInstallPath(); break;
        case kLlmrEditorActionInstallBridge: installDeviceBridgeFromSettings(); break;
        case kLlmrEditorActionTestReadiness: testReadiness(); break;
        case kLlmrEditorActionChooseBridgeUserLibrary: chooseBridgeUserLibrary(); break;
        case kLlmrEditorActionRevealInstalledBridge: revealInstalledBridge(); break;
        case kLlmrEditorActionUseDetectedBridgeLibrary: useDetectedBridgeLibrary(); break;
        case kLlmrEditorActionOpenSystemPrompts: openSystemPromptsWindow(); break;
        case kLlmrEditorActionSaveSystemPrompt: saveSystemPromptFromEditor(); break;
        case kLlmrEditorActionCancelSystemPrompt: closeSystemPromptsWindow(); break;
        case kLlmrEditorActionSaveSystemPromptAs: saveSystemPromptToFile(); break;
        case kLlmrEditorActionLoadSystemPrompt: loadSystemPromptFromFile(); break;
        case kLlmrEditorActionResetSystemPrompt: resetSystemPromptToDefault(); break;
        case kLlmrEditorActionSystemPromptPresetChanged: systemPromptPresetChanged(); break;
        case kLlmrEditorActionCancelOperation: cancelCurrentOperation(); break;
        default: break;
        }
    }
#endif

private:
    static bool isNsViewType(FIDString type)
    {
        return type && std::strcmp(type, kPlatformTypeNSView) == 0;
    }

#if defined(__APPLE__)
    static NSString *defaultEndpointForProvider(NSString *provider)
    {
        NSString *raw = provider ? provider : @"";
        NSString *p = [[raw stringByTrimmingCharactersInSet:
                        [NSCharacterSet whitespaceAndNewlineCharacterSet]] lowercaseString];
        if ([p isEqualToString:@"ollama"]) {
            return @"http://127.0.0.1:11434/api/chat";
        }
        if ([p isEqualToString:@"anthropic"]) {
            return @"https://api.anthropic.com/v1/messages";
        }
        if ([p isEqualToString:@"google"]) {
            return @"https://generativelanguage.googleapis.com/v1beta";
        }
        if ([p isEqualToString:@"custom"]) {
            return @"";
        }
        if ([p length] == 0 || [p isEqualToString:@"openai"]) {
            return @"https://api.openai.com/v1/chat/completions";
        }
        return @"";
    }

    static NSArray *providers()
    {
        return @[@"openai", @"anthropic", @"google", @"ollama", @"omlx", @"custom"];
    }

    static NSString *canonicalProvider(NSString *provider)
    {
        NSString *raw = provider ? provider : @"";
        NSString *p = [[raw stringByTrimmingCharactersInSet:
                        [NSCharacterSet whitespaceAndNewlineCharacterSet]] lowercaseString];
        return [p length] > 0 ? p : @"openai";
    }

    static bool providerHasManagedEndpoint(NSString *provider)
    {
        NSString *p = canonicalProvider(provider);
        return [p isEqualToString:@"openai"] ||
               [p isEqualToString:@"anthropic"] ||
               [p isEqualToString:@"google"] ||
               [p isEqualToString:@"ollama"];
    }

    static NSArray *defaultModelsForProvider(NSString *provider)
    {
        NSString *p = [provider lowercaseString];
        if ([p isEqualToString:@"anthropic"]) {
            return @[@"claude-3-5-sonnet-latest", @"claude-3-5-haiku-latest", @"claude-3-opus-latest"];
        }
        if ([p isEqualToString:@"google"]) {
            return @[@"gemini-2.5-flash", @"gemini-2.5-pro", @"gemini-1.5-flash", @"gemini-1.5-pro"];
        }
        if ([p isEqualToString:@"ollama"]) {
            return @[];
        }
        if ([p isEqualToString:@"omlx"]) {
            return @[];
        }
        if ([p isEqualToString:@"custom"]) {
            return @[];
        }
        return @[@"gpt-4.1-mini", @"gpt-4.1", @"gpt-4o-mini", @"gpt-4o"];
    }

    static NSArray *fallbackOllamaDownloadModels()
    {
        return @[
            @"llama3.1", @"deepseek-r1", @"llama3.2", @"gemma3", @"qwen3", @"qwen2.5",
            @"mistral", @"gpt-oss", @"phi4", @"gemma2", @"codellama", @"llava",
            @"qwen2.5-coder", @"mistral-nemo", @"llama3.3", @"tinyllama", @"mixtral",
            @"smollm2", @"devstral", @"codestral", @"dolphin3", @"granite3.3"
        ];
    }

    static NSString *controlString(id control)
    {
        NSString *value = @"";
        if ([control isKindOfClass:[NSPopUpButton class]]) {
            NSMenuItem *item = [(NSPopUpButton *)control selectedItem];
            id represented = [item representedObject];
            if ([represented isKindOfClass:[NSString class]]) {
                value = represented;
            } else {
                value = [item title] ?: @"";
            }
        } else if ([control respondsToSelector:@selector(stringValue)]) {
            value = [control stringValue] ?: @"";
        }
        return [value stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
    }

    static bool buttonOn(NSButton *button)
    {
        return button && [button state] == NSControlStateValueOn;
    }

    static double numberValue(NSDictionary *dict, NSString *key, double fallback)
    {
        id value = [dict objectForKey:key];
        return value ? [value doubleValue] : fallback;
    }

    static int intValue(NSDictionary *dict, NSString *key, int fallback)
    {
        id value = [dict objectForKey:key];
        return value ? [value intValue] : fallback;
    }

    static NSNumber *boolNumber(NSDictionary *dict, NSString *key, bool fallback)
    {
        id value = [dict objectForKey:key];
        return [NSNumber numberWithInt:(value ? [value boolValue] : fallback) ? 1 : 0];
    }

    static double clampedNumberValue(NSDictionary *dict, NSString *key, double fallback, double minimum, double maximum)
    {
        double value = numberValue(dict, key, fallback);
        if (value < minimum) return minimum;
        if (value > maximum) return maximum;
        return value;
    }

    static NSString *stringValue(NSDictionary *dict, NSString *key, NSString *fallback)
    {
        id value = [dict objectForKey:key];
        if ([value isKindOfClass:[NSString class]] && [value length] > 0) {
            return value;
        }
        return fallback;
    }

    static int semanticParameterIndex(NSDictionary *args, int fallback)
    {
        NSString *raw = stringValue(args, @"parameter_name", @"");
        NSString *name = [[raw lowercaseString] stringByReplacingOccurrencesOfString:@"_" withString:@" "];
        name = [name stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
        if ([name isEqualToString:@"device on"] ||
            [name isEqualToString:@"on"] ||
            [name isEqualToString:@"enabled"] ||
            [name isEqualToString:@"activator"] ||
            [name isEqualToString:@"device activator"]) {
            return 0;
        }
        return fallback;
    }

    static NSString *normalizedDeviceType(NSString *raw)
    {
        NSString *value = [(raw ? raw : @"instrument") lowercaseString];
        value = [value stringByReplacingOccurrencesOfString:@" " withString:@"_"];
        if ([value isEqualToString:@"instruments"]) return @"instrument";
        if ([value isEqualToString:@"audio_effects"] || [value isEqualToString:@"effect"] || [value isEqualToString:@"effects"]) return @"audio_effect";
        if ([value isEqualToString:@"midi_effects"]) return @"midi_effect";
        if ([value isEqualToString:@"plugins"]) return @"plugin";
        if ([value isEqualToString:@"drums"]) return @"drum";
        if ([value isEqualToString:@"audio_effect"] ||
            [value isEqualToString:@"midi_effect"] ||
            [value isEqualToString:@"instrument"] ||
            [value isEqualToString:@"plugin"] ||
            [value isEqualToString:@"drum"] ||
            [value isEqualToString:@"all"]) {
            return value;
        }
        return @"instrument";
    }

    // ─── Color helpers ────────────────────────────────────────
    static NSColor *cBg()     { return [NSColor colorWithCalibratedRed:0.10 green:0.11 blue:0.12 alpha:1.0]; }
    static NSColor *cHdr()    { return [NSColor colorWithCalibratedRed:0.14 green:0.15 blue:0.17 alpha:1.0]; }
    static NSColor *cPanel()  { return [NSColor colorWithCalibratedRed:0.145 green:0.155 blue:0.17 alpha:1.0]; }
    static NSColor *cPri()    { return [NSColor colorWithCalibratedWhite:0.96 alpha:1.0]; }
    static NSColor *cSec()    { return [NSColor colorWithCalibratedWhite:0.60 alpha:1.0]; }
    static NSColor *cAccent() { return [NSColor colorWithCalibratedRed:0.43 green:0.76 blue:0.96 alpha:1.0]; }
    static NSColor *cChatBg() { return [NSColor colorWithCalibratedRed:0.07 green:0.075 blue:0.085 alpha:1.0]; }
    static NSColor *cOk()     { return [NSColor colorWithCalibratedRed:0.36 green:0.78 blue:0.55 alpha:1.0]; }
    static NSColor *cWarn()   { return [NSColor colorWithCalibratedRed:0.98 green:0.72 blue:0.30 alpha:1.0]; }
    static NSColor *cBad()    { return [NSColor colorWithCalibratedRed:0.95 green:0.38 blue:0.38 alpha:1.0]; }

    // ─── Generic UI helpers (add to arbitrary parent) ─────────
    NSTextField *labelIn(NSView *p, NSString *txt, NSRect f, NSFont *font, NSColor *col)
    {
        NSTextField *v = [[NSTextField alloc] initWithFrame:f];
        [v setStringValue:txt]; [v setBezeled:NO]; [v setDrawsBackground:NO];
        [v setEditable:NO]; [v setSelectable:NO];
        [v setLineBreakMode:NSLineBreakByTruncatingTail];
        [v setFont:font]; [v setTextColor:col];
        [p addSubview:v]; [v release]; return v;
    }
    NSTextField *noteIn(NSView *p, NSString *txt, NSRect f, NSFont *font, NSColor *col)
    {
        NSTextField *v = labelIn(p, txt, f, font, col);
        [v setLineBreakMode:NSLineBreakByWordWrapping];
        [v setUsesSingleLineMode:NO];
        [[v cell] setWraps:YES];
        return v;
    }
    NSTextField *chipIn(NSView *p, NSString *txt, NSRect f, NSColor *fg, NSColor *bg, NSColor *border)
    {
        NSTextField *v = labelIn(p, txt, f, [NSFont boldSystemFontOfSize:10.0], fg);
        (void)bg;
        (void)border;
        [v setAlignment:NSTextAlignmentLeft];
        [[v cell] setLineBreakMode:NSLineBreakByTruncatingTail];
        [[v cell] setUsesSingleLineMode:YES];
        [v setWantsLayer:NO];
        return v;
    }
    void setChip(NSTextField *chip, NSString *txt, bool ok)
    {
        if (!chip) return;
        NSString *text = txt ?: @"";
        NSColor *iconColor = ok ? cOk() : cBad();
        NSDictionary *iconAttrs = @{
            NSFontAttributeName: [NSFont boldSystemFontOfSize:11.0],
            NSForegroundColorAttributeName: iconColor,
        };
        NSDictionary *textAttrs = @{
            NSFontAttributeName: [NSFont systemFontOfSize:11.0],
            NSForegroundColorAttributeName: cPri(),
        };
        NSMutableAttributedString *value = [[[NSMutableAttributedString alloc] init] autorelease];
        [value appendAttributedString:[[[NSAttributedString alloc] initWithString:@"● "
                                                                        attributes:iconAttrs] autorelease]];
        [value appendAttributedString:[[[NSAttributedString alloc] initWithString:text
                                                                        attributes:textAttrs] autorelease]];
        [chip setAttributedStringValue:value];
        [chip setWantsLayer:NO];
    }
    NSTextField *fieldIn(NSView *p, NSRect f, NSString *ph, BOOL secure)
    {
        NSTextField *v = secure ? [[NSSecureTextField alloc] initWithFrame:f]
                                : [[LlmrTextField alloc] initWithFrame:f];
        [v setPlaceholderString:ph]; [v setFont:[NSFont systemFontOfSize:12.0]];
        [p addSubview:v]; [v release]; return v;
    }
    NSTextView *promptTextViewIn(NSView *p, NSRect f, NSScrollView **outScroll)
    {
        NSScrollView *sc = [[NSScrollView alloc] initWithFrame:f];
        [sc setHasVerticalScroller:YES];
        [sc setHasHorizontalScroller:NO];
        [sc setHorizontalScrollElasticity:NSScrollElasticityNone];
        [sc setAutohidesScrollers:YES];
        [sc setBorderType:NSBezelBorder];
        [sc setAutoresizingMask:NSViewWidthSizable | NSViewMaxYMargin];

        NSTextView *v = [[LlmrPromptTextView alloc] initWithFrame:NSMakeRect(0, 0, f.size.width, f.size.height)];
        [v setFont:[NSFont systemFontOfSize:13.0]];
        [v setEditable:YES];
        [v setRichText:NO];
        [v setSelectable:YES];
        [v setAllowsUndo:YES];
        [v setBackgroundColor:cChatBg()];
        [v setTextColor:cPri()];
        [v setHorizontallyResizable:NO];
        [v setVerticallyResizable:YES];
        [[v textContainer] setWidthTracksTextView:YES];
        [[v textContainer] setContainerSize:NSMakeSize(f.size.width, CGFLOAT_MAX)];
        [v setAutoresizingMask:NSViewWidthSizable | NSViewHeightSizable];

        [sc setDocumentView:v];
        [p addSubview:sc];
        if (outScroll) {
            *outScroll = sc;
        }
        [v release];
        [sc release];
        return v;
    }
    NSPopUpButton *comboIn(NSView *p, NSRect f, NSArray *items)
    {
        NSPopUpButton *v = [[FullClickComboBox alloc] initWithFrame:f pullsDown:NO];
        [v removeAllItems];
        for (NSString *item in items ?: @[]) {
            [v addItemWithTitle:item];
            [[v lastItem] setRepresentedObject:item];
        }
        [v setFont:[NSFont systemFontOfSize:12.0]];
        [p addSubview:v]; [v release]; return v;
    }
    void setButtonTextColor(NSButton *button, NSColor *color)
    {
        if (!button) return;
        NSMutableParagraphStyle *style = [[[NSMutableParagraphStyle alloc] init] autorelease];
        [style setAlignment:NSTextAlignmentCenter];
        [style setLineBreakMode:NSLineBreakByTruncatingTail];
        NSDictionary *attrs = @{
            NSFontAttributeName: [button font] ?: [NSFont systemFontOfSize:12.0],
            NSForegroundColorAttributeName: color ?: cPri(),
            NSParagraphStyleAttributeName: style,
        };
        NSAttributedString *title = [[NSAttributedString alloc] initWithString:[button title] attributes:attrs];
        [button setAlignment:NSTextAlignmentCenter];
        [button setAttributedTitle:title];
        [[button cell] setLineBreakMode:NSLineBreakByTruncatingTail];
        [title release];
    }
    NSButton *checkIn(NSView *p, NSRect f, NSString *title, bool on)
    {
        NSButton *v = [[NSButton alloc] initWithFrame:f];
        [v setButtonType:NSButtonTypeSwitch]; [v setTitle:title];
        [v setState:on ? NSControlStateValueOn : NSControlStateValueOff];
        [v setFont:[NSFont systemFontOfSize:12.0]];
        setButtonTextColor(v, cPri());
        [p addSubview:v]; [v release]; return v;
    }
    NSButton *btnIn(NSView *p, NSRect f, NSString *title, NSInteger action)
    {
        NSButton *v = [[NSButton alloc] initWithFrame:f];
        [v setTitle:title]; [v setBezelStyle:NSBezelStyleRounded];
        [v setFont:[NSFont systemFontOfSize:12.0]];
        setButtonTextColor(v, [NSColor controlTextColor]);
        LlmrEditorTarget *t = [[LlmrEditorTarget alloc] initWithOwner:this action:action];
        [targets_ addObject:t]; [t release];
        [v setTarget:t]; [v setAction:@selector(performAction:)];
        [p addSubview:v]; [v release]; return v;
    }
    NSTextView *chatTextViewIn(NSView *p, NSRect scrollF)
    {
        NSScrollView *sc = [[NSScrollView alloc] initWithFrame:scrollF];
        [sc setHasVerticalScroller:YES]; [sc setBorderType:NSNoBorder];
        [sc setHasHorizontalScroller:NO];
        [sc setAutohidesScrollers:YES];
        [sc setAutoresizingMask:NSViewWidthSizable | NSViewHeightSizable];
        NSTextView *tv = [[LlmrCopyTextView alloc] initWithFrame:NSMakeRect(0,0,scrollF.size.width,scrollF.size.height)];
        [tv setEditable:NO]; [tv setRichText:YES];
        [tv setSelectable:YES];
        [tv setAllowsUndo:NO];
        [tv setBackgroundColor:cChatBg()];
        [tv setTextColor:cPri()];
        [tv setFont:[NSFont systemFontOfSize:12.0]];
        [tv setTypingAttributes:@{
            NSFontAttributeName: [NSFont systemFontOfSize:12.0],
            NSForegroundColorAttributeName: cPri(),
        }];
        [tv setDrawsBackground:YES];
        [tv setAutoresizingMask:NSViewWidthSizable | NSViewHeightSizable];
        [tv setHorizontallyResizable:NO]; [tv setVerticallyResizable:YES];
        [[tv textContainer] setWidthTracksTextView:YES];
        [sc setDocumentView:tv];
        [p addSubview:sc]; [tv release]; [sc release]; return tv;
    }

    // ─── buildEditor ─────────────────────────────────────────
    void buildEditor(CGFloat width, CGFloat height)
    {
        targets_ = [[NSMutableArray alloc] init];
        if (!chatHistory_) {
            chatHistory_ = [[NSMutableAttributedString alloc] init];
        }

        // Chat view (shown by default)
        chatView_ = [[NSView alloc] initWithFrame:NSMakeRect(0, 0, width, height)];
        [chatView_ setAutoresizingMask:NSViewWidthSizable | NSViewHeightSizable];
        [view_ addSubview:chatView_]; [chatView_ release];
        buildChatView(width, height);

        // Settings surface (hosted in a separate fixed-size window)
        settingsView_ = [[NSView alloc] initWithFrame:NSMakeRect(0, 0, width, height)];
        [settingsView_ setAutoresizingMask:NSViewWidthSizable | NSViewHeightSizable];
        [settingsView_ setWantsLayer:YES];
        settingsView_.layer.backgroundColor = cBg().CGColor;
        [settingsView_ setHidden:NO];
        buildSettingsView(width, height);

        loadSettings();
    }

    void buildChatView(CGFloat width, CGFloat height)
    {
        static const CGFloat kHdr = 74.0, kGuide = 34.0, kTabs = 34.0, kBtm = 164.0, kPad = 12.0;

        // Header bar (top-anchored)
        NSView *hdr = [[NSView alloc] initWithFrame:NSMakeRect(0, height - kHdr, width, kHdr)];
        [hdr setWantsLayer:YES]; hdr.layer.backgroundColor = cHdr().CGColor;
        [hdr setAutoresizingMask:NSViewWidthSizable | NSViewMinYMargin];
        [chatView_ addSubview:hdr]; [hdr release];

        labelIn(hdr, @"LLM-r", NSMakeRect(kPad, 41, 56, 26),
                [NSFont boldSystemFontOfSize:18.0], cPri());
        labelIn(hdr, [NSString stringWithFormat:@"v%s", LLMR_VERSION],
                NSMakeRect(kPad + 60, 46, 52, 16),
                [NSFont systemFontOfSize:10.0], cSec());
        chatModelLabel_ = chipIn(hdr, @"● Model missing",
                NSMakeRect(kPad, 10, 160, 22),
                cAccent(),
                [NSColor colorWithCalibratedRed:0.07 green:0.13 blue:0.22 alpha:1.0],
                [NSColor colorWithCalibratedRed:0.18 green:0.42 blue:0.72 alpha:1.0]);
        [chatModelLabel_ setToolTip:@"Provider and model readiness for planning."];
        [chatModelLabel_ setAutoresizingMask:NSViewMaxXMargin | NSViewMaxYMargin];
        chatOscLabel_ = chipIn(hdr, @"● AbletonOSC: not tested",
                NSMakeRect(kPad + 168, 10, 126, 22),
                cPri(),
                [NSColor colorWithCalibratedRed:0.12 green:0.14 blue:0.18 alpha:1.0],
                [NSColor colorWithCalibratedRed:0.30 green:0.35 blue:0.42 alpha:1.0]);
        [chatOscLabel_ setToolTip:@"AbletonOSC connection settings. This is required for ordinary Live actions."];
        chatBridgeLabel_ = chipIn(hdr, @"● Device Bridge: only needed for devices",
                NSMakeRect(kPad + 302, 10, 126, 22),
                cPri(),
                [NSColor colorWithCalibratedRed:0.12 green:0.14 blue:0.18 alpha:1.0],
                [NSColor colorWithCalibratedRed:0.30 green:0.35 blue:0.42 alpha:1.0]);
        [chatBridgeLabel_ setToolTip:@"Device Bridge status. It is only required for browser/device loading actions."];
        chatDryRunLabel_ = chipIn(hdr, @"● Safety: preview only",
                NSMakeRect(kPad + 436, 10, 112, 22),
                cPri(),
                [NSColor colorWithCalibratedRed:0.12 green:0.14 blue:0.18 alpha:1.0],
                [NSColor colorWithCalibratedRed:0.30 green:0.35 blue:0.42 alpha:1.0]);
        [chatDryRunLabel_ setToolTip:@"Safety mode. Preview only runs the plan without changing the Live set; live run sends actions."];

        NSButton *helpBtn = btnIn(hdr, NSMakeRect(width - 274, 38, 74, 28),
                                  @"Help", kLlmrEditorActionOpenHelp);
        [helpBtn setAutoresizingMask:NSViewMinXMargin | NSViewMaxYMargin];
        NSButton *systemPromptsButton = btnIn(hdr, NSMakeRect(width - 192, 38, 108, 28),
                            @"System Prompts", kLlmrEditorActionOpenSystemPrompts);
        [systemPromptsButton setAutoresizingMask:NSViewMinXMargin | NSViewMaxYMargin];
        chatSettingsButton_ = btnIn(hdr, NSMakeRect(width - 80, 38, 68, 28),
                                    @"Settings", kLlmrEditorActionOpenSettings);
        [chatSettingsButton_ setAutoresizingMask:NSViewMinXMargin | NSViewMaxYMargin];

        NSView *guide = [[NSView alloc] initWithFrame:NSMakeRect(0, height - kHdr - kGuide, width, kGuide)];
        [guide setWantsLayer:YES]; guide.layer.backgroundColor = cPanel().CGColor;
        [guide setAutoresizingMask:NSViewWidthSizable | NSViewMinYMargin];
        [chatView_ addSubview:guide]; [guide release];
        labelIn(guide,
                @"Status: Model, AbletonOSC, Device Bridge, Safety. Type a request and click Run.",
                NSMakeRect(kPad, 8, width - 2*kPad, 18),
                [NSFont systemFontOfSize:11.0], cSec());

        NSView *tabs = [[NSView alloc] initWithFrame:NSMakeRect(0, height - kHdr - kGuide - kTabs, width, kTabs)];
        [tabs setWantsLayer:YES]; tabs.layer.backgroundColor = cBg().CGColor;
        [tabs setAutoresizingMask:NSViewWidthSizable | NSViewMinYMargin];
        [chatView_ addSubview:tabs]; [tabs release];

        chatTabButton_ = btnIn(tabs, NSMakeRect(kPad, 4, 86, 26), @"Result", kLlmrEditorActionShowChatTab);
        rawTabButton_ = btnIn(tabs, NSMakeRect(kPad + 92, 4, 96, 26), @"Details", kLlmrEditorActionShowRawTab);

        // Chat history scroll (fills middle, auto-resizes)
        chatHistoryView_ = chatTextViewIn(chatView_,
            NSMakeRect(0, kBtm, width, height - kHdr - kGuide - kTabs - kBtm));
        rawResponseView_ = chatTextViewIn(chatView_,
            NSMakeRect(0, kBtm, width, height - kHdr - kGuide - kTabs - kBtm));
        [[rawResponseView_ enclosingScrollView] setHidden:YES];
        [rawResponseView_ setRichText:NO];
        [rawResponseView_ setTextColor:cPri()];
        [rawResponseView_ setFont:[NSFont userFixedPitchFontOfSize:11.0]];
        [rawResponseView_ setString:@"Execution details and raw JSON will appear here after the model returns a response."];
        if (lastRawResponse_) {
            [rawResponseView_ setString:lastRawResponse_];
        }

        // Restore previous chat history
        if ([chatHistory_ length] > 0) {
            [[chatHistoryView_ textStorage] setAttributedString:chatHistory_];
        }
        showResponseTab(activeRawTab_);

        // Bottom container (bottom-anchored, fixed height)
        NSView *btm = [[NSView alloc] initWithFrame:NSMakeRect(0, 0, width, kBtm)];
        [btm setAutoresizingMask:NSViewWidthSizable | NSViewMaxYMargin];
        [chatView_ addSubview:btm]; [btm release];

        // Status label
        NSString *initialStatus = @"Ready. Type a request and press Plan.";
        NSUserDefaults *defaults = [NSUserDefaults standardUserDefaults];
        NSString *provider = [defaults stringForKey:@"llmr.vst3.provider"] ?: @"";
        NSString *apiKey = [defaults stringForKey:@"llmr.vst3.api_key"] ?: @"";
        if ([provider length] == 0) {
            initialStatus = @"Setup needed: Choose a provider in Settings.";
        } else if (![provider isEqualToString:@"ollama"] && ![provider isEqualToString:@"omlx"] && [apiKey length] == 0) {
            initialStatus = @"Setup needed: add API key in Settings.";
        }
        chatStatusLabel_ = labelIn(btm, initialStatus,
                                   NSMakeRect(kPad, 4, width - kPad*2, 18),
                                   [NSFont systemFontOfSize:11.0], cSec());
        [chatStatusLabel_ setAutoresizingMask:NSViewWidthSizable | NSViewMaxYMargin];

        // Multiline composer (top row of bottom)
        chatInputView_ = promptTextViewIn(btm, NSMakeRect(kPad, 68, width - kPad*2 - 92, 84), &chatInputScrollView_);
        chatPromptPlaceholderLabel_ = noteIn(btm,
            @"Ask LLM-r to create, edit, arrange, mix, or control Live…",
            NSMakeRect(kPad + 8, 132, width - kPad*2 - 108, 16),
            [NSFont systemFontOfSize:12.0], cSec());
        [chatPromptPlaceholderLabel_ setAutoresizingMask:NSViewWidthSizable | NSViewMaxYMargin];
        if ([chatInputView_ respondsToSelector:@selector(setLlmrPlaceholderLabel:)]) {
            [(LlmrPromptTextView *)chatInputView_ setLlmrPlaceholderLabel:chatPromptPlaceholderLabel_];
        }

        chatSendButton_ = btnIn(btm, NSMakeRect(width - kPad - 84, 124, 84, 28),
                                @"Run", kLlmrEditorActionPlan);
        [chatSendButton_ setAutoresizingMask:NSViewMinXMargin | NSViewMaxYMargin];
        [chatSendButton_ setToolTip:@"Plan with the selected model, then run the resulting Ableton actions."];
        chatCancelButton_ = btnIn(btm, NSMakeRect(width - kPad - 84, 90, 84, 28),
                                  @"Cancel", kLlmrEditorActionCancelOperation);
        [chatCancelButton_ setAutoresizingMask:NSViewMinXMargin | NSViewMaxYMargin];
        [chatCancelButton_ setEnabled:NO];
        [chatCancelButton_ setHidden:YES];
        [chatCancelButton_ setToolTip:@"Cancel the current planning or execution request."];

        // Populate model badge from saved settings
        NSUserDefaults *d = [NSUserDefaults standardUserDefaults];
        NSString *savedProv = [d stringForKey:@"llmr.vst3.provider"] ?: @"";
        NSString *savedMdl  = [d stringForKey:@"llmr.vst3.model"] ?: @"";
        if ([savedProv length] > 0 && [savedMdl length] > 0 && chatModelLabel_) {
            [chatModelLabel_ setStringValue:[NSString stringWithFormat:@"%@ / %@", savedProv, savedMdl]];
        }
        refreshReadinessGuidance();
    }

    // ─── buildSettingsView ────────────────────────────────────
    void buildSettingsView(CGFloat width, CGFloat height)
    {
        (void)width;
        (void)height;
        static const CGFloat kSettingsWidth = 920.0;
        static const CGFloat kSettingsHeight = 720.0;
        static const CGFloat kHdr = 48.0, kFooter = 48.0, kPad = 16.0;
        static const CGFloat kLblW = 104.0, kGap = 8.0;
        static const CGFloat kLeftX = 16.0, kColW = 432.0, kRightX = 464.0;
        const CGFloat fldW = kColW - kLblW - kGap;
        [settingsView_ setFrame:NSMakeRect(0, 0, kSettingsWidth, kSettingsHeight)];

        // Header
        NSView *hdr = [[NSView alloc] initWithFrame:NSMakeRect(0, kSettingsHeight - kHdr, kSettingsWidth, kHdr)];
        [hdr setWantsLayer:YES]; hdr.layer.backgroundColor = cHdr().CGColor;
        [hdr setAutoresizingMask:NSViewMinYMargin];
        [settingsView_ addSubview:hdr]; [hdr release];

        labelIn(hdr, @"Settings", NSMakeRect(kPad, 12, 160, 24),
                [NSFont boldSystemFontOfSize:16.0], cPri());
        NSButton *cancelBtn = btnIn(hdr, NSMakeRect(kSettingsWidth - 198, 8, 86, 28),
                                    @"Cancel", kLlmrEditorActionCancelSettings);
        [cancelBtn setAutoresizingMask:NSViewMinXMargin | NSViewMaxYMargin];
        NSButton *saveBtn = btnIn(hdr, NSMakeRect(kSettingsWidth - 104, 8, 88, 28),
                                  @"Save", kLlmrEditorActionSaveSettings);
        [saveBtn setAutoresizingMask:NSViewMinXMargin | NSViewMaxYMargin];

        settingsMainView_ = [[NSView alloc] initWithFrame:NSMakeRect(0, kFooter, kSettingsWidth, kSettingsHeight - kHdr - kFooter)];
        [settingsMainView_ setAutoresizingMask:NSViewNotSizable];
        [settingsMainView_ setWantsLayer:YES]; settingsMainView_.layer.backgroundColor = cBg().CGColor;
        [settingsView_ addSubview:settingsMainView_]; [settingsMainView_ release];

        NSView *footer = [[NSView alloc] initWithFrame:NSMakeRect(0, 0, kSettingsWidth, kFooter)];
        [footer setWantsLayer:YES]; footer.layer.backgroundColor = cHdr().CGColor;
        [settingsView_ addSubview:footer]; [footer release];
        noteIn(footer,
            @"Save applies changes. Cancel restores the previously saved settings.",
            NSMakeRect(kPad, 15, 420, 18),
            [NSFont systemFontOfSize:11.0], cSec());
        NSButton *bottomCancelBtn = btnIn(footer, NSMakeRect(kSettingsWidth - 198, 10, 86, 28),
                                         @"Cancel", kLlmrEditorActionCancelSettings);
        [bottomCancelBtn setAutoresizingMask:NSViewMinXMargin | NSViewMaxYMargin];
        NSButton *bottomSaveBtn = btnIn(footer, NSMakeRect(kSettingsWidth - 104, 10, 88, 28),
                                       @"Save", kLlmrEditorActionSaveSettings);
        [bottomSaveBtn setAutoresizingMask:NSViewMinXMargin | NSViewMaxYMargin];

        CGFloat leftY = kSettingsHeight - kHdr - kFooter - 14.0;
        CGFloat rightY = leftY;

#define SECTION(parent, x, y, title) \
        labelIn(parent, title, NSMakeRect(x, y - 22.0, kColW, 22.0), \
                [NSFont boldSystemFontOfSize:12.0], cAccent()); \
        y -= 30.0;

#define ROW(parent, x, y, label, field_expr) \
        labelIn(parent, label, NSMakeRect(x, y - 28.0, kLblW, 28.0), \
                [NSFont systemFontOfSize:12.0], cSec()); \
        field_expr; \
        y -= 36.0;

        SECTION(settingsMainView_, kLeftX, leftY, @"Provider")
        ROW(settingsMainView_, kLeftX, leftY, @"Provider",
            settingsProviderCombo_ = comboIn(settingsMainView_,
                NSMakeRect(kLeftX + kLblW + kGap, leftY - 28.0, fldW, 28.0),
                providers()))
        LlmrEditorTarget *providerTarget = [[LlmrEditorTarget alloc] initWithOwner:this action:kLlmrEditorActionProviderChanged];
        [targets_ addObject:providerTarget];
        [settingsProviderCombo_ setTarget:providerTarget];
        [settingsProviderCombo_ setAction:@selector(performAction:)];
        [providerTarget release];
        [settingsProviderCombo_ setAutoresizingMask:NSViewMaxYMargin];

        ROW(settingsMainView_, kLeftX, leftY, @"Model",
            settingsModelField_ = comboIn(settingsMainView_,
                NSMakeRect(kLeftX + kLblW + kGap, leftY - 28.0, fldW, 28.0),
                defaultModelsForProvider(@"openai")))
        [settingsModelField_ setAutoresizingMask:NSViewMaxYMargin];

        ROW(settingsMainView_, kLeftX, leftY, @"Custom model",
            settingsCustomModelField_ = fieldIn(settingsMainView_,
                NSMakeRect(kLeftX + kLblW + kGap, leftY - 28.0, fldW, 28.0),
                @"Only for unlisted or custom models", NO))
        [settingsCustomModelField_ setAutoresizingMask:NSViewMaxYMargin];
        settingsModelStatusLabel_ = noteIn(settingsMainView_,
            @"Select a listed model or enter a custom model.",
            NSMakeRect(kLeftX + kLblW + kGap, leftY - 28.0, fldW, 28.0),
            [NSFont systemFontOfSize:11.0], cSec());
        leftY -= 38.0;

        ROW(settingsMainView_, kLeftX, leftY, @"Server",
            settingsEndpointField_ = fieldIn(settingsMainView_,
                NSMakeRect(kLeftX + kLblW + kGap, leftY - 28.0, fldW, 28.0),
                @"Provider default or API base URL", NO))
        [settingsEndpointField_ setAutoresizingMask:NSViewMaxYMargin];

        ROW(settingsMainView_, kLeftX, leftY, @"API key",
            settingsApiKeyField_ = fieldIn(settingsMainView_,
                NSMakeRect(kLeftX + kLblW + kGap, leftY - 28.0, fldW, 28.0),
                @"Cloud providers only", YES))

        SECTION(settingsMainView_, kLeftX, leftY, @"Run behaviour")
        settingsDryRunButton_ = checkIn(settingsMainView_,
            NSMakeRect(kLeftX + kLblW + kGap, leftY - 24.0, 260, 24), @"Preview only; do not change Live", true);
        leftY -= 30.0;
        settingsDestructiveButton_ = checkIn(settingsMainView_,
            NSMakeRect(kLeftX + kLblW + kGap, leftY - 24.0, 220, 24), @"Allow destructive actions", false);
        leftY -= 30.0;
        settingsExtraPromptButton_ = checkIn(settingsMainView_,
            NSMakeRect(kLeftX + kLblW + kGap, leftY - 24.0, 220, 24), @"LLM-r guidance prompt", true);
        leftY -= 38.0;
        btnIn(settingsMainView_, NSMakeRect(kLeftX + kLblW + kGap, leftY - 30.0, 124, 30),
              @"Test readiness", kLlmrEditorActionTestReadiness);
        leftY -= 42.0;
        noteIn(settingsMainView_,
            @"Preview mode is the safety path. Turn it off when you want one-click live execution.",
            NSMakeRect(kLeftX, leftY - 44.0, kColW, 44.0),
            [NSFont systemFontOfSize:11.0], cSec());

        SECTION(settingsMainView_, kRightX, rightY, @"Ableton")
        labelIn(settingsMainView_, @"OSC host", NSMakeRect(kRightX, rightY - 28.0, kLblW, 28.0),
                [NSFont systemFontOfSize:12.0], cSec());
        settingsOscHostField_ = fieldIn(settingsMainView_,
            NSMakeRect(kRightX + kLblW + kGap, rightY - 28.0, 170, 28.0), @"127.0.0.1", NO);
        labelIn(settingsMainView_, @"Port", NSMakeRect(kRightX + kLblW + kGap + 182, rightY - 28.0, 44, 28.0),
                [NSFont systemFontOfSize:12.0], cSec());
        settingsOscPortField_ = fieldIn(settingsMainView_,
            NSMakeRect(kRightX + kLblW + kGap + 232, rightY - 28.0, 90, 28.0), @"11000", NO);
        rightY -= 36.0;

        labelIn(settingsMainView_, @"Bridge host", NSMakeRect(kRightX, rightY - 28.0, kLblW, 28.0),
                [NSFont systemFontOfSize:12.0], cSec());
        settingsBridgeHostField_ = fieldIn(settingsMainView_,
            NSMakeRect(kRightX + kLblW + kGap, rightY - 28.0, 170, 28.0), @"127.0.0.1", NO);
        labelIn(settingsMainView_, @"Port", NSMakeRect(kRightX + kLblW + kGap + 182, rightY - 28.0, 44, 28.0),
                [NSFont systemFontOfSize:12.0], cSec());
        settingsBridgePortField_ = fieldIn(settingsMainView_,
            NSMakeRect(kRightX + kLblW + kGap + 232, rightY - 28.0, 90, 28.0), @"8788", NO);
        rightY -= 36.0;

        labelIn(settingsMainView_, @"Detected", NSMakeRect(kRightX, rightY - 28.0, kLblW, 28.0),
                [NSFont systemFontOfSize:12.0], cSec());
        settingsBridgeLibraryCandidatesCombo_ = comboIn(settingsMainView_,
            NSMakeRect(kRightX + kLblW + kGap, rightY - 28.0, 174.0, 28.0), @[]);
        LlmrEditorTarget *detectedLibraryTarget = [[LlmrEditorTarget alloc] initWithOwner:this action:kLlmrEditorActionUseDetectedBridgeLibrary];
        [targets_ addObject:detectedLibraryTarget];
        [settingsBridgeLibraryCandidatesCombo_ setTarget:detectedLibraryTarget];
        [settingsBridgeLibraryCandidatesCombo_ setAction:@selector(performAction:)];
        [detectedLibraryTarget release];
        btnIn(settingsMainView_, NSMakeRect(kRightX + kLblW + kGap + 182.0, rightY - 28.0, 142, 28),
              @"Choose Ableton User Library…", kLlmrEditorActionChooseBridgeUserLibrary);
        rightY -= 34.0;

        settingsBridgeLibraryLabel_ = noteIn(settingsMainView_,
            @"Selected Ableton User Library: Not selected",
            NSMakeRect(kRightX, rightY - 28.0, kColW, 28.0),
            [NSFont systemFontOfSize:11.0], cSec());
        rightY -= 30.0;
        settingsBridgeInstallTargetLabel_ = noteIn(settingsMainView_,
            @"Bridge install target: Not selected",
            NSMakeRect(kRightX, rightY - 28.0, kColW, 28.0),
            [NSFont systemFontOfSize:11.0], cSec());
        rightY -= 30.0;
        deviceBridgeStatusLabel_ = noteIn(settingsMainView_,
            @"Bridge status: Not installed",
            NSMakeRect(kRightX, rightY - 72.0, kColW, 72.0),
            [NSFont systemFontOfSize:11.0], cSec());
        rightY -= 78.0;

        btnIn(settingsMainView_, NSMakeRect(kRightX, rightY - 28.0, 72, 28), @"Recheck", kLlmrEditorActionDeviceBridgeStatus);
        settingsBridgeInstallButton_ = btnIn(settingsMainView_, NSMakeRect(kRightX + 80, rightY - 28.0, 114, 28), @"Install Bridge", kLlmrEditorActionInstallBridge);
        settingsBridgeRevealButton_ = btnIn(settingsMainView_, NSMakeRect(kRightX + 202, rightY - 28.0, 104, 28), @"Reveal", kLlmrEditorActionRevealInstalledBridge);
        btnIn(settingsMainView_, NSMakeRect(kRightX + 314, rightY - 28.0, 92, 28), @"Copy Path", kLlmrEditorActionCopyBridgeInstallPath);
        rightY -= 34.0;
        btnIn(settingsMainView_, NSMakeRect(kRightX, rightY - 28.0, 132, 28), @"Bridge Setup Help", kLlmrEditorActionOpenBridgeHelp);
        rightY -= 38.0;

        SECTION(settingsMainView_, kRightX, rightY, @"Ollama")
        ollamaStatusLabel_ = noteIn(settingsMainView_,
            @"Ollama: status unknown. Click Refresh Status.",
            NSMakeRect(kRightX, rightY - 34.0, kColW, 34.0),
            [NSFont systemFontOfSize:11.0], cSec());
        rightY -= 40.0;
        btnIn(settingsMainView_, NSMakeRect(kRightX,          rightY - 28.0, 86, 28), @"Start",   kLlmrEditorActionOllamaStart);
        btnIn(settingsMainView_, NSMakeRect(kRightX + 94,     rightY - 28.0, 82, 28), @"Stop",    kLlmrEditorActionOllamaStop);
        btnIn(settingsMainView_, NSMakeRect(kRightX + 184,    rightY - 28.0, 78, 28), @"Install", kLlmrEditorActionOllamaInstall);
        btnIn(settingsMainView_, NSMakeRect(kRightX + 270,    rightY - 28.0, 112, 28), @"Refresh Status", kLlmrEditorActionOllamaListModels);
        rightY -= 36.0;

        labelIn(settingsMainView_, @"Installed model", NSMakeRect(kRightX, rightY - 20.0, 160, 20.0),
                [NSFont systemFontOfSize:11.0], cSec());
        rightY -= 24.0;
        ollamaModelsCombo_ = comboIn(settingsMainView_,
            NSMakeRect(kRightX, rightY - 28.0, 188, 28.0), @[]);
        [ollamaModelsCombo_ setAutoresizingMask:NSViewMaxYMargin];
        btnIn(settingsMainView_, NSMakeRect(kRightX + 198, rightY - 28.0, 58, 28), @"Serve", kLlmrEditorActionOllamaServeModel);
        btnIn(settingsMainView_, NSMakeRect(kRightX + 264, rightY - 28.0, 94, 28), @"Stop Serve", kLlmrEditorActionOllamaStopServingModel);
        btnIn(settingsMainView_, NSMakeRect(kRightX + 366, rightY - 28.0, 52, 28), @"Test", kLlmrEditorActionOllamaTestModel);
        rightY -= 36.0;

        labelIn(settingsMainView_, @"Downloadable model", NSMakeRect(kRightX, rightY - 20.0, 160, 20.0),
                [NSFont systemFontOfSize:11.0], cSec());
        rightY -= 24.0;
        ollamaModelField_ = comboIn(settingsMainView_,
            NSMakeRect(kRightX, rightY - 28.0, 188, 28.0),
            fallbackOllamaDownloadModels());
        [ollamaModelField_ setAutoresizingMask:NSViewMaxYMargin];
        btnIn(settingsMainView_, NSMakeRect(kRightX + 198, rightY - 28.0, 104, 28),
              @"Refresh Online", kLlmrEditorActionOllamaRefreshOnlineModels);
        btnIn(settingsMainView_, NSMakeRect(kRightX + 310, rightY - 28.0, 86, 28),
              @"Download", kLlmrEditorActionOllamaDownloadModel);
        rightY -= 36.0;

        noteIn(settingsMainView_,
            @"oMLX can be selected as a provider. Use the PyQt companion for oMLX runtime management in this release.",
            NSMakeRect(kRightX, rightY - 34.0, kColW, 34.0),
            [NSFont systemFontOfSize:11.0], cSec());

        refreshBridgeLibraryCandidates();
        refreshBridgePathUI();
#undef SECTION
#undef ROW
    }

    void setStatus(NSString *message)
    {
        if (chatStatusLabel_) {
            [chatStatusLabel_ setStringValue:message ?: @""];
        }
    }

    void setComboItems(NSPopUpButton *combo, NSArray *items, NSString *preferred,
                       NSString *emptyTitle = @"No items")
    {
        if (!combo) return;
        [combo removeAllItems];
        NSArray *safeItems = items ?: @[];
        if ([safeItems count] == 0) {
            [combo addItemWithTitle:emptyTitle ?: @"No items"];
            NSMenuItem *item = [combo lastItem];
            [item setRepresentedObject:@""];
            [item setEnabled:NO];
            [combo selectItemAtIndex:0];
            return;
        }
        for (NSString *itemTitle in safeItems) {
            if (![itemTitle isKindOfClass:[NSString class]] || [itemTitle length] == 0) continue;
            [combo addItemWithTitle:itemTitle];
            [[combo lastItem] setRepresentedObject:itemTitle];
        }
        BOOL selected = NO;
        if ([preferred length] > 0) {
            for (NSInteger i = 0; i < [combo numberOfItems]; ++i) {
                NSMenuItem *item = [combo itemAtIndex:i];
                id value = [item representedObject];
                if ([value isKindOfClass:[NSString class]] && [value isEqualToString:preferred]) {
                    [combo selectItemAtIndex:i];
                    selected = YES;
                    break;
                }
            }
        }
        if (!selected && [combo numberOfItems] > 0) {
            [combo selectItemAtIndex:0];
        }
    }

    bool comboContainsValue(NSPopUpButton *combo, NSString *value)
    {
        if (!combo || [value length] == 0) return false;
        for (NSInteger i = 0; i < [combo numberOfItems]; ++i) {
            id represented = [[combo itemAtIndex:i] representedObject];
            if ([represented isKindOfClass:[NSString class]] && [represented isEqualToString:value]) {
                return true;
            }
        }
        return false;
    }

    void selectComboValue(NSPopUpButton *combo, NSString *value)
    {
        if (!combo || [value length] == 0) return;
        for (NSInteger i = 0; i < [combo numberOfItems]; ++i) {
            id represented = [[combo itemAtIndex:i] representedObject];
            if ([represented isKindOfClass:[NSString class]] && [represented isEqualToString:value]) {
                [combo selectItemAtIndex:i];
                return;
            }
        }
    }

    void updateModelBadge()
    {
        if (!chatModelLabel_) return;
        NSString *provider = settingsProviderCombo_ ? controlString(settingsProviderCombo_) : @"";
        NSString *model = resolvedModelForSettings(provider, settingsModelField_ ? controlString(settingsModelField_) : @"");
        NSString *modelBadge = @"Model missing";
        if ([provider length] > 0 && [model length] > 0) {
            modelBadge = [NSString stringWithFormat:@"%@ / %@", provider, model];
        } else if ([provider length] > 0) {
            modelBadge = provider;
        }
        if ([modelBadge length] > 30) {
            modelBadge = [NSString stringWithFormat:@"%@…", [modelBadge substringToIndex:29]];
        }
        [chatModelLabel_ setStringValue:modelBadge];
        refreshReadinessGuidance();
    }

    NSString *promptInputText()
    {
        if (!chatInputView_) return @"";
        NSString *value = [chatInputView_ string] ?: @"";
        return [value stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
    }

    void clearPromptInput()
    {
        if (chatInputView_) {
            [chatInputView_ setString:@""];
        }
        refreshPromptPlaceholder();
    }

    void refreshPromptPlaceholder()
    {
        if (!chatPromptPlaceholderLabel_ || !chatInputView_) return;
        NSString *raw = [chatInputView_ string] ?: @"";
        BOOL empty = [[raw stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]] length] == 0;
        [chatPromptPlaceholderLabel_ setHidden:!empty];
    }

    bool requireDryRunBeforeExecuteSetting()
    {
        if (settingsDryRunButton_) return buttonOn(settingsDryRunButton_);
        NSUserDefaults *d = [NSUserDefaults standardUserDefaults];
        if ([d objectForKey:@"llmr.vst3.require_dry_run_before_execute"]) {
            return [d boolForKey:@"llmr.vst3.require_dry_run_before_execute"];
        }
        if ([d objectForKey:@"llmr.vst3.dry_run"]) {
            return [d boolForKey:@"llmr.vst3.dry_run"];
        }
        return true;
    }

    NSString *deviceBridgeHost()
    {
        NSString *host = settingsBridgeHostField_ ? controlString(settingsBridgeHostField_) : @"";
        if ([host length] == 0) {
            host = [[NSUserDefaults standardUserDefaults] stringForKey:@"llmr.vst3.bridge_host"] ?: @"127.0.0.1";
        }
        return [host length] > 0 ? host : @"127.0.0.1";
    }

    int deviceBridgePort()
    {
        NSInteger port = settingsBridgePortField_ ? [controlString(settingsBridgePortField_) integerValue] : 0;
        if (port <= 0) {
            port = [[NSUserDefaults standardUserDefaults] integerForKey:@"llmr.vst3.bridge_port"];
        }
        if (port <= 0) port = 8788;
        deviceBridgePort_ = static_cast<int>(port);
        return deviceBridgePort_;
    }

    void refreshReadinessGuidance()
    {
        NSString *provider = settingsProviderCombo_ ? controlString(settingsProviderCombo_) :
            ([[NSUserDefaults standardUserDefaults] stringForKey:@"llmr.vst3.provider"] ?: @"");
        NSString *model = resolvedModelForSettings(provider, settingsModelField_ ? controlString(settingsModelField_) :
            ([[NSUserDefaults standardUserDefaults] stringForKey:@"llmr.vst3.model"] ?: @""));
        bool modelReady = [provider length] > 0 && [model length] > 0;
        setChip(chatModelLabel_, modelReady ? @"Model configured" : @"Model missing", modelReady);

        NSString *oscHost = settingsOscHostField_ ? controlString(settingsOscHostField_) :
            ([[NSUserDefaults standardUserDefaults] stringForKey:@"llmr.vst3.osc_host"] ?: @"127.0.0.1");
        NSInteger oscPort = settingsOscPortField_ ? [controlString(settingsOscPortField_) integerValue] :
            [[NSUserDefaults standardUserDefaults] integerForKey:@"llmr.vst3.osc_port"];
        if (oscPort <= 0) oscPort = 11000;
        bool oscConfigured = [oscHost length] > 0 && oscPort > 0;
        setChip(chatOscLabel_, oscConfigured ? @"AbletonOSC: not tested" : @"AbletonOSC: configure host/port", false);

        NSString *bridgeLabel = deviceBridgeChecked_
            ? (deviceBridgeReachable_ ? @"Device Bridge: available" : @"Device Bridge: not reachable")
            : @"Device Bridge: only needed for devices";
        setChip(chatBridgeLabel_, bridgeLabel, deviceBridgeReachable_);

        bool requireDryRun = requireDryRunBeforeExecuteSetting();
        setChip(chatDryRunLabel_, requireDryRun ? @"Safety: preview only" : @"Safety: live run", requireDryRun);
    }

    void testReadiness()
    {
        refreshReadinessGuidance();
        NSString *provider = settingsProviderCombo_ ? controlString(settingsProviderCombo_) : @"";
        NSString *model = resolvedModelForSettings(provider, settingsModelField_ ? controlString(settingsModelField_) : @"");
        if ([provider length] == 0 || [model length] == 0) {
            setStatus(@"Model missing - open Settings and choose a provider/model or enter Custom model.");
            return;
        }
        NSString *oscHost = settingsOscHostField_ ? controlString(settingsOscHostField_) : @"127.0.0.1";
        NSInteger oscPort = settingsOscPortField_ ? [controlString(settingsOscPortField_) integerValue] : 11000;
        if ([oscHost length] == 0 || oscPort <= 0) {
            setStatus(@"AbletonOSC missing - open Settings and set host/port.");
            return;
        }
        setStatus(requireDryRunBeforeExecuteSetting()
            ? @"Readiness: model configured; AbletonOSC not tested; Device Bridge only needed for device loading; preview mode is on."
            : @"Readiness: model configured; AbletonOSC not tested; Device Bridge only needed for device loading; live run is on.");
        checkDeviceBridgeStatus();
    }

    void setBusy(bool busy)
    {
        operationBusy_.store(busy);
        if (chatSendButton_) {
            [chatSendButton_ setEnabled:!busy];
            [chatSendButton_ setTitle:busy ? @"Running" : @"Run"];
        }
        if (chatCancelButton_) {
            [chatCancelButton_ setEnabled:busy];
            [chatCancelButton_ setHidden:!busy];
        }
        if (chatInputView_) {
            [chatInputView_ setEditable:!busy];
        }
        bool hasActions = !busy && lastActions_ && [lastActions_ count] > 0;
        if (chatExecuteButton_) [chatExecuteButton_ setEnabled:hasActions];
        if (chatPreviewButton_) [chatPreviewButton_ setEnabled:hasActions];
    }

    void cancelCurrentOperation()
    {
        if (!operationBusy_.load()) {
            setStatus(@"No process is running.");
            return;
        }
        operationCancelRequested_.store(true);
        setStatus(@"Cancelling...");
    }

    void showSettings()
    {
        if (!settingsView_) return;
        if (!settingsWindow_) {
            NSRect frame = NSMakeRect(0, 0, 920, 720);
            settingsWindow_ = [[NSWindow alloc]
                initWithContentRect:frame
                          styleMask:NSWindowStyleMaskTitled
                            backing:NSBackingStoreBuffered
                              defer:NO];
            [settingsWindow_ setTitle:@"LLM-r Settings"];
            [settingsWindow_ setReleasedWhenClosed:NO];
            [settingsWindow_ setLevel:NSModalPanelWindowLevel];
            [settingsWindow_ setContentView:settingsView_];
        }
        loadSettings();
        ollamaListModels();
        NSWindow *owner = view_ ? [view_ window] : nil;
        if (owner && [settingsWindow_ sheetParent] != owner) {
            [owner beginSheet:settingsWindow_ completionHandler:nil];
        } else {
            [settingsWindow_ makeKeyAndOrderFront:nil];
        }
        [settingsWindow_ makeKeyWindow];
        [NSApp activateIgnoringOtherApps:YES];
    }

    void hideSettings()
    {
        if (settingsWindow_) {
            NSWindow *parent = [settingsWindow_ sheetParent];
            if (parent) {
                [parent endSheet:settingsWindow_];
            }
            [settingsWindow_ orderOut:nil];
        }
    }

    void ensureSystemPromptsWindow()
    {
        if (systemPromptsWindow_) return;

        NSRect frame = NSMakeRect(0, 0, 760, 560);
        systemPromptsWindow_ = [[NSWindow alloc]
            initWithContentRect:frame
                      styleMask:(NSWindowStyleMaskTitled | NSWindowStyleMaskClosable)
                        backing:NSBackingStoreBuffered
                          defer:NO];
        [systemPromptsWindow_ setTitle:@"System Prompts"];
        [systemPromptsWindow_ setReleasedWhenClosed:NO];

        NSView *content = [systemPromptsWindow_ contentView];
        const CGFloat pad = 12.0;
        labelIn(content, @"Preset", NSMakeRect(pad, 524, 64, 24), [NSFont boldSystemFontOfSize:12.0], cPri());
        systemPromptPresetCombo_ = comboIn(content, NSMakeRect(78, 522, 220, 28),
            @[@"Default LLM-r planner", @"Conservative editor", @"Creative composer", @"Arrangement assistant", @"Custom"]);
        LlmrEditorTarget *presetTarget = [[LlmrEditorTarget alloc] initWithOwner:this action:kLlmrEditorActionSystemPromptPresetChanged];
        [targets_ addObject:presetTarget];
        [systemPromptPresetCombo_ setTarget:presetTarget];
        [systemPromptPresetCombo_ setAction:@selector(performAction:)];
        [presetTarget release];
        [systemPromptPresetCombo_ setToolTip:@"Choose the base planner prompt shown in the editor below."];

        NSScrollView *editorScroll = nil;
        systemPromptEditor_ = promptTextViewIn(content, NSMakeRect(pad, 86, 736, 430), &editorScroll);
        [systemPromptEditor_ setFont:[NSFont userFixedPitchFontOfSize:12.0]];
        (void)editorScroll;

        noteIn(content,
            @"Note: planner prompts must output executable LLM-r JSON with explanation, confidence, calls, tool, and args.",
            NSMakeRect(pad, 62, 736, 16),
            [NSFont systemFontOfSize:11.0], cSec());

        btnIn(content, NSMakeRect(pad, 20, 72, 30), @"Save", kLlmrEditorActionSaveSystemPrompt);
        btnIn(content, NSMakeRect(pad + 80, 20, 92, 30), @"Save As…", kLlmrEditorActionSaveSystemPromptAs);
        btnIn(content, NSMakeRect(pad + 180, 20, 76, 30), @"Load…", kLlmrEditorActionLoadSystemPrompt);
        btnIn(content, NSMakeRect(pad + 264, 20, 108, 30), @"Reset Default", kLlmrEditorActionResetSystemPrompt);
        btnIn(content, NSMakeRect(668, 20, 76, 30), @"Cancel", kLlmrEditorActionCancelSystemPrompt);
    }

    void loadSystemPromptEditorState()
    {
        if (!systemPromptEditor_ || !systemPromptPresetCombo_) return;
        NSUserDefaults *d = [NSUserDefaults standardUserDefaults];
        NSString *preset = [d stringForKey:systemPromptPresetKey()] ?: @"Default LLM-r planner";
        selectComboValue(systemPromptPresetCombo_, preset);
        [systemPromptEditor_ setString:selectedSystemPromptBase() ?: defaultSystemPromptBase()];
    }

    void systemPromptPresetChanged()
    {
        if (!systemPromptEditor_ || !systemPromptPresetCombo_) return;
        NSString *preset = controlString(systemPromptPresetCombo_);
        [systemPromptEditor_ setString:systemPromptBaseForPreset(preset) ?: defaultSystemPromptBase()];
    }

    bool systemPromptLooksSafe(NSString *text)
    {
        NSString *lower = [[text ?: @"" lowercaseString] stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
        NSArray *needles = @[@"json", @"calls", @"tool", @"args", @"llm-r"];
        for (NSString *needle in needles) {
            if ([lower containsString:needle]) return true;
        }
        return false;
    }

    bool confirmPotentiallyUnsafeSystemPrompt(NSString *text)
    {
        if (systemPromptLooksSafe(text)) return true;
        NSAlert *alert = [[NSAlert alloc] init];
        [alert setMessageText:@"Prompt may break execution"];
        [alert setInformativeText:@"The prompt does not mention JSON/tool-call concepts. Save anyway?"];
        [alert addButtonWithTitle:@"Save Anyway"];
        [alert addButtonWithTitle:@"Cancel"];
        NSModalResponse response = [alert runModal];
        [alert release];
        return response == NSAlertFirstButtonReturn;
    }

    void openSystemPromptsWindow()
    {
        ensureSystemPromptsWindow();
        loadSystemPromptEditorState();
        [systemPromptsWindow_ makeKeyAndOrderFront:nil];
        [NSApp activateIgnoringOtherApps:YES];
    }

    void closeSystemPromptsWindow()
    {
        if (systemPromptsWindow_) {
            [systemPromptsWindow_ orderOut:nil];
        }
    }

    void saveSystemPromptFromEditor()
    {
        if (!systemPromptEditor_ || !systemPromptPresetCombo_) return;
        NSString *text = [systemPromptEditor_ string] ?: @"";
        if (!confirmPotentiallyUnsafeSystemPrompt(text)) {
            return;
        }
        NSString *preset = controlString(systemPromptPresetCombo_);
        NSUserDefaults *d = [NSUserDefaults standardUserDefaults];
        [d setObject:([preset length] > 0 ? preset : @"Custom") forKey:systemPromptPresetKey()];
        [d setObject:text forKey:systemPromptCustomKey()];
        [d synchronize];
        setStatus(@"System prompt saved.");
        closeSystemPromptsWindow();
    }

    void saveSystemPromptToFile()
    {
        if (!systemPromptEditor_) return;
        NSSavePanel *panel = [NSSavePanel savePanel];
        [panel setAllowedFileTypes:@[@"txt", @"md"]];
        [panel setNameFieldStringValue:@"llmr-system-prompt.md"];
        if ([panel runModal] != NSModalResponseOK) return;
        NSString *text = [systemPromptEditor_ string] ?: @"";
        [text writeToURL:[panel URL] atomically:YES encoding:NSUTF8StringEncoding error:nil];
    }

    void loadSystemPromptFromFile()
    {
        if (!systemPromptEditor_ || !systemPromptPresetCombo_) return;
        NSOpenPanel *panel = [NSOpenPanel openPanel];
        [panel setCanChooseFiles:YES];
        [panel setCanChooseDirectories:NO];
        [panel setAllowsMultipleSelection:NO];
        [panel setAllowedFileTypes:@[@"txt", @"md"]];
        if ([panel runModal] != NSModalResponseOK) return;
        NSString *text = [NSString stringWithContentsOfURL:[panel URL] encoding:NSUTF8StringEncoding error:nil];
        if (!text) return;
        [systemPromptEditor_ setString:text];
        selectComboValue(systemPromptPresetCombo_, @"Custom");
    }

    void resetSystemPromptToDefault()
    {
        if (!systemPromptEditor_ || !systemPromptPresetCombo_) return;
        [systemPromptEditor_ setString:defaultSystemPromptBase()];
        selectComboValue(systemPromptPresetCombo_, @"Default LLM-r planner");
    }

    void refreshSettingsScreenAfterModeToggle(NSResponder *preferredResponder)
    {
        if (!settingsView_) return;
        [settingsView_ setNeedsLayout:YES];
        [settingsView_ layoutSubtreeIfNeeded];
        [settingsView_ setNeedsDisplay:YES];
        [settingsView_ displayIfNeeded];
        NSWindow *window = [settingsView_ window];
        if (!window) return;
        [window recalculateKeyViewLoop];
        if (preferredResponder) {
            [window makeFirstResponder:preferredResponder];
        }
    }

    void showBasicSettings()
    {
        if (settingsMainView_) [settingsMainView_ setHidden:NO];
        if (settingsAdvancedView_) [settingsAdvancedView_ setHidden:NO];
        refreshSettingsScreenAfterModeToggle(settingsProviderCombo_);
    }

    void showAdvancedSettings()
    {
        if (settingsMainView_) [settingsMainView_ setHidden:NO];
        if (settingsAdvancedView_) [settingsAdvancedView_ setHidden:NO];
        refreshSettingsScreenAfterModeToggle(settingsApiKeyField_);
        refreshBridgePathUI();
    }

    void showResponseTab(bool raw)
    {
        NSScrollView *chatScroll = chatHistoryView_ ? [chatHistoryView_ enclosingScrollView] : nil;
        NSScrollView *rawScroll = rawResponseView_ ? [rawResponseView_ enclosingScrollView] : nil;
        if (chatScroll) [chatScroll setHidden:raw];
        if (rawScroll) [rawScroll setHidden:!raw];
        if (chatTabButton_) [chatTabButton_ setState:raw ? NSControlStateValueOff : NSControlStateValueOn];
        if (rawTabButton_) [rawTabButton_ setState:raw ? NSControlStateValueOn : NSControlStateValueOff];
        activeRawTab_ = raw;
    }

    void updateRawResponse(NSString *text)
    {
        [lastRawResponse_ release];
        lastRawResponse_ = [text ? text : @"" retain];
        if (rawResponseView_) {
            [rawResponseView_ setTextColor:cPri()];
            [rawResponseView_ setFont:[NSFont userFixedPitchFontOfSize:11.0]];
            [rawResponseView_ setTypingAttributes:@{
                NSFontAttributeName: [NSFont userFixedPitchFontOfSize:11.0],
                NSForegroundColorAttributeName: cPri(),
            }];
            [rawResponseView_ setString:lastRawResponse_ ?: @""];
        }
    }

    void showTextDialog(NSString *title, NSString *text)
    {
        NSAlert *alert = [[NSAlert alloc] init];
        [alert setMessageText:title ?: @"LLM-r Help"];
        [alert addButtonWithTitle:@"Close"];
        NSScrollView *scroll = [[[NSScrollView alloc] initWithFrame:NSMakeRect(0, 0, 640, 420)] autorelease];
        [scroll setHasVerticalScroller:YES];
        [scroll setHasHorizontalScroller:NO];
        [scroll setAutohidesScrollers:YES];
        NSTextView *body = [[[LlmrCopyTextView alloc] initWithFrame:NSMakeRect(0, 0, 620, 420)] autorelease];
        [body setEditable:NO];
        [body setSelectable:YES];
        [body setRichText:NO];
        [body setFont:[NSFont systemFontOfSize:12.0]];
        [body setString:text ?: @""];
        [body setHorizontallyResizable:NO];
        [[body textContainer] setWidthTracksTextView:YES];
        [scroll setDocumentView:body];
        [alert setAccessoryView:scroll];
        [alert runModal];
        [alert release];
    }

    NSString *bridgeSetupText()
    {
        NSString *library = bridgeUserLibraryPath_ ? bridgeUserLibraryPath_ : @"";
        NSString *target = bridgeInstallTargetForUserLibrary(library);
        if ([target length] == 0) {
            target = @"Not selected";
        }
        return [NSString stringWithFormat:
            @"Device Bridge setup\n\n"
            @"How to find your Ableton User Library:\n"
            @"1. In Live's Browser, right-click User Library.\n"
            @"2. Choose Show in Finder.\n"
            @"3. In LLM-r, click Choose Ableton User Library… and select that folder.\n\n"
            @"Selected User Library:\n%@\n"
            @"Bridge install target:\n%@\n\n"
            @"Setup steps:\n"
            @"1. Click Install / Reinstall Bridge in LLM-r.\n"
            @"2. Restart Ableton Live.\n"
            @"3. Open Settings -> Link, Tempo & MIDI.\n"
            @"4. In a Control Surface slot, choose LLMR_Bridge if it appears.\n"
            @"5. If it does not appear, check Live Log.txt for LLMR, Bridge, RemoteScriptError, Traceback, or ImportError.\n\n"
            @"The User Library may be on an external SSD. This is supported as long as the drive is mounted before launching Live.\n\n"
            @"Fallback (documented only, not preferred):\n"
            @"/Applications/Ableton Live 12 Suite.app/Contents/App-Resources/MIDI Remote Scripts/\n"
            @"This may require admin permissions and may be overwritten by Ableton updates.\n\n"
            @"Device Bridge is optional for core AbletonOSC plans and required for device_load/browser loading.",
            [library length] > 0 ? library : @"Not selected",
            target];
    }

    void refreshBridgeLibraryCandidates()
    {
        if (!settingsBridgeLibraryCandidatesCombo_) return;
        NSArray<NSString *> *candidates = detectedUserLibraryCandidates();
        NSString *preferred = bridgeUserLibraryPath_ ?: @"";
        setComboItems(settingsBridgeLibraryCandidatesCombo_, candidates, preferred, @"No detected libraries");
    }

    void refreshBridgePathUI()
    {
        NSString *library = bridgeUserLibraryPath_ ? bridgeUserLibraryPath_ : @"";
        NSString *target = bridgeInstallTargetForUserLibrary(library);

        if (settingsBridgeLibraryLabel_) {
            [settingsBridgeLibraryLabel_ setStringValue:[NSString stringWithFormat:@"Selected Ableton User Library: %@",
                [library length] > 0 ? library : @"Not selected"]];
        }
        if (settingsBridgeInstallTargetLabel_) {
            [settingsBridgeInstallTargetLabel_ setStringValue:[NSString stringWithFormat:@"Bridge install target: %@",
                [target length] > 0 ? target : @"Not selected"]];
        }

        BOOL hasSelection = [library length] > 0;
        if (settingsBridgeInstallButton_) [settingsBridgeInstallButton_ setEnabled:hasSelection];
        if (settingsBridgeRevealButton_) [settingsBridgeRevealButton_ setEnabled:hasSelection];

        NSString *status = bridgeInstallStatusForUserLibrary(library);
        if (deviceBridgeChecked_ && !deviceBridgeReachable_) {
            NSString *runtimeState = bridgeInitFileExistsForUserLibrary(library)
                ? @"Bridge status: Installed but not reachable"
                : @"Bridge status: Not installed";
            NSString *reachability =
                [NSString stringWithFormat:@"\n\n%@\n"
                @"Device Bridge not reachable.\n"
                @"Likely causes:\n"
                @"- The LLM-r Remote Script is not installed in Ableton's active User Library.\n"
                @"- Live has not been restarted after installation.\n"
                @"- The Remote Script has not been selected in Live Settings -> Link, Tempo & MIDI.\n"
                @"- Ableton blocked the script because of an import/runtime error.\n"
                @"Next actions:\n"
                @"1. Reveal Installed Bridge\n"
                @"2. Copy Install Path\n"
                @"3. Reinstall Bridge\n"
                @"4. Open Bridge Setup Help\n"
                @"5. Recheck Bridge", runtimeState];
            status = [status stringByAppendingString:reachability];
        } else if (deviceBridgeReachable_) {
            status = [status stringByAppendingString:@"\n\nBridge status: Reachable"];
        }
        if (deviceBridgeStatusLabel_) {
            [deviceBridgeStatusLabel_ setStringValue:status];
        }
    }

    void setBridgeUserLibraryPath(NSString *path, bool persist, bool refreshCandidates = false)
    {
        NSString *normalized = normalizedPath(path);
        [bridgeUserLibraryPath_ release];
        bridgeUserLibraryPath_ = ([normalized length] > 0) ? [normalized retain] : nil;
        if (persist) {
            NSUserDefaults *d = [NSUserDefaults standardUserDefaults];
            if (bridgeUserLibraryPath_) {
                [d setObject:bridgeUserLibraryPath_ forKey:bridgeUserLibrarySettingsKey()];
            } else {
                [d removeObjectForKey:bridgeUserLibrarySettingsKey()];
            }
            [d synchronize];
        }
        if (refreshCandidates) {
            refreshBridgeLibraryCandidates();
        }
        refreshBridgePathUI();
    }

    void useDetectedBridgeLibrary()
    {
        NSString *selected = controlString(settingsBridgeLibraryCandidatesCombo_);
        if ([selected length] == 0) {
            setStatus(@"No detected User Library selected.");
            return;
        }
        setBridgeUserLibraryPath(selected, true, false);
        setStatus([NSString stringWithFormat:@"Selected Ableton User Library: %@", selected]);
    }

    void chooseBridgeUserLibrary()
    {
        NSOpenPanel *panel = [NSOpenPanel openPanel];
        [panel setCanChooseFiles:NO];
        [panel setCanChooseDirectories:YES];
        [panel setAllowsMultipleSelection:NO];
        [panel setCanCreateDirectories:NO];
        [panel setMessage:@"Select Ableton User Library folder (not Remote Scripts)."];
        NSString *start = bridgeUserLibraryPath_;
        if ([start length] == 0) {
            start = [detectedUserLibraryCandidates() firstObject] ?: @"";
        }
        if ([start length] > 0) {
            [panel setDirectoryURL:[NSURL fileURLWithPath:start]];
        }
        NSModalResponse response = [panel runModal];
        if (response != NSModalResponseOK) return;
        NSString *selected = normalizedPath([[panel URL] path]);
        if ([selected length] == 0) return;
        setBridgeUserLibraryPath(selected, true, true);
        setStatus([NSString stringWithFormat:@"Selected Ableton User Library: %@", selected]);
    }

    void revealInstalledBridge()
    {
        NSString *target = bridgeInstallTargetForUserLibrary(bridgeUserLibraryPath_);
        if ([target length] == 0) {
            setStatus(@"Choose Ableton User Library first, then reveal install path.");
            return;
        }
        NSFileManager *fm = [NSFileManager defaultManager];
        NSString *toReveal = [fm fileExistsAtPath:target]
            ? target
            : remoteScriptsPathForUserLibrary(bridgeUserLibraryPath_);
        if (![fm fileExistsAtPath:toReveal]) {
            setStatus(@"Install target does not exist yet. Choose User Library and install bridge first.");
            return;
        }
        [[NSWorkspace sharedWorkspace] activateFileViewerSelectingURLs:@[[NSURL fileURLWithPath:toReveal]]];
        setStatus([NSString stringWithFormat:@"Revealed bridge path: %@", toReveal]);
    }

    void openHelp()
    {
        showTextDialog(@"LLM-r first preview help",
            @"First preview in 60 seconds\n\n"
            @"1. Keep Preview only enabled.\n"
            @"2. Open Settings and choose Provider and Model.\n"
            @"3. Enter a simple prompt.\n"
            @"4. Click Run.\n"
            @"5. Review Result and Details.\n"
            @"6. Turn Preview only off in Settings when you want live execution.\n\n"
            @"Example safe prompts\n\n"
            @"- Set tempo to 120 BPM\n"
            @"- Create a MIDI track called Drums\n"
            @"- Load Drum Rack on the selected track (requires Device Bridge)\n\n"
            @"Safety\n\n"
            @"Preview only does not mutate the Live set. Live run sends actions. Destructive actions require explicit approval in Settings.\n\n"
            @"Bridge\n\n"
                @"AbletonOSC handles core commands. Device Bridge handles browser/device loading.\n\n"
                @"How to find your Ableton User Library:\n"
                @"1. In Live's Browser, right-click User Library.\n"
                @"2. Choose Show in Finder.\n"
                @"3. In LLM-r, click Choose Ableton User Library… and select that folder.\n\n"
                @"After installing the bridge:\n"
                @"1. Restart Ableton Live.\n"
                @"2. Open Live Settings -> Link, Tempo & MIDI.\n"
                @"3. In a Control Surface slot, choose LLMR_Bridge if it appears.\n"
                @"4. If it does not appear, check Live Log.txt for LLMR, Bridge, RemoteScriptError, Traceback, or ImportError.\n\n"
                @"The User Library may be on an external SSD. This is supported as long as the drive is mounted before launching Live.");
    }

    void openBridgeSetupHelp()
    {
        showTextDialog(@"Device Bridge setup", bridgeSetupText());
    }

    void copyBridgeInstallPath()
    {
        NSString *path = bridgeInstallTargetForUserLibrary(bridgeUserLibraryPath_);
        if ([path length] == 0) {
            setStatus(@"Choose Ableton User Library first, then copy install path.");
            return;
        }
        NSPasteboard *pasteboard = [NSPasteboard generalPasteboard];
        [pasteboard clearContents];
        [pasteboard setString:path forType:NSPasteboardTypeString];
        setStatus([NSString stringWithFormat:@"Copied Device Bridge install path: %@", path]);
    }

    void installDeviceBridgeFromSettings()
    {
        NSString *library = bridgeUserLibraryPath_ ? bridgeUserLibraryPath_ : @"";
        if ([library length] == 0) {
            setStatus(@"Choose your Ableton User Library first. In Live, right-click User Library in the Browser and choose Show in Finder.");
            refreshBridgePathUI();
            return;
        }

        if (bridgeDoubleNestedForUserLibrary(library)) {
            NSAlert *warning = [[NSAlert alloc] init];
            [warning setMessageText:@"Bridge install structure warning"];
            [warning setInformativeText:@"Bridge appears to be double-nested. Reinstalling will replace it with the correct folder structure."];
            [warning runModal];
            [warning release];
        }

        NSString *error = nil;
        bool ok = installLLMRBridgeToUserLibrary(library, &error);
        NSAlert *done = [[NSAlert alloc] init];
        if (ok) {
            [done setMessageText:@"LLM-r Device Bridge Installed"];
            [done setInformativeText:
                @"Bridge files are installed. Restart Ableton Live and select LLMR_Bridge in Live Settings if it appears."];
            setStatus(@"Bridge files installed on disk. Restart Live and select LLMR_Bridge in Settings -> Link, Tempo & MIDI.");
        } else {
            [done setMessageText:@"Device Bridge Installation Failed"];
            [done setInformativeText:error ?: @"Could not install LLMR_Bridge."];
            setStatus(@"Device Bridge installation failed.");
        }
        [done runModal];
        [done release];
        refreshBridgePathUI();
    }

    void appendToChat(NSString *role, NSString *text)
    {
        if (!chatHistory_) {
            chatHistory_ = [[NSMutableAttributedString alloc] init];
        }
        bool isUser = [role isEqualToString:@"user"];
        NSColor *roleColor = isUser ? cAccent() : cPri();
        NSColor *bodyColor = [NSColor colorWithCalibratedWhite:0.85 alpha:1.0];
        NSDictionary *roleAttrs = @{
            NSFontAttributeName: [NSFont boldSystemFontOfSize:12.0],
            NSForegroundColorAttributeName: roleColor,
        };
        NSDictionary *bodyAttrs = @{
            NSFontAttributeName: [NSFont systemFontOfSize:12.0],
            NSForegroundColorAttributeName: bodyColor,
        };
        NSString *prefix = ([chatHistory_ length] > 0) ? @"\n\n" : @"";
        NSString *label  = isUser ? @"You" : @"Assistant";
        NSAttributedString *sep  = [[NSAttributedString alloc] initWithString:prefix attributes:bodyAttrs];
        NSAttributedString *hdr  = [[NSAttributedString alloc]
            initWithString:[NSString stringWithFormat:@"%@\n", label] attributes:roleAttrs];
        NSAttributedString *body = [[NSAttributedString alloc] initWithString:text attributes:bodyAttrs];
        [chatHistory_ appendAttributedString:sep];
        [chatHistory_ appendAttributedString:hdr];
        [chatHistory_ appendAttributedString:body];
        [sep release]; [hdr release]; [body release];
        if (chatHistoryView_) {
            [[chatHistoryView_ textStorage] setAttributedString:chatHistory_];
            [chatHistoryView_ scrollToEndOfDocument:nil];
        }
    }

    void loadSettings()
    {
        if (!settingsProviderCombo_) return;
        NSUserDefaults *d = [NSUserDefaults standardUserDefaults];
        NSString *prov = canonicalProvider([d stringForKey:@"llmr.vst3.provider"] ?: @"openai");
        NSString *mdl  = [d stringForKey:@"llmr.vst3.model"] ?: @"gpt-4.1-mini";
        NSString *ep   = resolvedEndpointForSettings(prov, [d stringForKey:@"llmr.vst3.endpoint"] ?: @"");
        NSString *key  = [d stringForKey:@"llmr.vst3.api_key"] ?: @"";
        NSString *host = [d stringForKey:@"llmr.vst3.osc_host"] ?: @"127.0.0.1";
        NSInteger port = [d integerForKey:@"llmr.vst3.osc_port"];
        if (port <= 0) port = 11000;
        NSString *bridgeHost = [d stringForKey:@"llmr.vst3.bridge_host"] ?: @"127.0.0.1";
        NSInteger bridgePort = [d integerForKey:@"llmr.vst3.bridge_port"];
        NSString *bridgeUserLibrary = normalizedPath([d stringForKey:bridgeUserLibrarySettingsKey()] ?: @"");
        if (bridgePort <= 0) bridgePort = 8788;
        deviceBridgePort_ = static_cast<int>(bridgePort);
        selectComboValue(settingsProviderCombo_, prov);
        rebuildModelChoices(prov, mdl, true);
        [settingsEndpointField_ setStringValue:ep];
        [settingsApiKeyField_   setStringValue:key];
        [settingsOscHostField_  setStringValue:host];
        [settingsOscPortField_  setStringValue:[NSString stringWithFormat:@"%ld", (long)port]];
        [settingsBridgeHostField_ setStringValue:bridgeHost];
        [settingsBridgePortField_ setStringValue:[NSString stringWithFormat:@"%ld", (long)bridgePort]];
        setBridgeUserLibraryPath(bridgeUserLibrary, false, false);
        bool extraOn = [d objectForKey:@"llmr.vst3.extra_prompt_enabled"]
                       ? [d boolForKey:@"llmr.vst3.extra_prompt_enabled"] : true;
        bool dryOn   = [d objectForKey:@"llmr.vst3.require_dry_run_before_execute"]
                   ? [d boolForKey:@"llmr.vst3.require_dry_run_before_execute"]
                   : ([d objectForKey:@"llmr.vst3.dry_run"] ? [d boolForKey:@"llmr.vst3.dry_run"] : true);
        bool autoOn  = [d objectForKey:@"llmr.vst3.auto_approve"]
                       ? [d boolForKey:@"llmr.vst3.auto_approve"] : false;
        [settingsExtraPromptButton_ setState:extraOn ? NSControlStateValueOn : NSControlStateValueOff];
        [settingsDestructiveButton_ setState:[d boolForKey:@"llmr.vst3.allow_destructive"]
                                               ? NSControlStateValueOn : NSControlStateValueOff];
        [settingsDryRunButton_      setState:dryOn  ? NSControlStateValueOn : NSControlStateValueOff];
        [settingsAutoApproveButton_ setState:autoOn ? NSControlStateValueOn : NSControlStateValueOff];
        if (chatAutoApproveButton_) {
            [chatAutoApproveButton_ setState:autoOn ? NSControlStateValueOn : NSControlStateValueOff];
        }
        updateModelBadge();
    }

    void rebuildModelChoices(NSString *provider, NSString *preferred, bool allowCustomPreferred = true)
    {
        if (!settingsModelField_) return;
        NSString *p = [(provider ? provider : @"openai") lowercaseString];
        NSMutableArray *models = [NSMutableArray array];
        if ([p isEqualToString:@"ollama"] && ollamaModelsCombo_) {
            for (NSInteger i = 0; i < [ollamaModelsCombo_ numberOfItems]; ++i) {
                NSString *item = @"";
                id represented = [[ollamaModelsCombo_ itemAtIndex:i] representedObject];
                if ([represented isKindOfClass:[NSString class]]) item = represented;
                if ([item length] > 0) [models addObject:item];
            }
        }
        if ([models count] == 0) {
            [models addObjectsFromArray:defaultModelsForProvider(p)];
        }
        NSString *message = @"Select a listed model or enter a custom model if needed.";
        NSString *emptyTitle = @"No listed models";
        BOOL preferredIsListed = [preferred length] > 0 && [models containsObject:preferred];
        setComboItems(settingsModelField_, models, preferredIsListed ? preferred : nil, emptyTitle);
        if (settingsCustomModelField_) {
            [settingsCustomModelField_ setStringValue:
                (!preferredIsListed && allowCustomPreferred && [preferred length] > 0) ? preferred : @""];
        }
        if ([models count] == 0) {
            if ([p isEqualToString:@"custom"]) {
                message = @"Enter a custom model and Server URL.";
            } else {
                message = @"Could not list models for this provider. Enter a custom model or use PyQt settings.";
            }
        } else if (!preferredIsListed && allowCustomPreferred && [preferred length] > 0) {
            message = @"Saved model is not in the provider list. It is kept in Custom model.";
        }
        if (settingsModelStatusLabel_) {
            [settingsModelStatusLabel_ setStringValue:message];
        }
    }

    bool endpointLooksDefault(NSString *endpoint)
    {
        NSString *value = [endpoint stringByTrimmingCharactersInSet:
                           [NSCharacterSet whitespaceAndNewlineCharacterSet]];
        if ([value length] == 0) return true;
        for (NSString *provider in providers()) {
            if ([value isEqualToString:defaultEndpointForProvider(provider)]) {
                return true;
            }
        }
        return false;
    }

    NSString *resolvedEndpointForSettings(NSString *provider, NSString *endpoint)
    {
        NSString *p = canonicalProvider(provider);
        NSString *raw = endpoint ? endpoint : @"";
        NSString *value = [raw stringByTrimmingCharactersInSet:
                           [NSCharacterSet whitespaceAndNewlineCharacterSet]];
        if (providerHasManagedEndpoint(p) && ([value length] == 0 || endpointLooksDefault(value))) {
            return defaultEndpointForProvider(p);
        }
        return value;
    }

    NSString *resolvedModelForSettings(NSString *provider, NSString *model)
    {
        NSString *p = canonicalProvider(provider);
        NSString *customRaw = settingsCustomModelField_ ? controlString(settingsCustomModelField_) : @"";
        NSString *customValue = [customRaw stringByTrimmingCharactersInSet:
                           [NSCharacterSet whitespaceAndNewlineCharacterSet]];
        if ([customValue length] > 0) return customValue;
        NSString *raw = model ? model : @"";
        NSString *value = [raw stringByTrimmingCharactersInSet:
                           [NSCharacterSet whitespaceAndNewlineCharacterSet]];
        if ([value length] > 0) return value;
        if ([p isEqualToString:@"ollama"] && ollamaModelsCombo_) {
            NSString *selected = controlString(ollamaModelsCombo_);
            if ([selected length] > 0) return selected;
        }
        NSArray *defaults = defaultModelsForProvider(p);
        return [defaults count] > 0 ? [defaults objectAtIndex:0] : value;
    }

    void providerChanged()
    {
        NSString *provider = canonicalProvider(controlString(settingsProviderCombo_));
        selectComboValue(settingsProviderCombo_, provider);
        if (settingsCustomModelField_) [settingsCustomModelField_ setStringValue:@""];
        rebuildModelChoices(provider, nil, false);
        if (settingsEndpointField_) {
            NSString *endpoint = resolvedEndpointForSettings(provider, controlString(settingsEndpointField_));
            [settingsEndpointField_ setStringValue:endpoint];
        }
        if ([provider isEqualToString:@"ollama"]) {
            ollamaListModels();
        }
        refreshReadinessGuidance();
    }

    void saveSettings()
    {
        if (!settingsProviderCombo_) return;
        NSUserDefaults *d = [NSUserDefaults standardUserDefaults];
        NSString *provider = canonicalProvider(controlString(settingsProviderCombo_));
        NSString *model = resolvedModelForSettings(provider, controlString(settingsModelField_));
        NSString *endpoint = resolvedEndpointForSettings(provider, controlString(settingsEndpointField_));
        selectComboValue(settingsProviderCombo_, provider);
        if (comboContainsValue(settingsModelField_, model)) {
            selectComboValue(settingsModelField_, model);
            if (settingsCustomModelField_) [settingsCustomModelField_ setStringValue:@""];
        } else if (settingsCustomModelField_) {
            [settingsCustomModelField_ setStringValue:model ?: @""];
        }
        [settingsEndpointField_ setStringValue:endpoint];
        [d setObject:provider forKey:@"llmr.vst3.provider"];
        [d setObject:model forKey:@"llmr.vst3.model"];
        [d setObject:endpoint forKey:@"llmr.vst3.endpoint"];
        [d setObject:controlString(settingsApiKeyField_)   forKey:@"llmr.vst3.api_key"];
        [d setObject:controlString(settingsOscHostField_)  forKey:@"llmr.vst3.osc_host"];
        [d setInteger:[controlString(settingsOscPortField_) integerValue] forKey:@"llmr.vst3.osc_port"];
        [d setObject:controlString(settingsBridgeHostField_) forKey:@"llmr.vst3.bridge_host"];
        [d setInteger:[controlString(settingsBridgePortField_) integerValue] forKey:@"llmr.vst3.bridge_port"];
        if (bridgeUserLibraryPath_ && [bridgeUserLibraryPath_ length] > 0) {
            [d setObject:bridgeUserLibraryPath_ forKey:bridgeUserLibrarySettingsKey()];
        } else {
            [d removeObjectForKey:bridgeUserLibrarySettingsKey()];
        }
        [d setBool:buttonOn(settingsExtraPromptButton_) forKey:@"llmr.vst3.extra_prompt_enabled"];
        [d setBool:buttonOn(settingsDestructiveButton_) forKey:@"llmr.vst3.allow_destructive"];
        [d setBool:buttonOn(settingsDryRunButton_)      forKey:@"llmr.vst3.require_dry_run_before_execute"];
        if (settingsAutoApproveButton_) {
            [d setBool:buttonOn(settingsAutoApproveButton_) forKey:@"llmr.vst3.auto_approve"];
        }
        [d synchronize];
        if (chatAutoApproveButton_) {
            [chatAutoApproveButton_ setState:buttonOn(settingsAutoApproveButton_) ? NSControlStateValueOn : NSControlStateValueOff];
        }
        updateModelBadge();
    }

    void saveAutoApproveSetting()
    {
        NSUserDefaults *d = [NSUserDefaults standardUserDefaults];
        bool enabled = buttonOn(chatAutoApproveButton_);
        [d setBool:enabled forKey:@"llmr.vst3.auto_approve"];
        [d synchronize];
        if (settingsAutoApproveButton_) {
            [settingsAutoApproveButton_ setState:enabled ? NSControlStateValueOn : NSControlStateValueOff];
        }
        if (enabled) {
            setStatus(@"Auto-approve enabled. Plans run after planning using the preview setting.");
        } else {
            setStatus(@"Auto-approve disabled.");
        }
    }

    void cancelSettings()
    {
        loadSettings();
        hideSettings();
    }

    // ─── Ollama operations ────────────────────────────────────
    NSString *httpRequest(NSString *urlString, NSString *method, NSDictionary *body,
                          NSDictionary *headers, NSTimeInterval timeout,
                          NSInteger *statusCode, NSString **error)
    {
        if ([NSThread isMainThread]) {
            if (statusCode) *statusCode = 0;
            if (error) *error = @"Internal error: blocking HTTP request attempted on the UI thread.";
            return nil;
        }
        NSURL *url = [NSURL URLWithString:urlString];
        if (!url) {
            if (error) *error = @"Invalid URL.";
            return nil;
        }
        NSMutableURLRequest *request = [NSMutableURLRequest requestWithURL:url
                                                               cachePolicy:NSURLRequestReloadIgnoringLocalCacheData
                                                           timeoutInterval:timeout];
        [request setHTTPMethod:method ?: @"GET"];
        for (NSString *key in headers) {
            [request setValue:[headers objectForKey:key] forHTTPHeaderField:key];
        }
        if (body) {
            [request setValue:@"application/json" forHTTPHeaderField:@"Content-Type"];
            NSData *data = [NSJSONSerialization dataWithJSONObject:body options:0 error:nil];
            [request setHTTPBody:data];
        }

        __block NSData *responseData = nil;
        __block NSError *requestError = nil;
        __block NSHTTPURLResponse *httpResponse = nil;
        dispatch_semaphore_t semaphore = dispatch_semaphore_create(0);
        NSURLSessionDataTask *task = [[NSURLSession sharedSession]
            dataTaskWithRequest:request
              completionHandler:^(NSData *data, NSURLResponse *response, NSError *err) {
                  responseData = [data retain];
                  requestError = [err retain];
                  httpResponse = [(NSHTTPURLResponse *)response retain];
                  dispatch_semaphore_signal(semaphore);
              }];
        [task resume];
        long waitResult = dispatch_semaphore_wait(
            semaphore,
            dispatch_time(DISPATCH_TIME_NOW, (int64_t)(90.0 * NSEC_PER_SEC)));
        if (waitResult != 0) {
            [task cancel];
            if (error) {
                *error = @"LLM request timed out after 90 seconds.";
            }
            return nil;
        }

        if (statusCode) *statusCode = httpResponse ? [httpResponse statusCode] : 0;
        NSString *text = responseData
            ? [[NSString alloc] initWithData:responseData encoding:NSUTF8StringEncoding]
            : [@"" retain];
        if (requestError && error) {
            *error = [requestError localizedDescription];
        } else if (httpResponse && ([httpResponse statusCode] < 200 || [httpResponse statusCode] >= 300) && error) {
            *error = [NSString stringWithFormat:@"HTTP %ld: %@",
                      static_cast<long>([httpResponse statusCode]), text ?: @""];
        }
        [responseData release];
        [requestError release];
        [httpResponse release];
        return [text autorelease];
    }

    NSString *cleanModelName(id value)
    {
        NSString *raw = [[NSString stringWithFormat:@"%@", value ?: @""]
            stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
        if ([raw length] == 0) return @"";
        NSArray *parts = [raw componentsSeparatedByCharactersInSet:[NSCharacterSet whitespaceCharacterSet]];
        NSString *name = [parts count] > 0 ? [parts objectAtIndex:0] : raw;
        if ([name length] == 0 || [name isEqualToString:@"NAME"] || [name isEqualToString:@"MODEL"]) {
            return @"";
        }
        return name;
    }

    NSArray *modelNamesFromOllamaJSON(NSString *jsonText)
    {
        if ([jsonText length] == 0) return @[];
        NSData *data = [jsonText dataUsingEncoding:NSUTF8StringEncoding];
        id json = [NSJSONSerialization JSONObjectWithData:data options:0 error:nil];
        NSArray *items = [json isKindOfClass:[NSDictionary class]] ? [json objectForKey:@"models"] : nil;
        NSMutableArray *models = [NSMutableArray array];
        for (NSDictionary *item in items) {
            if (![item isKindOfClass:[NSDictionary class]]) continue;
            NSString *name = cleanModelName([item objectForKey:@"name"] ?: [item objectForKey:@"model"]);
            if ([name length] > 0 && ![models containsObject:name]) {
                [models addObject:name];
            }
        }
        return models;
    }

    NSArray *modelNamesFromOllamaLibraryHTML(NSString *html)
    {
        if ([html length] == 0) return @[];
        NSRegularExpression *re = [NSRegularExpression
            regularExpressionWithPattern:@"href=\"/library/([A-Za-z0-9._-]+)\""
                                 options:0 error:nil];
        NSArray *matches = [re matchesInString:html options:0 range:NSMakeRange(0, [html length])];
        NSMutableArray *models = [NSMutableArray array];
        for (NSTextCheckingResult *match in matches) {
            if ([match numberOfRanges] < 2) continue;
            NSString *name = [html substringWithRange:[match rangeAtIndex:1]];
            if ([name length] > 0 && ![models containsObject:name]) {
                [models addObject:name];
            }
        }
        return models;
    }

    NSString *ollamaExecutablePath()
    {
        NSArray *candidates = @[
            @"/opt/homebrew/bin/ollama",
            @"/usr/local/bin/ollama",
            @"/Applications/Ollama.app/Contents/Resources/ollama",
            @"/usr/bin/ollama",
        ];
        NSFileManager *fm = [NSFileManager defaultManager];
        for (NSString *path in candidates) {
            if ([fm isExecutableFileAtPath:path]) return path;
        }
        return nil;
    }

    void ollamaStart()
    {
        if (ollamaStatusLabel_) [ollamaStatusLabel_ setStringValue:@"Ollama: starting..."];
        NSString *exe = [ollamaExecutablePath() retain];
        BOOL openApp = (!exe && [[NSFileManager defaultManager] fileExistsAtPath:@"/Applications/Ollama.app"]);
        dispatch_async(dispatch_get_global_queue(QOS_CLASS_UTILITY, 0), ^{
            @autoreleasepool {
                if (exe) {
                    NSTask *task = [[NSTask alloc] init];
                    [task setLaunchPath:exe];
                    [task setArguments:@[@"serve"]];
                    [task setStandardOutput:[NSFileHandle fileHandleWithNullDevice]];
                    [task setStandardError:[NSFileHandle fileHandleWithNullDevice]];
                    @try { [task launch]; } @catch (NSException *) {}
                    [task release];
                } else if (openApp) {
                    dispatch_sync(dispatch_get_main_queue(), ^{
                        [[NSWorkspace sharedWorkspace] openURL:[NSURL fileURLWithPath:@"/Applications/Ollama.app"]];
                    });
                }
                [exe release];
                [NSThread sleepForTimeInterval:1.5];
                dispatch_async(dispatch_get_main_queue(), ^{
                    ollamaListModels();
                });
            }
        });
    }

    void ollamaStop()
    {
        if (ollamaStatusLabel_) [ollamaStatusLabel_ setStringValue:@"Ollama: stopping..."];
        dispatch_async(dispatch_get_global_queue(QOS_CLASS_UTILITY, 0), ^{
            @autoreleasepool {
                NSTask *task = [[NSTask alloc] init];
                [task setLaunchPath:@"/usr/bin/pkill"];
                [task setArguments:@[@"-x", @"ollama"]];
                @try { [task launch]; [task waitUntilExit]; } @catch (NSException *) {}
                [task release];
                [NSThread sleepForTimeInterval:0.8];
                dispatch_async(dispatch_get_main_queue(), ^{
                    ollamaListModels();
                });
            }
        });
    }

    void ollamaInstall()
    {
        [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"https://ollama.com/download"]];
        if (ollamaStatusLabel_)
            [ollamaStatusLabel_ setStringValue:@"Ollama: opening installer page. Install, then click Start Ollama."];
    }

    void ollamaListModels()
    {
        if (ollamaListInFlight_) {
            if (ollamaStatusLabel_) [ollamaStatusLabel_ setStringValue:@"Ollama: already checking status..."];
            setStatus(@"Already checking Ollama status...");
            return;
        }
        ollamaListInFlight_ = true;
        if (ollamaStatusLabel_) [ollamaStatusLabel_ setStringValue:@"Ollama: checking local service..."];
        addRef();
        dispatch_async(dispatch_get_global_queue(QOS_CLASS_UTILITY, 0), ^{
            @autoreleasepool {
                NSString *error = nil;
                NSInteger code = 0;
                NSString *tags = httpRequest(@"http://127.0.0.1:11434/api/tags", @"GET", nil, nil, 8.0, &code, &error);
                BOOL running = (code >= 200 && code < 300 && !error);
                NSArray *installed = running ? modelNamesFromOllamaJSON(tags) : @[];

                NSString *psError = nil;
                NSInteger psCode = 0;
                NSString *ps = running ? httpRequest(@"http://127.0.0.1:11434/api/ps", @"GET", nil, nil, 8.0, &psCode, &psError) : nil;
                NSArray *served = (psCode >= 200 && psCode < 300 && !psError) ? modelNamesFromOllamaJSON(ps) : @[];

                NSString *status = nil;
                if (running) {
                    NSString *servingNote = [served count] > 0
                        ? [NSString stringWithFormat:@"Active: %@.", [served componentsJoinedByString:@", "]]
                        : @"No model loaded yet — loads on demand when you send a request.";
                    status = [NSString stringWithFormat:@"Ollama: running. Installed: %lu model(s). %@",
                              (unsigned long)[installed count], servingNote];
                } else {
                    NSString *reason = [error length] > 0 ? error : @"local API did not respond";
                    status = [NSString stringWithFormat:@"Ollama: not running (%@). Start Ollama to list installed models.", reason];
                }

                __block NSArray *rm = [installed retain];
                __block NSString *rs = [status retain];
                dispatch_async(dispatch_get_main_queue(), ^{
                    ollamaListInFlight_ = false;
                    NSString *preferred = ollamaModelsCombo_ ? controlString(ollamaModelsCombo_) : @"";
                    setComboItems(ollamaModelsCombo_, rm, preferred);
                    if (settingsProviderCombo_ &&
                        [[controlString(settingsProviderCombo_) lowercaseString] isEqualToString:@"ollama"]) {
                        rebuildModelChoices(@"ollama", resolvedModelForSettings(@"ollama", controlString(settingsModelField_)), true);
                    }
                    if (ollamaStatusLabel_) [ollamaStatusLabel_ setStringValue:rs];
                    [rm release]; [rs release];
                    this->release();
                });
            }
        });
    }

    void ollamaRefreshOnlineModels(bool userInitiated)
    {
        if (ollamaOnlineLoadInFlight_) return;
        ollamaOnlineLoadInFlight_ = true;
        if (userInitiated && ollamaStatusLabel_) {
            [ollamaStatusLabel_ setStringValue:@"Ollama: loading online model catalog..."];
        }
        addRef();
        dispatch_async(dispatch_get_global_queue(QOS_CLASS_UTILITY, 0), ^{
            @autoreleasepool {
                NSString *error = nil;
                NSInteger code = 0;
                NSString *html = httpRequest(@"https://ollama.com/library", @"GET", nil, nil, 18.0, &code, &error);
                NSArray *models = modelNamesFromOllamaLibraryHTML(html);
                BOOL fromNetwork = ([models count] > 0);
                if (!fromNetwork) {
                    models = fallbackOllamaDownloadModels();
                }
                NSString *status = fromNetwork
                    ? [NSString stringWithFormat:@"Ollama: loaded %lu online downloadable model(s).",
                       (unsigned long)[models count]]
                    : (userInitiated
                        ? @"Ollama: online catalog unavailable; showing built-in fallback models."
                        : @"Ollama: showing built-in fallback downloadable models.");
                __block NSArray *rm = [models retain];
                __block NSString *rs = [status retain];
                dispatch_async(dispatch_get_main_queue(), ^{
                    NSString *preferred = ollamaModelField_ ? controlString(ollamaModelField_) : @"";
                    setComboItems(ollamaModelField_, rm, preferred);
                    ollamaOnlineModelsLoaded_ = fromNetwork;
                    ollamaOnlineLoadInFlight_ = false;
                    if (userInitiated && ollamaStatusLabel_) [ollamaStatusLabel_ setStringValue:rs];
                    [rm release]; [rs release];
                    this->release();
                });
            }
        });
    }

    void ollamaDownloadModel()
    {
        NSString *name = ollamaModelField_ ? [controlString(ollamaModelField_) copy] : nil;
        if (!name || [name length] == 0) {
            if (ollamaStatusLabel_) [ollamaStatusLabel_ setStringValue:@"Choose a downloadable Ollama model first."];
            [name release]; return;
        }
        if (ollamaStatusLabel_)
            [ollamaStatusLabel_ setStringValue:[NSString stringWithFormat:@"Ollama: pulling %@...", name]];
        addRef();
        dispatch_async(dispatch_get_global_queue(QOS_CLASS_UTILITY, 0), ^{
            @autoreleasepool {
                NSDictionary *body = @{@"model": name, @"stream": @NO};
                NSString *error = nil;
                NSInteger code = 0;
                NSString *out = httpRequest(@"http://127.0.0.1:11434/api/pull", @"POST", body, nil, 3600.0, &code, &error);
                BOOL ok = (code >= 200 && code < 300 && !error);
                if (ok && [out length] > 0 && ![out containsString:@"success"]) {
                    ok = NO;
                }
                NSString *status = ok
                    ? [NSString stringWithFormat:@"Ollama: %@ downloaded.", name]
                    : [NSString stringWithFormat:@"Ollama: download failed for %@. %@", name, error ?: @"Check that Ollama is running."];
                __block NSString *rs = [status retain];
                [name release];
                dispatch_async(dispatch_get_main_queue(), ^{
                    if (ollamaStatusLabel_) [ollamaStatusLabel_ setStringValue:rs];
                    [rs release];
                    ollamaListModels();
                    this->release();
                });
            }
        });
    }

    void ollamaServeModel()
    {
        NSString *name = ollamaModelsCombo_ ? [[controlString(ollamaModelsCombo_) copy] autorelease] : @"";
        if (!name || [name length] == 0) {
            if (ollamaStatusLabel_) [ollamaStatusLabel_ setStringValue:@"Choose an installed model to serve."];
            return;
        }
        if (settingsProviderCombo_) selectComboValue(settingsProviderCombo_, @"ollama");
        if (settingsCustomModelField_) [settingsCustomModelField_ setStringValue:@""];
        if (settingsModelField_) {
            rebuildModelChoices(@"ollama", name, true);
            selectComboValue(settingsModelField_, name);
        }
        if (settingsEndpointField_) [settingsEndpointField_ setStringValue:defaultEndpointForProvider(@"ollama")];
        if (ollamaStatusLabel_) [ollamaStatusLabel_ setStringValue:[NSString stringWithFormat:@"Ollama: serving %@...", name]];
        runOllamaGenerate(name, @"30m", @"Ollama: model is being served.");
    }

    void ollamaStopServingModel()
    {
        NSString *name = ollamaModelsCombo_ ? [[controlString(ollamaModelsCombo_) copy] autorelease] : @"";
        if (!name || [name length] == 0) {
            if (ollamaStatusLabel_) [ollamaStatusLabel_ setStringValue:@"Choose an installed model to stop serving."];
            return;
        }
        if (ollamaStatusLabel_) [ollamaStatusLabel_ setStringValue:[NSString stringWithFormat:@"Ollama: stopping %@...", name]];
        runOllamaGenerate(name, @0, @"Ollama: model stopped.");
    }

    void ollamaTestModel()
    {
        NSString *name = ollamaModelsCombo_ ? [controlString(ollamaModelsCombo_) copy] : nil;
        if (!name || [name length] == 0) {
            if (ollamaStatusLabel_) [ollamaStatusLabel_ setStringValue:@"Choose an installed model to test."];
            [name release]; return;
        }
        if (ollamaStatusLabel_) [ollamaStatusLabel_ setStringValue:[NSString stringWithFormat:@"Ollama: testing %@...", name]];
        addRef();
        dispatch_async(dispatch_get_global_queue(QOS_CLASS_UTILITY, 0), ^{
            @autoreleasepool {
                NSDictionary *body = @{
                    @"model": name,
                    @"prompt": @"Reply exactly with: LLM-r Ollama test OK",
                    @"stream": @NO,
                    @"keep_alive": @"5m",
                };
                NSString *error = nil;
                NSInteger code = 0;
                NSString *out = httpRequest(@"http://127.0.0.1:11434/api/generate", @"POST", body, nil, 120.0, &code, &error);
                NSData *data = [out dataUsingEncoding:NSUTF8StringEncoding];
                NSDictionary *json = data ? [NSJSONSerialization JSONObjectWithData:data options:0 error:nil] : nil;
                NSString *reply = [json isKindOfClass:[NSDictionary class]] ? [json objectForKey:@"response"] : nil;
                BOOL ok = (code >= 200 && code < 300 && !error && [reply length] > 0);
                NSString *status = ok
                    ? [NSString stringWithFormat:@"Ollama: test succeeded with %@. Reply: %@", name, reply]
                    : [NSString stringWithFormat:@"Ollama: test failed for %@. %@", name, error ?: @"No response."];
                __block NSString *rs = [status retain];
                [name release];
                dispatch_async(dispatch_get_main_queue(), ^{
                    if (ollamaStatusLabel_) [ollamaStatusLabel_ setStringValue:rs];
                    [rs release];
                    ollamaListModels();
                    this->release();
                });
            }
        });
    }

    void runOllamaGenerate(NSString *model, id keepAlive, NSString *success)
    {
        NSDictionary *body = @{
            @"model": model ?: @"",
            @"prompt": @"",
            @"stream": @NO,
            @"keep_alive": keepAlive ?: @"30m",
        };
        addRef();
        dispatch_async(dispatch_get_global_queue(QOS_CLASS_UTILITY, 0), ^{
            @autoreleasepool {
                NSString *error = nil;
                NSInteger code = 0;
                httpRequest(@"http://127.0.0.1:11434/api/generate", @"POST", body, nil, 120.0, &code, &error);
                BOOL ok = (code >= 200 && code < 300 && !error);
                NSString *status = ok ? success : [NSString stringWithFormat:@"%@ %@", success, error ?: @"Ollama did not respond."];
                __block NSString *rs = [status retain];
                dispatch_async(dispatch_get_main_queue(), ^{
                    if (ollamaStatusLabel_) [ollamaStatusLabel_ setStringValue:rs];
                    [rs release];
                    ollamaListModels();
                    this->release();
                });
            }
        });
    }

    NSString *toolCatalogPrompt()
    {
        return @"Available LLM-r tools:\n"
               "- create_midi_track {index?}; create_audio_track {index?}; set_tempo {bpm};\n"
               "- song_play {}; song_stop {}; song_continue {}; song_record {record}; song_metronome {enabled};\n"
               "- song_set_time_signature {numerator,denominator}; song_set_global_quantization {quantization}; song_set_count_in {count_in};\n"
               "- fire_clip {track_index,clip_index}; fire_scene {scene_index}; stop_all_clips {} destructive;\n"
               "- set_track_volume {track_index,volume 0..1}; set_track_mute {track_index,mute}; set_track_solo {track_index,solo}; arm_track {track_index,arm};\n"
               "- track_rename {track_index,name}; track_delete {track_index} destructive; track_duplicate {track_index}; track_set_pan {track_index,pan -1..1}; track_set_send {track_index,send_index,level 0..1};\n"
               "- scene_create {scene_index?}; scene_delete {scene_index} destructive; scene_rename {scene_index,name};\n"
               "- clip_create {track_index,clip_index,length_beats}; clip_delete {track_index,clip_index} destructive; clip_duplicate_loop {track_index,clip_index}; clip_duplicate_to {track_index,clip_index,target_track_index,target_clip_index}; clip_rename {track_index,clip_index,name};\n"
               "- clip_set_color {track_index,clip_index,color}; clip_set_color_index {track_index,clip_index,color_index}; clip_set_start_marker/end_marker/loop_start/loop_end/position {track_index,clip_index,value}; clip_set_looping {track_index,clip_index,looping};\n"
               "- clip_set_gain {track_index,clip_index,gain}; clip_set_pitch_coarse {track_index,clip_index,semitones}; clip_set_pitch_fine {track_index,clip_index,cents}; clip_set_warping {track_index,clip_index,warping}; clip_set_warp_mode {track_index,clip_index,warp_mode}; clip_set_ram_mode {track_index,clip_index,ram_mode};\n"
               "- midi_notes_get {track_index,clip_index,start_pitch?,pitch_span?,start_time?,time_span?}; midi_notes_add {track_index,clip_index,notes:[{pitch,start_time,duration,velocity,mute?}]}; midi_notes_remove {track_index,clip_index,...range?} destructive; midi_notes_clear {track_index,clip_index} destructive;\n"
               "- device_load {track_index,query,device_type? instrument|audio_effect|midi_effect|plugin|drum|all,preset_query?,browser_path?,allow_ambiguous?}; device_get_parameters/device_get_parameter/device_get_parameter_name/device_get_parameter_value_string/device_get_parameter_names/device_get_parameter_min_values/device_get_parameter_max_values {track_index,device_index,parameter_index?}; device_set_parameters {track_index,device_index,values 0..1}; device_set_parameter {track_index,device_index,parameter_index or device_name+parameter_name,value 0..1}; device_delete {track_index,device_index} destructive; utility_undo {}; utility_redo {}.\n";
    }

    NSString *systemPromptPresetKey()
    {
        return @"llmr.vst3.system_prompt_preset";
    }

    NSString *systemPromptCustomKey()
    {
        return @"llmr.vst3.system_prompt_custom";
    }

    NSString *defaultSystemPromptBase()
    {
        return @"You are the LLM-r planner running inside the LLM-r VST3 plug-in in Ableton Live. "
               "Return ONLY valid JSON matching this schema: "
               "{\"explanation\":\"short explanation\",\"confidence\":0.0,\"calls\":[{\"tool\":\"set_tempo\",\"args\":{\"bpm\":128}}]}. "
               "Do not include Markdown, prose, numbered lists, comments, or code fences outside the JSON object. "
               "The top-level JSON object must contain a calls array. Every call must contain tool and args. "
               "Plan only executable LLM-r tools. Do not claim to export/render, master, analyze loudness, or inspect unavailable Live state unless a listed tool supports it. "
               "Use device_load when the user asks to load an instrument, audio effect, MIDI effect, drum device, preset, or plug-in by name. "
               "Use preset_query for named presets and allow_ambiguous only when the user chose a specific ambiguous candidate. "
               "For composition requests, create tracks/clips and MIDI notes when enough musical detail is provided. "
               "For drum-loop requests, create a MIDI track, create a clip, add General MIDI drum notes with midi_notes_add, and fire the clip. "
               "Do not use unsupported tools such as set_track_quantization, clip_set_start_time, or clip_set_end_time. "
               "If arrangement insertion is unavailable, clearly state that a Session clip is created instead. "
               "For mixing requests, use exposed mixer/device parameter tools only.\n";
    }

    NSString *systemPromptStyleForPreset(NSString *preset)
    {
        NSString *name = [[preset ?: @"default" lowercaseString] stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
        if ([name isEqualToString:@"conservative editor"]) {
            return @"Style: prioritise safety, minimal edits, and explicit assumptions.\n";
        }
        if ([name isEqualToString:@"creative composer"]) {
            return @"Style: allow richer musical variation while staying executable.\n";
        }
        if ([name isEqualToString:@"arrangement assistant"]) {
            return @"Style: prefer arrangement-aware plans; if unsupported, explain Session fallback explicitly.\n";
        }
        return @"Style: default LLM-r planner behaviour.\n";
    }

    NSString *systemPromptBaseForPreset(NSString *preset)
    {
        NSUserDefaults *d = [NSUserDefaults standardUserDefaults];
        NSString *rawPreset = preset ?: @"Default LLM-r planner";
        NSString *name = [[rawPreset lowercaseString] stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
        NSString *custom = [d stringForKey:systemPromptCustomKey()] ?: @"";
        if ([name isEqualToString:@"custom"]) {
            return [custom length] > 0 ? custom : defaultSystemPromptBase();
        }
        return [defaultSystemPromptBase() stringByAppendingString:systemPromptStyleForPreset(rawPreset)];
    }

    NSString *selectedSystemPromptBase()
    {
        NSUserDefaults *d = [NSUserDefaults standardUserDefaults];
        NSString *preset = [d stringForKey:systemPromptPresetKey()] ?: @"Default LLM-r planner";
        return systemPromptBaseForPreset(preset);
    }

    NSString *systemPrompt()
    {
        NSMutableString *prompt = [NSMutableString stringWithString:selectedSystemPromptBase()];
        [prompt appendString:toolCatalogPrompt()];
        [prompt appendString:
            @"Example drum-loop response: {\"explanation\":\"Create a 2-bar MIDI jazz drum loop.\",\"confidence\":0.82,\"calls\":["
             "{\"tool\":\"set_tempo\",\"args\":{\"bpm\":92}},"
             "{\"tool\":\"create_midi_track\",\"args\":{\"index\":0}},"
             "{\"tool\":\"track_rename\",\"args\":{\"track_index\":0,\"name\":\"Jazzy Drum Loop\"}},"
             "{\"tool\":\"clip_create\",\"args\":{\"track_index\":0,\"clip_index\":0,\"length_beats\":8}},"
             "{\"tool\":\"midi_notes_add\",\"args\":{\"track_index\":0,\"clip_index\":0,\"notes\":[{\"pitch\":51,\"start_time\":0,\"duration\":0.16,\"velocity\":92,\"mute\":false}]}},"
             "{\"tool\":\"clip_set_looping\",\"args\":{\"track_index\":0,\"clip_index\":0,\"looping\":true}},"
             "{\"tool\":\"fire_clip\",\"args\":{\"track_index\":0,\"clip_index\":0}}"
             "]}.\n"];
        if (buttonOn(settingsExtraPromptButton_)) {
            [prompt appendString:@"Additional guidance: be explicit about limitations, keep plans conservative for destructive edits, and prefer preview review before live execution.\n"];
        }
        return prompt;
    }

    NSString *repairSystemPrompt()
    {
        return @"You convert non-compliant LLM-r planner output into executable LLM-r JSON. "
               "Return ONLY one valid JSON object with keys explanation, confidence, and calls. "
               "Use only tools from the provided catalog. Drop unsupported or impossible steps. "
               "For drum-loop requests, create a MIDI track, a clip, MIDI drum notes, loop it, and fire it.\n";
    }

    NSString *assistantFailureMessage(NSString *error, NSString *raw)
    {
        NSMutableString *out = [NSMutableString stringWithString:
            @"I could not turn that response into executable Ableton actions."];
        if ([error length] > 0) {
            if ([error hasPrefix:@"LLM HTTP "]) {
                NSRange colon = [error rangeOfString:@":"];
                NSString *head = colon.location == NSNotFound ? error : [error substringToIndex:colon.location];
                [out appendFormat:@"\n\n%@. Check the provider, model, endpoint, and API key in Settings.", head];
            } else {
                [out appendFormat:@"\n\n%@", error];
            }
        } else if ([raw length] > 0) {
            [out appendString:@"\n\nThe model replied, but the reply did not match the LLM-r action schema."];
        }
        [out appendString:@"\n\nOpen Details for the exact provider response."];
        return out;
    }

    double parseRequestedDurationBeats(NSString *prompt, double tempo)
    {
        NSString *lower = [prompt.lowercaseString stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
        if ([lower length] == 0) return 8.0;

        NSRegularExpression *minutesRe = [NSRegularExpression regularExpressionWithPattern:@"([0-9]+(?:\\.[0-9]+)?)\\s*minute" options:0 error:nil];
        NSTextCheckingResult *minutes = [minutesRe firstMatchInString:lower options:0 range:NSMakeRange(0, [lower length])];
        if (minutes && [minutes numberOfRanges] > 1) {
            double value = [[lower substringWithRange:[minutes rangeAtIndex:1]] doubleValue];
            return MAX(8.0, value * MAX(tempo, 60.0));
        }

        NSRegularExpression *secondsRe = [NSRegularExpression regularExpressionWithPattern:@"([0-9]+(?:\\.[0-9]+)?)\\s*second" options:0 error:nil];
        NSTextCheckingResult *seconds = [secondsRe firstMatchInString:lower options:0 range:NSMakeRange(0, [lower length])];
        if (seconds && [seconds numberOfRanges] > 1) {
            double value = [[lower substringWithRange:[seconds rangeAtIndex:1]] doubleValue];
            return MAX(8.0, value * MAX(tempo, 60.0) / 60.0);
        }

        NSRegularExpression *barsRe = [NSRegularExpression regularExpressionWithPattern:@"([0-9]+(?:\\.[0-9]+)?)\\s*bar" options:0 error:nil];
        NSTextCheckingResult *bars = [barsRe firstMatchInString:lower options:0 range:NSMakeRange(0, [lower length])];
        if (bars && [bars numberOfRanges] > 1) {
            double value = [[lower substringWithRange:[bars rangeAtIndex:1]] doubleValue];
            return MAX(8.0, value * 4.0);
        }

        return 8.0;
    }

    bool isDrumCompositionRequest(NSString *userPrompt)
    {
        NSString *lower = [userPrompt lowercaseString];
        return [lower containsString:@"drum"] || [lower containsString:@"beat"] || [lower containsString:@"groove"];
    }

    bool isPianoCompositionRequest(NSString *userPrompt)
    {
        NSString *lower = [userPrompt lowercaseString];
        return [lower containsString:@"piano"] || [lower containsString:@"ballad"];
    }

    NSDictionary *buildJazzDrumPlan(double durationBeats, double tempo, bool humanise, bool variation)
    {
        NSMutableArray *notes = [NSMutableArray array];
        const int totalBeats = (int)MAX(8.0, durationBeats);
        const int noteBudget = 640;
        for (int beat = 0; beat < totalBeats && (int)[notes count] < noteBudget; ++beat) {
            double t = (double)beat;
            int section = beat / 16;
            int rideVelocity = 84 + (section % 2 ? 6 : 0);
            [notes addObject:@{@"pitch": @51, @"start_time": @(t), @"duration": @0.2, @"velocity": @(rideVelocity), @"mute": @NO}];
            [notes addObject:@{@"pitch": @44, @"start_time": @(t + 0.5), @"duration": @0.1, @"velocity": @(humanise ? 62 + (beat % 5) : 68), @"mute": @NO}];
            if (beat % 4 == 0) {
                [notes addObject:@{@"pitch": @36, @"start_time": @(t), @"duration": @0.18, @"velocity": @(88 + (beat % 8 == 0 ? 6 : 0)), @"mute": @NO}];
            }
            if (beat % 4 == 2) {
                [notes addObject:@{@"pitch": @38, @"start_time": @(t), @"duration": @0.16, @"velocity": @(74 + (variation && beat % 16 == 14 ? 10 : 0)), @"mute": @NO}];
            }
            if (variation && beat % 16 == 15) {
                [notes addObject:@{@"pitch": @50, @"start_time": @(t + 0.5), @"duration": @0.12, @"velocity": @86, @"mute": @NO}];
            }
        }

        return @{
            @"explanation": [NSString stringWithFormat:@"Built-in fallback: create a jazz drum Session clip (%d beats). If Arrangement insertion is unavailable, Session fallback is used.", totalBeats],
            @"confidence": @0.74,
            @"calls": @[
                @{@"tool": @"set_tempo", @"args": @{@"bpm": @(tempo)}},
                @{@"tool": @"create_midi_track", @"args": @{@"index": @0}},
                @{@"tool": @"track_rename", @"args": @{@"track_index": @0, @"name": @"Jazz Drums"}},
                @{@"tool": @"clip_create", @"args": @{@"track_index": @0, @"clip_index": @0, @"length_beats": @(totalBeats)}},
                @{@"tool": @"midi_notes_add", @"args": @{@"track_index": @0, @"clip_index": @0, @"notes": notes}},
                @{@"tool": @"clip_set_looping", @"args": @{@"track_index": @0, @"clip_index": @0, @"looping": @YES}},
                @{@"tool": @"fire_clip", @"args": @{@"track_index": @0, @"clip_index": @0}},
            ],
        };
    }

    NSDictionary *buildPianoBalladPlan(double durationBeats, double tempo, NSString *key, NSString *style)
    {
        (void)key;
        (void)style;
        NSMutableArray *notes = [NSMutableArray array];
        const int totalBeats = (int)MAX(8.0, durationBeats);
        const int progression[4][3] = {{60,64,67},{57,60,64},{62,65,69},{55,59,62}};
        for (int beat = 0; beat < totalBeats; beat += 4) {
            int chord = (beat / 4) % 4;
            for (int i = 0; i < 3; ++i) {
                [notes addObject:@{@"pitch": @(progression[chord][i]), @"start_time": @(beat), @"duration": @3.6, @"velocity": @(68 + i * 6), @"mute": @NO}];
            }
            [notes addObject:@{@"pitch": @(progression[chord][1] + 12), @"start_time": @(beat + 2.0), @"duration": @1.6, @"velocity": @74, @"mute": @NO}];
        }

        return @{
            @"explanation": [NSString stringWithFormat:@"Built-in fallback: create a piano ballad Session clip (%d beats).", totalBeats],
            @"confidence": @0.7,
            @"calls": @[
                @{@"tool": @"set_tempo", @"args": @{@"bpm": @(tempo)}},
                @{@"tool": @"create_midi_track", @"args": @{@"index": @0}},
                @{@"tool": @"track_rename", @"args": @{@"track_index": @0, @"name": @"Piano Ballad"}},
                @{@"tool": @"clip_create", @"args": @{@"track_index": @0, @"clip_index": @0, @"length_beats": @(totalBeats)}},
                @{@"tool": @"midi_notes_add", @"args": @{@"track_index": @0, @"clip_index": @0, @"notes": notes}},
                @{@"tool": @"clip_set_looping", @"args": @{@"track_index": @0, @"clip_index": @0, @"looping": @YES}},
                @{@"tool": @"fire_clip", @"args": @{@"track_index": @0, @"clip_index": @0}},
            ],
        };
    }

    NSDictionary *localDrumLoopPlan(NSString *userPrompt)
    {
        if (!isDrumCompositionRequest(userPrompt)) {
            return nil;
        }
        double durationBeats = parseRequestedDurationBeats(userPrompt, 120.0);
        bool humanise = [[userPrompt lowercaseString] containsString:@"human"];
        return buildJazzDrumPlan(durationBeats, 120.0, humanise, true);
    }

    NSDictionary *localPianoPlan(NSString *userPrompt)
    {
        if (!isPianoCompositionRequest(userPrompt)) {
            return nil;
        }
        double durationBeats = parseRequestedDurationBeats(userPrompt, 80.0);
        return buildPianoBalladPlan(durationBeats, 80.0, @"C", @"ballad");
    }

    bool isDrumLoopRequest(NSString *userPrompt)
    {
        return isDrumCompositionRequest(userPrompt);
    }

    NSString *repairNonJsonPlan(NSString *provider, NSString *model, NSString *endpoint, NSString *apiKey,
                                NSString *userPrompt, NSString *badOutput, NSString **error)
    {
        NSMutableString *repairPrompt = [NSMutableString string];
        [repairPrompt appendString:toolCatalogPrompt()];
        [repairPrompt appendFormat:@"\nUser request:\n%@\n\nNon-compliant output:\n%@\n\nReturn only corrected JSON.",
            userPrompt ?: @"", badOutput ?: @""];
        NSString *system = [[repairSystemPrompt() stringByAppendingString:toolCatalogPrompt()] retain];
        NSString *fixed = callLLM(provider, model, endpoint, apiKey, system, repairPrompt, error);
        [system release];
        return fixed;
    }

    void planFromPrompt()
    {
        if (operationBusy_.load()) {
            setStatus(@"A process is already running.");
            return;
        }
        NSString *userPrompt = [[promptInputText() copy] retain];
        if ([userPrompt length] == 0) {
            setStatus(@"Enter a request first.");
            [userPrompt release];
            return;
        }
        NSString *providerValue = canonicalProvider(controlString(settingsProviderCombo_));
        NSString *modelValue = resolvedModelForSettings(providerValue, controlString(settingsModelField_));
        if ([modelValue length] == 0) {
            setStatus(@"Model missing - open Settings and choose a provider/model or enter Custom model.");
            [userPrompt release];
            refreshReadinessGuidance();
            return;
        }
        // Clear input field and add to chat history
        clearPromptInput();
        appendToChat(@"user", userPrompt);
        hasDryRunCurrentPlan_ = false;
        operationCancelRequested_.store(false);
        setBusy(true);
        NSTimeInterval planStartTime = [NSDate timeIntervalSinceReferenceDate];
        setStatus(@"Planning...");

        NSString *endpointValue = resolvedEndpointForSettings(providerValue, controlString(settingsEndpointField_));
        if (settingsProviderCombo_) selectComboValue(settingsProviderCombo_, providerValue);
        if (settingsModelField_ && comboContainsValue(settingsModelField_, modelValue)) {
            selectComboValue(settingsModelField_, modelValue);
        }
        if (settingsEndpointField_) [settingsEndpointField_ setStringValue:endpointValue ?: @""];
        NSString *provider = [providerValue copy];
        NSString *model = [modelValue copy];
        NSString *endpoint = [endpointValue copy];
        NSString *apiKey = [controlString(settingsApiKeyField_) copy];
        NSString *system = [systemPrompt() copy];

        addRef();
        dispatch_async(dispatch_get_global_queue(QOS_CLASS_USER_INITIATED, 0), ^{
            @autoreleasepool {
                NSString *error = nil;
                NSString *content = [callLLM(provider, model, endpoint, apiKey, system, userPrompt, &error) retain];
                BOOL cancelled = operationCancelRequested_.load();
                NSDictionary *plan = (!cancelled && content) ? parsePlan(content, &error) : nil;
                if (!plan && content) {
                    NSString *repairError = nil;
                    NSString *repaired = operationCancelRequested_.load()
                        ? nil
                        : repairNonJsonPlan(provider, model, endpoint, apiKey, userPrompt, content, &repairError);
                    NSDictionary *repairedPlan = repaired ? parsePlan(repaired, &repairError) : nil;
                    if (repairedPlan) {
                        NSString *original = [content retain];
                        [content release];
                        content = [[NSString stringWithFormat:
                            @"%@\n\n--- repaired JSON ---\n%@", original ?: @"", repaired ?: @""] retain];
                        [original release];
                        plan = repairedPlan;
                        error = nil;
                    } else if (repairError) {
                        error = repairError;
                    }
                }
                if (!plan && !operationCancelRequested_.load()) {
                    NSDictionary *fallback = localDrumLoopPlan(userPrompt);
                    if (!fallback) {
                        fallback = localPianoPlan(userPrompt);
                    }
                    if (fallback) {
                        plan = fallback;
                        NSString *original = [content retain];
                        [content release];
                        content = [[NSString stringWithFormat:
                            @"%@\n\n--- local fallback JSON ---\n%@",
                            original ?: @"",
                            renderRawPlan(fallback, @"Built-in fallback generated because the model did not return JSON.", @[])] retain];
                        [original release];
                        error = nil;
                    }
                }
                id calls = plan ? ([plan objectForKey:@"calls"] ?: [plan objectForKey:@"actions"] ?: [plan objectForKey:@"tool_calls"]) : nil;
                NSArray *actions = plan ? buildActions(calls, &error) : nil;
                if (plan && !operationCancelRequested_.load() && isDrumLoopRequest(userPrompt) && !planHasUsefulDrumLoop(calls)) {
                    NSDictionary *fallback = localDrumLoopPlan(userPrompt);
                    if (fallback) {
                        plan = fallback;
                        calls = [fallback objectForKey:@"calls"];
                        actions = buildActions(calls, &error);
                        NSString *original = [content retain];
                        [content release];
                        content = [[NSString stringWithFormat:
                            @"%@\n\n--- local fallback JSON ---\n%@",
                            original ?: @"",
                            renderRawPlan(fallback, @"Built-in fallback generated because the model returned an incomplete drum-loop plan.", actions ?: @[])] retain];
                        [original release];
                        error = nil;
                    }
                }
                if (!plan && !operationCancelRequested_.load() && isPianoCompositionRequest(userPrompt)) {
                    NSDictionary *fallback = localPianoPlan(userPrompt);
                    if (fallback) {
                        plan = fallback;
                        calls = [fallback objectForKey:@"calls"];
                        actions = buildActions(calls, &error);
                        error = nil;
                    }
                }
                NSTimeInterval elapsed = [NSDate timeIntervalSinceReferenceDate] - planStartTime;
                NSString *display = nil;
                NSString *rawDisplay = nil;
                NSString *status = nil;
                cancelled = operationCancelRequested_.load();
                if (cancelled) {
                    display = [@"Cancelled." retain];
                    rawDisplay = [(error ?: @"Request cancelled.") retain];
                    status = [@"Cancelled." retain];
                } else if (actions && [actions count] > 0) {
                    display = [renderPlan(plan, content, actions) retain];
                    rawDisplay = [renderRawPlan(plan, content, actions) retain];
                    status = [[NSString stringWithFormat:@"Plan ready - %lu step(s). (%.1fs)",
                               (unsigned long)[actions count], elapsed] retain];
                } else {
                    display = [assistantFailureMessage(error, content) retain];
                    rawDisplay = [(content ?: error ?: @"") retain];
                    if (error && [error length] > 0) {
                        status = [[NSString stringWithFormat:@"Planning failed: %@", error] retain];
                    } else if (content && [content length] > 0 && [content rangeOfString:@"no executable actions" options:NSCaseInsensitiveSearch].location != NSNotFound) {
                        status = [@"Plan has no executable actions. Model may need clarification." retain];
                    } else {
                        status = [@"No executable actions." retain];
                    }
                }
                __block NSArray *retainedActions = [actions retain];
                [content release];
                [provider release];
                [model release];
                [endpoint release];
                [apiKey release];
                [system release];
                [userPrompt release];
                dispatch_async(dispatch_get_main_queue(), ^{
                    if (view_) {
                        [lastActions_ release];
                        lastActions_ = retainedActions;
                        retainedActions = nil;
                        appendToChat(@"assistant", display ?: @"");
                        updateRawResponse(rawDisplay ?: @"");
                        showResponseTab(false);
                        setStatus(status);
                        if (!operationCancelRequested_.load() && lastActions_ && [lastActions_ count] > 0) {
                            bool previewOnly = requireDryRunBeforeExecuteSetting();
                            setStatus(previewOnly ? @"Executing preview..." : @"Executing...");
                            executeLastPlan(previewOnly);
                        } else {
                            setBusy(false);
                        }
                    }
                    [retainedActions release];
                    [display release];
                    [rawDisplay release];
                    [status release];
                    this->release();
                });
            }
        });
    }

    NSString *deviceBridgeURL(NSString *path)
    {
        NSString *cleanPath = path ?: @"";
        if (![cleanPath hasPrefix:@"/"]) {
            cleanPath = [@"/" stringByAppendingString:cleanPath];
        }
        return [NSString stringWithFormat:@"http://%@:%d%@", deviceBridgeHost(), deviceBridgePort(), cleanPath];
    }

    void checkDeviceBridgeStatus()
    {
        if (deviceBridgeCheckInFlight_) {
            if (deviceBridgeStatusLabel_) {
                [deviceBridgeStatusLabel_ setStringValue:@"Device Bridge: already checking..."];
            }
            setStatus(@"Already checking Device Bridge...");
            return;
        }
        deviceBridgeCheckInFlight_ = true;
        if (deviceBridgeStatusLabel_) {
            [deviceBridgeStatusLabel_ setStringValue:@"Device Bridge: checking local Remote Script..."];
        }
        addRef();
        dispatch_async(dispatch_get_global_queue(QOS_CLASS_UTILITY, 0), ^{
            @autoreleasepool {
                NSString *error = nil;
                NSInteger code = 0;
                NSString *out = httpRequest(deviceBridgeURL(@"/health"), @"GET", nil, nil, 2.0, &code, &error);
                NSData *data = [out dataUsingEncoding:NSUTF8StringEncoding];
                NSDictionary *json = data ? [NSJSONSerialization JSONObjectWithData:data options:0 error:nil] : nil;
                NSString *bridge = [json isKindOfClass:[NSDictionary class]] ? [json objectForKey:@"bridge"] : nil;
                BOOL ok = (code >= 200 && code < 300 && !error);
                NSString *host = deviceBridgeHost();
                int port = deviceBridgePort();
                NSString *library = bridgeUserLibraryPath_ ? bridgeUserLibraryPath_ : @"";
                NSString *target = bridgeInstallTargetForUserLibrary(library);
                NSString *diskState = bridgeInstallStatusForUserLibrary(library);
                NSString *status = ok
                    ? [NSString stringWithFormat:@"Device Bridge reachable on %@:%d%@%@.",
                       host, port, [bridge length] ? @" - " : @"", bridge ?: @""]
                    : [NSString stringWithFormat:
                       @"Device Bridge not reachable\n"
                       @"Likely causes:\n"
                       @"- The LLM-r Remote Script is not installed in Ableton's active User Library.\n"
                       @"- Live has not been restarted after installation.\n"
                       @"- The Remote Script has not been selected in Live Settings -> Link, Tempo & MIDI.\n"
                       @"- Ableton blocked the script because of an import/runtime error.\n"
                       @"Selected User Library: %@\n"
                       @"Install target: %@\n"
                       @"%@\n"
                       @"Next actions:\n"
                       @"1. Reveal Installed Bridge\n"
                       @"2. Copy Install Path\n"
                       @"3. Reinstall Bridge\n"
                       @"4. Open Bridge Setup Help\n"
                       @"5. Recheck Bridge\n"
                       @"Bridge files are installed only on disk; Live selection is a separate step. %@",
                       [library length] > 0 ? library : @"Not selected",
                       [target length] > 0 ? target : @"Not selected",
                       diskState,
                       error ?: @""];
                __block NSString *rs = [status retain];
                __block BOOL rok = ok;
                dispatch_async(dispatch_get_main_queue(), ^{
                    deviceBridgeCheckInFlight_ = false;
                    deviceBridgeChecked_ = true;
                    deviceBridgeReachable_ = rok;
                    if (deviceBridgeStatusLabel_) [deviceBridgeStatusLabel_ setStringValue:rs];
                    refreshBridgePathUI();
                    refreshReadinessGuidance();
                    if ([library length] == 0) {
                        setStatus(@"Choose Ableton User Library before installing the bridge.");
                    } else if (rok) {
                        setStatus(@"Device Bridge reachable.");
                    } else {
                        setStatus(@"Device Bridge not reachable. Open Settings and recheck Bridge.");
                    }
                    [rs release];
                    this->release();
                });
            }
        });
    }

    NSDictionary *deviceBridgeBodyForAction(NSDictionary *act, NSString **error)
    {
        NSDictionary *body = [act objectForKey:@"body"];
        if ([body isKindOfClass:[NSDictionary class]]) {
            return body;
        }
        NSArray *args = [act objectForKey:@"args"];
        if (![args isKindOfClass:[NSArray class]] || [args count] < 3) {
            if (error) *error = @"Device Bridge action is missing arguments.";
            return nil;
        }
        NSMutableDictionary *payload = [NSMutableDictionary dictionaryWithDictionary:@{
            @"track_index": [args objectAtIndex:0],
            @"query": [args objectAtIndex:1],
            @"device_type": [args objectAtIndex:2],
        }];
        if ([args count] > 3 && [[args objectAtIndex:3] isKindOfClass:[NSDictionary class]]) {
            NSDictionary *options = [args objectAtIndex:3];
            for (NSString *key in @[@"preset_query", @"browser_path", @"allow_ambiguous"]) {
                id value = [options objectForKey:key];
                if (value) {
                    [payload setObject:value forKey:key];
                }
            }
        }
        return payload;
    }

    NSArray *deviceBridgeCandidatesFromResponse(NSString *response)
    {
        if ([response length] == 0) return @[];
        NSData *data = [response dataUsingEncoding:NSUTF8StringEncoding];
        id json = data ? [NSJSONSerialization JSONObjectWithData:data options:0 error:nil] : nil;
        NSArray *items = [json isKindOfClass:[NSDictionary class]] ? [json objectForKey:@"candidates"] : nil;
        if (![items isKindOfClass:[NSArray class]]) return @[];
        NSMutableArray *out = [NSMutableArray array];
        for (id item in items) {
            if ([item isKindOfClass:[NSDictionary class]]) {
                [out addObject:item];
            }
        }
        return out;
    }

    NSString *deviceBridgeCandidateLabel(NSDictionary *candidate)
    {
        NSString *name = [candidate objectForKey:@"name"] ?: @"(unnamed)";
        NSArray *path = [candidate objectForKey:@"path"];
        NSString *pathText = @"";
        if ([path isKindOfClass:[NSArray class]] && [path count] > 0) {
            pathText = [path componentsJoinedByString:@" > "];
        }
        NSNumber *score = [candidate objectForKey:@"score"];
        if ([pathText length] > 0 && score) {
            return [NSString stringWithFormat:@"%@ — %@ (score %@)", name, pathText, score];
        }
        if ([pathText length] > 0) {
            return [NSString stringWithFormat:@"%@ — %@", name, pathText];
        }
        return name;
    }

    NSDictionary *deviceBridgeActionWithBrowserPath(NSDictionary *act, NSArray *browserPath)
    {
        if (![browserPath isKindOfClass:[NSArray class]] || [browserPath count] == 0) return nil;

        NSDictionary *body = [act objectForKey:@"body"];
        if ([body isKindOfClass:[NSDictionary class]]) {
            NSMutableDictionary *updatedBody = [NSMutableDictionary dictionaryWithDictionary:body];
            [updatedBody setObject:browserPath forKey:@"browser_path"];
            [updatedBody removeObjectForKey:@"allow_ambiguous"];
            NSMutableDictionary *updatedAction = [NSMutableDictionary dictionaryWithDictionary:act];
            [updatedAction setObject:updatedBody forKey:@"body"];
            return updatedAction;
        }

        NSArray *args = [act objectForKey:@"args"];
        if (![args isKindOfClass:[NSArray class]] || [args count] < 3) return nil;
        NSMutableArray *updatedArgs = [NSMutableArray arrayWithArray:args];
        NSMutableDictionary *options = [NSMutableDictionary dictionary];
        if ([updatedArgs count] > 3 && [[updatedArgs objectAtIndex:3] isKindOfClass:[NSDictionary class]]) {
            [options addEntriesFromDictionary:[updatedArgs objectAtIndex:3]];
        }
        [options setObject:browserPath forKey:@"browser_path"];
        [options removeObjectForKey:@"allow_ambiguous"];
        if ([updatedArgs count] > 3) {
            [updatedArgs replaceObjectAtIndex:3 withObject:options];
        } else {
            [updatedArgs addObject:options];
        }
        NSMutableDictionary *updatedAction = [NSMutableDictionary dictionaryWithDictionary:act];
        [updatedAction setObject:updatedArgs forKey:@"args"];
        return updatedAction;
    }

    NSDictionary *chooseDeviceBridgeCandidateForAction(NSDictionary *act,
                                                       NSString *resolveResponse,
                                                       NSString **error)
    {
        NSArray *candidates = deviceBridgeCandidatesFromResponse(resolveResponse);
        if ([candidates count] == 0) {
            if (error) *error = @"Ambiguous Device Bridge match returned no selectable candidates.";
            return nil;
        }

        __block NSInteger selectedIndex = -1;
        dispatch_sync(dispatch_get_main_queue(), ^{
            NSAlert *alert = [[NSAlert alloc] init];
            [alert setMessageText:@"Choose Device Candidate"];
            NSString *tool = [act objectForKey:@"tool"] ?: @"device_load";
            [alert setInformativeText:[NSString stringWithFormat:
                @"The Device Bridge found multiple matches for %@. Choose the exact browser path to continue.",
                tool]];
            [alert addButtonWithTitle:@"Use Selected Candidate"];
            [alert addButtonWithTitle:@"Cancel Execution"];

            NSPopUpButton *picker = [[[NSPopUpButton alloc] initWithFrame:NSMakeRect(0, 0, 560, 30)] autorelease];
            for (NSDictionary *candidate in candidates) {
                [picker addItemWithTitle:deviceBridgeCandidateLabel(candidate)];
            }
            [picker selectItemAtIndex:0];
            [alert setAccessoryView:picker];

            NSInteger response = [alert runModal];
            if (response == NSAlertFirstButtonReturn) {
                selectedIndex = [picker indexOfSelectedItem];
            }
            [alert release];
        });

        if (selectedIndex < 0 || selectedIndex >= (NSInteger)[candidates count]) {
            if (error) *error = @"Device Bridge candidate selection was cancelled.";
            return nil;
        }

        NSDictionary *candidate = [candidates objectAtIndex:(NSUInteger)selectedIndex];
        NSArray *path = [candidate objectForKey:@"path"];
        NSDictionary *updatedAction = deviceBridgeActionWithBrowserPath(act, path);
        if (!updatedAction) {
            if (error) *error = @"Selected candidate did not provide a valid browser path.";
            return nil;
        }
        return updatedAction;
    }

    bool sendDeviceBridgeAction(NSDictionary *act, NSString **error)
    {
        NSDictionary *body = deviceBridgeBodyForAction(act, error);
        if (!body) return false;
        NSInteger code = 0;
        NSString *path = [act objectForKey:@"address"] ?: @"/api/devices/load";
        NSString *response = httpRequest(deviceBridgeURL(path), @"POST", body, nil, 20.0, &code, error);
        (void)response;
        return code >= 200 && code < 300 && (!error || !*error);
    }

    void executeFromMainButton()
    {
        if (!lastActions_ || [lastActions_ count] == 0) {
            setStatus(@"Create a plan first.");
            return;
        }
        if (!requireDryRunBeforeExecuteSetting() || hasDryRunCurrentPlan_) {
            executeLastPlan(false);
            return;
        }

        NSAlert *alert = [[NSAlert alloc] init];
        [alert setMessageText:@"Run Preview first"];
        [alert setInformativeText:@"This plan has not been previewed since it was generated."];
        [alert addButtonWithTitle:@"Run Preview"];
        [alert addButtonWithTitle:@"Execute Anyway"];
        [alert addButtonWithTitle:@"Cancel"];
        NSModalResponse response = [alert runModal];
        [alert release];

        if (response == NSAlertFirstButtonReturn) {
            executeLastPlan(true);
        } else if (response == NSAlertSecondButtonReturn) {
            executeLastPlan(false);
        } else {
            setStatus(@"Execution cancelled.");
        }
    }

    void executeLastPlan(bool dryRun)
    {
        if (!lastActions_ || [lastActions_ count] == 0) {
            setStatus(@"Create a plan first.");
            return;
        }
        if (!operationBusy_.load()) {
            operationCancelRequested_.store(false);
        }
        bool allowDestructive = buttonOn(settingsDestructiveButton_);
        NSString *host = [controlString(settingsOscHostField_) copy];
        int port = static_cast<int>([controlString(settingsOscPortField_) integerValue]);
        NSArray *actions = [lastActions_ retain];
        NSMutableArray *runtimeActions = [actions mutableCopy];
        setBusy(true);
        setStatus(dryRun ? @"Executing preview..." : @"Executing...");

        addRef();
        dispatch_async(dispatch_get_global_queue(QOS_CLASS_USER_INITIATED, 0), ^{
            @autoreleasepool {
                NSMutableString *report = [NSMutableString string];
                bool blocked = false;
                bool cancelled = operationCancelRequested_.load();
                if (!dryRun && !cancelled) {
                    bool needsDeviceBridge = false;
                    for (NSDictionary *act in actions) {
                        if (operationCancelRequested_.load()) {
                            cancelled = true;
                            break;
                        }
                        NSString *transport = [act objectForKey:@"transport"] ?: @"osc";
                        if ([transport isEqualToString:@"device_bridge"]) {
                            needsDeviceBridge = true;
                            break;
                        }
                    }
                    if (needsDeviceBridge && !cancelled) {
                        NSString *err = nil;
                        NSInteger code = 0;
                        httpRequest(deviceBridgeURL(@"/health"), @"GET", nil, nil, 2.0, &code, &err);
                        cancelled = operationCancelRequested_.load();
                        if (code < 200 || code >= 300 || err) {
                            blocked = true;
                            [report appendFormat:@"BLOCKED Device Bridge preflight failed on %@:%d. %@\n",
                                deviceBridgeHost(), deviceBridgePort(), err ?: @"Enable LLMR_Bridge in Ableton Live."];
                        }
                        if (!blocked && !cancelled) {
                            for (NSUInteger actionIndex = 0; actionIndex < [runtimeActions count]; ++actionIndex) {
                                if (operationCancelRequested_.load()) {
                                    cancelled = true;
                                    break;
                                }
                                NSDictionary *act = [runtimeActions objectAtIndex:actionIndex];
                                NSString *transport = [act objectForKey:@"transport"] ?: @"osc";
                                if (![transport isEqualToString:@"device_bridge"]) continue;
                                NSString *resolveError = nil;
                                NSDictionary *body = deviceBridgeBodyForAction(act, &resolveError);
                                if (!body) {
                                    blocked = true;
                                    [report appendFormat:@"BLOCKED Device Bridge preflight failed: %@\n",
                                        resolveError ?: @"invalid device_load action"];
                                    break;
                                }
                                NSInteger resolveCode = 0;
                                NSString *resolveResponse = httpRequest(deviceBridgeURL(@"/api/devices/resolve"), @"POST", body, nil, 10.0, &resolveCode, &resolveError);
                                if (operationCancelRequested_.load()) {
                                    cancelled = true;
                                    break;
                                }
                                if (resolveCode == 409) {
                                    NSString *pickerError = nil;
                                    NSDictionary *updatedAction = chooseDeviceBridgeCandidateForAction(act, resolveResponse, &pickerError);
                                    if (!updatedAction) {
                                        blocked = true;
                                        [report appendFormat:@"BLOCKED Device Bridge resolve failed for %@. %@\n",
                                            [act objectForKey:@"tool"] ?: @"device_load",
                                            pickerError ?: @"Choose a specific candidate path."];
                                        break;
                                    }
                                    [runtimeActions replaceObjectAtIndex:actionIndex withObject:updatedAction];
                                    act = updatedAction;
                                    resolveError = nil;
                                    body = deviceBridgeBodyForAction(act, &resolveError);
                                    resolveCode = 0;
                                    resolveResponse = httpRequest(deviceBridgeURL(@"/api/devices/resolve"), @"POST", body, nil, 10.0, &resolveCode, &resolveError);
                                    if (operationCancelRequested_.load()) {
                                        cancelled = true;
                                        break;
                                    }
                                }
                                if (resolveCode < 200 || resolveCode >= 300 || resolveError) {
                                    blocked = true;
                                    [report appendFormat:@"BLOCKED Device Bridge resolve failed for %@. %@\n",
                                        [act objectForKey:@"tool"] ?: @"device_load",
                                        resolveError ?: @"Choose a specific candidate path or confirm allow_ambiguous."];
                                    break;
                                }
                            }
                        }
                    }
                }
                if (!blocked && !cancelled) {
                    for (NSDictionary *act in runtimeActions) {
                        if (operationCancelRequested_.load()) {
                            cancelled = true;
                            break;
                        }
                        bool destructive = [[act objectForKey:@"destructive"] boolValue];
                        if (destructive && !dryRun && !allowDestructive) {
                            [report appendFormat:@"Skipped destructive: %@\n", [act objectForKey:@"tool"]];
                            continue;
                        }
                        if (dryRun) {
                            [report appendFormat:@"PREVIEW %@ %@\n",
                                [act objectForKey:@"address"], [[act objectForKey:@"args"] description]];
                            continue;
                        }
                        NSString *err = nil;
                        NSString *transport = [act objectForKey:@"transport"] ?: @"osc";
                        bool ok = false;
                        if ([transport isEqualToString:@"device_bridge"]) {
                            ok = sendDeviceBridgeAction(act, &err);
                        } else {
                            ok = sendOsc(host, port, [act objectForKey:@"address"],
                                         [act objectForKey:@"args"], &err);
                        }
                        if (operationCancelRequested_.load()) {
                            cancelled = true;
                            break;
                        }
                        [report appendFormat:@"%@ %@ %@\n", ok ? @"SENT" : @"ERROR",
                            [act objectForKey:@"address"],
                            ok ? [[act objectForKey:@"args"] description] : err];
                    }
                }
                NSString *statusMsg = cancelled ? @"Cancelled." : (dryRun ? @"Preview complete." : (blocked ? @"BLOCKED execution." : @"Execution complete."));
                NSString *message = [[NSString stringWithFormat:@"%@\n%@", statusMsg, report] retain];
                NSString *status = [statusMsg retain];
                dispatch_async(dispatch_get_main_queue(), ^{
                    appendToChat(@"assistant", message);
                    setStatus(status);
                    if (dryRun && !blocked && !cancelled) {
                        hasDryRunCurrentPlan_ = true;
                    }
                    setBusy(false);
                    [message release];
                    [status release];
                    [actions release];
                    [runtimeActions release];
                    [host release];
                    this->release();
                });
            }
        });
    }

    NSInteger continueWaitingDecisionForLLM(NSString *provider, NSString *model, NSTimeInterval elapsed)
    {
        __block NSInteger decision = 0; // 0 wait again, 1 wait without timeout, 2 cancel
        void (^showAlert)(void) = ^{
            if (!view_) return;
            NSInteger seconds = (NSInteger)elapsed;
            NSString *runtime = [NSString stringWithFormat:@"%@ / %@",
                provider ?: @"provider", [model length] > 0 ? model : @"model"];
            NSAlert *alert = [[NSAlert alloc] init];
            [alert setMessageText:@"LLM request is still running"];
            [alert setInformativeText:[NSString stringWithFormat:
                @"%@ has been waiting for %ld seconds. Continue waiting?",
                runtime, (long)seconds]];
            [alert addButtonWithTitle:@"Wait 5 More Minutes"];
            [alert addButtonWithTitle:@"Wait Without Timeout"];
            [alert addButtonWithTitle:@"Cancel Request"];
            NSModalResponse response = [alert runModal];
            [alert release];
            if (response == NSAlertSecondButtonReturn) {
                decision = 1;
            } else if (response == NSAlertThirdButtonReturn) {
                decision = 2;
            }
        };
        if ([NSThread isMainThread]) {
            showAlert();
        } else {
            dispatch_sync(dispatch_get_main_queue(), showAlert);
        }
        return decision;
    }

    NSString *callLLM(NSString *provider, NSString *model, NSString *endpoint, NSString *apiKey,
                      NSString *system, NSString *userPrompt, NSString **error)
    {
        NSString *p = canonicalProvider(provider);
        NSString *urlString = resolvedEndpointForSettings(p, endpoint);
        if ([urlString length] == 0) {
            if (error) {
                *error = [NSString stringWithFormat:@"%@ provider requires an endpoint.", p];
            }
            return nil;
        }
        NSString *rawModel = model ? model : @"";
        NSString *llmModel = [[rawModel stringByTrimmingCharactersInSet:
                               [NSCharacterSet whitespaceAndNewlineCharacterSet]] retain];
        if ([p isEqualToString:@"ollama"] && [llmModel length] == 0) {
            NSString *tagsError = nil;
            NSInteger tagsCode = 0;
            NSString *tags = httpRequest(@"http://127.0.0.1:11434/api/tags",
                                         @"GET", nil, nil, 8.0, &tagsCode, &tagsError);
            NSArray *localModels = (tagsCode >= 200 && tagsCode < 300 && !tagsError)
                ? modelNamesFromOllamaJSON(tags)
                : @[];
            if ([localModels count] > 0) {
                [llmModel release];
                llmModel = [[localModels objectAtIndex:0] retain];
            }
        }
        if ([p isEqualToString:@"google"]) {
            if ([apiKey length] == 0 && ![urlString containsString:@"key="]) {
                if (error) *error = @"Google provider requires an API key.";
                [llmModel release];
                return nil;
            }
            NSString *googleModel = [llmModel length] ? llmModel : @"gemini-2.5-flash";
            NSString *encodedModel = [googleModel stringByAddingPercentEncodingWithAllowedCharacters:
                [NSCharacterSet URLPathAllowedCharacterSet]];
            NSString *encodedKey = [apiKey stringByAddingPercentEncodingWithAllowedCharacters:
                [NSCharacterSet URLQueryAllowedCharacterSet]];
            if ([urlString containsString:@":generateContent"]) {
                if (![urlString containsString:@"key="] && [encodedKey length] > 0) {
                    NSString *sep = [urlString containsString:@"?"] ? @"&" : @"?";
                    urlString = [urlString stringByAppendingFormat:@"%@key=%@", sep, encodedKey];
                }
            } else {
                while ([urlString hasSuffix:@"/"]) {
                    urlString = [urlString substringToIndex:[urlString length] - 1];
                }
                urlString = [NSString stringWithFormat:@"%@/models/%@:generateContent?key=%@",
                             urlString, encodedModel, encodedKey ?: @""];
            }
        }
        NSURL *url = [NSURL URLWithString:urlString];
        if (!url) {
            if (error) {
                *error = @"Invalid LLM endpoint URL.";
            }
            [llmModel release];
            return nil;
        }

        NSMutableURLRequest *request = [NSMutableURLRequest requestWithURL:url];
        [request setHTTPMethod:@"POST"];
        [request setTimeoutInterval:24.0 * 60.0 * 60.0];
        [request setValue:@"application/json" forHTTPHeaderField:@"Content-Type"];

        NSDictionary *body = nil;
        if ([p isEqualToString:@"ollama"]) {
            body = @{
                @"model": [llmModel length] ? llmModel : @"llama3",
                @"stream": @NO,
                @"format": @"json",
                @"options": @{@"temperature": @0.1},
                @"messages": @[
                    @{@"role": @"system", @"content": system},
                    @{@"role": @"user", @"content": userPrompt},
                ],
            };
        } else if ([p isEqualToString:@"anthropic"]) {
            [request setValue:apiKey forHTTPHeaderField:@"x-api-key"];
            [request setValue:@"2023-06-01" forHTTPHeaderField:@"anthropic-version"];
            body = @{
                @"model": [llmModel length] ? llmModel : @"claude-3-5-sonnet-latest",
                @"max_tokens": @4096,
                @"system": system,
                @"messages": @[@{@"role": @"user", @"content": userPrompt}],
            };
        } else if ([p isEqualToString:@"google"]) {
            body = @{
                @"systemInstruction": @{@"parts": @[@{@"text": system}]},
                @"contents": @[
                    @{@"role": @"user", @"parts": @[@{@"text": userPrompt}]},
                ],
                @"generationConfig": @{@"temperature": @0.2, @"responseMimeType": @"application/json"},
            };
        } else {
            if ([apiKey length] > 0) {
                [request setValue:[NSString stringWithFormat:@"Bearer %@", apiKey] forHTTPHeaderField:@"Authorization"];
            }
            NSMutableDictionary *openAiBody = [@{
                @"model": [llmModel length] ? llmModel : @"gpt-4.1-mini",
                @"temperature": @0.2,
                @"messages": @[
                    @{@"role": @"system", @"content": system},
                    @{@"role": @"user", @"content": userPrompt},
                ],
            } mutableCopy];
            if ([p isEqualToString:@"openai"]) {
                [openAiBody setObject:@{@"type": @"json_object"} forKey:@"response_format"];
            }
            body = [openAiBody autorelease];
        }

        NSData *bodyData = [NSJSONSerialization dataWithJSONObject:body options:0 error:nil];
        [request setHTTPBody:bodyData];

        __block NSData *responseData = nil;
        __block NSError *requestError = nil;
        __block NSHTTPURLResponse *httpResponse = nil;
        dispatch_semaphore_t semaphore = dispatch_semaphore_create(0);
        NSURLSessionDataTask *task = [[NSURLSession sharedSession]
            dataTaskWithRequest:request
              completionHandler:^(NSData *data, NSURLResponse *response, NSError *err) {
                  responseData = [data retain];
                  requestError = [err retain];
                  httpResponse = [(NSHTTPURLResponse *)response retain];
                  dispatch_semaphore_signal(semaphore);
              }];
        [task resume];
        NSTimeInterval requestStart = [NSDate timeIntervalSinceReferenceDate];
        NSTimeInterval nextPromptAt = requestStart + 300.0;
        BOOL waitWithoutTimeout = NO;
        while (true) {
            if (operationCancelRequested_.load()) {
                [task cancel];
                if (error) {
                    *error = @"Request cancelled.";
                }
                [llmModel release];
                return nil;
            }
            long waitResult = dispatch_semaphore_wait(
                semaphore,
                dispatch_time(DISPATCH_TIME_NOW, (int64_t)(0.25 * NSEC_PER_SEC)));
            if (waitResult == 0) {
                break;
            }
            NSTimeInterval now = [NSDate timeIntervalSinceReferenceDate];
            if (!waitWithoutTimeout && now >= nextPromptAt) {
                NSInteger decision = continueWaitingDecisionForLLM(p, llmModel, now - requestStart);
                if (decision == 2) {
                    operationCancelRequested_.store(true);
                    [task cancel];
                    if (error) {
                        *error = @"Request cancelled.";
                    }
                    [llmModel release];
                    return nil;
                }
                if (decision == 1) {
                    waitWithoutTimeout = YES;
                } else {
                    nextPromptAt = now + 300.0;
                }
            }
        }

        NSString *result = nil;
        if (requestError) {
            if (error) {
                *error = [requestError localizedDescription];
            }
        } else if ([httpResponse statusCode] < 200 || [httpResponse statusCode] >= 300) {
            NSString *bodyText = [[[NSString alloc] initWithData:responseData encoding:NSUTF8StringEncoding] autorelease];
            if (error) {
                *error = [NSString stringWithFormat:@"LLM HTTP %ld: %@", static_cast<long>([httpResponse statusCode]), bodyText ?: @""];
            }
        } else {
            id json = [NSJSONSerialization JSONObjectWithData:responseData options:0 error:nil];
            if ([p isEqualToString:@"ollama"]) {
                result = [[json valueForKeyPath:@"message.content"] retain];
            } else if ([p isEqualToString:@"anthropic"]) {
                NSArray *content = [json objectForKey:@"content"];
                if ([content count] > 0) {
                    result = [[[content objectAtIndex:0] objectForKey:@"text"] retain];
                }
            } else if ([p isEqualToString:@"google"]) {
                NSArray *candidates = [json objectForKey:@"candidates"];
                if ([candidates count] > 0) {
                    NSDictionary *content = [[candidates objectAtIndex:0] objectForKey:@"content"];
                    NSArray *parts = [content objectForKey:@"parts"];
                    if ([parts count] > 0) {
                        result = [[[parts objectAtIndex:0] objectForKey:@"text"] retain];
                    }
                }
            } else {
                NSArray *choices = [json objectForKey:@"choices"];
                if ([choices count] > 0) {
                    result = [[[[choices objectAtIndex:0] objectForKey:@"message"] objectForKey:@"content"] retain];
                }
            }
            if (!result && error) {
                *error = @"LLM response did not contain text content.";
            }
        }
        [responseData release];
        [requestError release];
        [httpResponse release];
        [llmModel release];
        return [result autorelease];
    }

    NSDictionary *parsePlan(NSString *text, NSString **error)
    {
        NSRange start = [text rangeOfString:@"{"];
        NSRange end = [text rangeOfString:@"}" options:NSBackwardsSearch];
        if (start.location == NSNotFound || end.location == NSNotFound || end.location <= start.location) {
            if (error) {
                *error = @"LLM output did not contain a JSON plan.";
            }
            return nil;
        }
        NSRange jsonRange = NSMakeRange(start.location, end.location - start.location + 1);
        NSString *candidate = [text substringWithRange:jsonRange];
        NSData *data = [candidate dataUsingEncoding:NSUTF8StringEncoding];
        id json = [NSJSONSerialization JSONObjectWithData:data options:0 error:nil];
        if (![json isKindOfClass:[NSDictionary class]]) {
            if (error) {
                *error = @"LLM output JSON was not an object.";
            }
            return nil;
        }
        return json;
    }

    NSString *humanValue(id value)
    {
        if ([value isKindOfClass:[NSString class]]) return value;
        if ([value isKindOfClass:[NSNumber class]]) return [value stringValue];
        if ([value isKindOfClass:[NSArray class]]) {
            NSMutableArray *parts = [NSMutableArray array];
            for (id item in (NSArray *)value) {
                [parts addObject:humanValue(item)];
            }
            return [parts componentsJoinedByString:@", "];
        }
        return [NSString stringWithFormat:@"%@", value ?: @""];
    }

    NSString *humanArgs(NSArray *args)
    {
        if (![args isKindOfClass:[NSArray class]] || [args count] == 0) return @"No parameters.";
        NSMutableArray *parts = [NSMutableArray array];
        for (id value in args) {
            NSString *text = humanValue(value);
            if ([text length] > 0) [parts addObject:text];
        }
        return [NSString stringWithFormat:@"Parameters: %@", [parts componentsJoinedByString:@", "]];
    }

    NSString *renderPlan(NSDictionary *plan, NSString *raw, NSArray *actions)
    {
        (void)raw;
        NSMutableString *out = [NSMutableString string];
        NSString *explanation = [plan objectForKey:@"explanation"] ?: @"No explanation provided.";
        double confidence = [[plan objectForKey:@"confidence"] doubleValue];
        if (confidence <= 1.0) confidence *= 100.0;
        [out appendFormat:@"PLAN BOARD — %lu action%@ ready\n\n",
            (unsigned long)[actions count], [actions count] == 1 ? @"" : @"s"];
        [out appendFormat:@"%@\n\n", explanation];
        [out appendFormat:@"Confidence: %.0f%%\n\n", confidence];
        [out appendString:@"Actions:\n"];
        NSUInteger index = 1;
        for (NSDictionary *action in actions) {
            BOOL destructive = [[action objectForKey:@"destructive"] boolValue];
            NSString *safety = destructive ? @"DESTRUCTIVE - requires permission" : @"SAFE";
            NSString *transport = [[action objectForKey:@"transport"] isKindOfClass:[NSString class]]
                ? [action objectForKey:@"transport"] : @"osc";
            NSString *description = [action objectForKey:@"description"] ?: [action objectForKey:@"tool"] ?: @"Action";
            [out appendFormat:@"[%lu] %@\n", (unsigned long)index, description];
            [out appendFormat:@"    Tool: %@    Safety: %@    Transport: %@\n",
                [action objectForKey:@"tool"] ?: @"unknown", safety, transport];
            [out appendFormat:@"    %@\n", humanArgs([action objectForKey:@"args"])];
            index++;
        }
        [out appendString:@"\nExecution details, provider output, and OSC addresses are available in Details."];
        return out;
    }

    NSString *renderRawPlan(NSDictionary *plan, NSString *raw, NSArray *actions)
    {
        NSMutableDictionary *payload = [NSMutableDictionary dictionary];
        [payload setObject:[plan objectForKey:@"explanation"] ?: @"" forKey:@"explanation"];
        [payload setObject:[plan objectForKey:@"confidence"] ?: @0 forKey:@"confidence"];
        [payload setObject:actions forKey:@"actions"];
        [payload setObject:raw ?: @"" forKey:@"llm_raw"];
        NSData *data = [NSJSONSerialization dataWithJSONObject:payload options:NSJSONWritingPrettyPrinted error:nil];
        return [[[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding] autorelease] ?: [payload description];
    }

    NSString *toolNameForCall(NSDictionary *call)
    {
        id value = [call objectForKey:@"tool"] ?: [call objectForKey:@"name"];
        if (!value) {
            NSDictionary *function = [call objectForKey:@"function"];
            if ([function isKindOfClass:[NSDictionary class]]) {
                value = [function objectForKey:@"name"];
            }
        }
        return [value isKindOfClass:[NSString class]] ? value : nil;
    }

    NSDictionary *argsForCall(NSDictionary *call)
    {
        id value = [call objectForKey:@"args"] ?: [call objectForKey:@"arguments"];
        if (!value) {
            NSDictionary *function = [call objectForKey:@"function"];
            if ([function isKindOfClass:[NSDictionary class]]) {
                value = [function objectForKey:@"arguments"];
            }
        }
        if ([value isKindOfClass:[NSDictionary class]]) {
            return value;
        }
        if ([value isKindOfClass:[NSString class]]) {
            NSData *data = [value dataUsingEncoding:NSUTF8StringEncoding];
            id json = data ? [NSJSONSerialization JSONObjectWithData:data options:0 error:nil] : nil;
            if ([json isKindOfClass:[NSDictionary class]]) {
                return json;
            }
        }
        return @{};
    }

    bool planHasUsefulDrumLoop(id calls)
    {
        if (![calls isKindOfClass:[NSArray class]]) return false;
        bool createsTrack = false;
        bool createsClip = false;
        bool addsNotes = false;
        for (NSDictionary *call in (NSArray *)calls) {
            if (![call isKindOfClass:[NSDictionary class]]) continue;
            NSString *tool = toolNameForCall(call);
            NSDictionary *args = argsForCall(call);
            if ([tool isEqualToString:@"create_midi_track"]) createsTrack = true;
            if ([tool isEqualToString:@"clip_create"]) createsClip = true;
            if ([tool isEqualToString:@"midi_notes_add"]) {
                id notes = [args objectForKey:@"notes"];
                addsNotes = [notes isKindOfClass:[NSArray class]] && [notes count] > 0;
            }
        }
        return createsTrack && createsClip && addsNotes;
    }

    NSArray *buildActions(id calls, NSString **error)
    {
        if (![calls isKindOfClass:[NSArray class]]) {
            if (error) {
                *error = @"Plan JSON has no calls array.";
            }
            return nil;
        }
        NSMutableArray *actions = [NSMutableArray array];
        for (NSDictionary *call in (NSArray *)calls) {
            if (![call isKindOfClass:[NSDictionary class]]) {
                continue;
            }
            NSDictionary *action = actionForTool(toolNameForCall(call), argsForCall(call));
            if (action) {
                [actions addObject:action];
            }
        }
        return actions;
    }

    NSDictionary *action(NSString *tool, NSString *address, NSString *description, NSArray *args, bool destructive)
    {
        return @{
            @"tool": tool ?: @"",
            @"address": address ?: @"",
            @"description": description ?: @"",
            @"args": args ?: @[],
            @"destructive": [NSNumber numberWithBool:destructive],
        };
    }

    NSDictionary *deviceLoadAction(NSString *tool, NSDictionary *args)
    {
        int trackIndex = intValue(args, @"track_index", 0);
        NSString *query = stringValue(args, @"query", stringValue(args, @"device_name", @""));
        query = [query stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
        id browserPath = [args objectForKey:@"browser_path"] ?: [args objectForKey:@"path"];
        bool hasBrowserPath = [browserPath isKindOfClass:[NSArray class]]
            ? [(NSArray *)browserPath count] > 0
            : ([browserPath isKindOfClass:[NSString class]] && [(NSString *)browserPath length] > 0);
        if ([query length] == 0 && !hasBrowserPath) return nil;
        NSString *deviceType = normalizedDeviceType(stringValue(args, @"device_type", @"instrument"));
        NSMutableArray *actionArgs = [NSMutableArray arrayWithObjects:@(trackIndex), query, deviceType, nil];
        NSMutableDictionary *body = [NSMutableDictionary dictionaryWithDictionary:@{
            @"track_index": @(trackIndex),
            @"query": query,
            @"device_type": deviceType,
        }];
        NSMutableDictionary *options = [NSMutableDictionary dictionary];
        NSString *presetQuery = stringValue(args, @"preset_query", stringValue(args, @"preset", @""));
        presetQuery = [presetQuery stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
        if ([presetQuery length] > 0) {
            [body setObject:presetQuery forKey:@"preset_query"];
            [options setObject:presetQuery forKey:@"preset_query"];
        }
        if (hasBrowserPath) {
            [body setObject:browserPath forKey:@"browser_path"];
            [options setObject:browserPath forKey:@"browser_path"];
        }
        id allowAmbiguous = [args objectForKey:@"allow_ambiguous"];
        if (allowAmbiguous && [allowAmbiguous boolValue]) {
            [body setObject:@YES forKey:@"allow_ambiguous"];
            [options setObject:@YES forKey:@"allow_ambiguous"];
        }
        if ([options count] > 0) {
            [actionArgs addObject:options];
        }
        return @{
            @"tool": tool ?: @"device_load",
            @"address": @"/api/devices/load",
            @"description": @"Load device through LLM-r Device Bridge",
            @"args": actionArgs,
            @"destructive": @NO,
            @"transport": @"device_bridge",
            @"body": body,
        };
    }

    NSDictionary *actionForTool(NSString *tool, NSDictionary *args)
    {
        if (![tool isKindOfClass:[NSString class]] || ![args isKindOfClass:[NSDictionary class]]) {
            return nil;
        }
        if ([tool isEqualToString:@"create_midi_track"]) return action(tool, @"/live/song/create_midi_track", @"Create MIDI track", @[@(intValue(args, @"index", -1))], false);
        if ([tool isEqualToString:@"create_audio_track"]) return action(tool, @"/live/song/create_audio_track", @"Create audio track", @[@(intValue(args, @"index", -1))], false);
        if ([tool isEqualToString:@"set_tempo"]) return action(tool, @"/live/song/set/tempo", @"Set global tempo", @[@(numberValue(args, @"bpm", 120.0))], false);
        if ([tool isEqualToString:@"fire_clip"]) return action(tool, @"/live/clip/fire", @"Launch clip slot", @[@(intValue(args, @"track_index", 0)), @(intValue(args, @"clip_index", 0))], false);
        if ([tool isEqualToString:@"stop_all_clips"]) return action(tool, @"/live/song/stop_all_clips", @"Stop all running clips", @[], true);
        if ([tool isEqualToString:@"set_track_volume"]) return action(tool, @"/live/track/set/volume", @"Set track volume", @[@(intValue(args, @"track_index", 0)), @(numberValue(args, @"volume", 0.8))], false);
        if ([tool isEqualToString:@"set_track_mute"]) return action(tool, @"/live/track/set/mute", @"Toggle mute", @[@(intValue(args, @"track_index", 0)), boolNumber(args, @"mute", true)], false);
        if ([tool isEqualToString:@"set_track_solo"]) return action(tool, @"/live/track/set/solo", @"Toggle solo", @[@(intValue(args, @"track_index", 0)), boolNumber(args, @"solo", true)], false);
        if ([tool isEqualToString:@"arm_track"]) return action(tool, @"/live/track/set/arm", @"Arm/disarm recording", @[@(intValue(args, @"track_index", 0)), boolNumber(args, @"arm", true)], false);
        if ([tool isEqualToString:@"fire_scene"]) return action(tool, @"/live/scene/fire", @"Launch scene", @[@(intValue(args, @"scene_index", 0))], false);
        if ([tool isEqualToString:@"song_play"]) return action(tool, @"/live/song/start_playing", @"Start transport playback", @[], false);
        if ([tool isEqualToString:@"song_stop"]) return action(tool, @"/live/song/stop_playing", @"Stop transport playback", @[], false);
        if ([tool isEqualToString:@"song_continue"]) return action(tool, @"/live/song/continue_playing", @"Continue playback", @[], false);
        if ([tool isEqualToString:@"song_record"]) return action(tool, @"/live/song/set/session_record", @"Toggle session record", @[boolNumber(args, @"record", true)], false);
        if ([tool isEqualToString:@"song_metronome"]) return action(tool, @"/live/song/set/metronome", @"Toggle metronome", @[boolNumber(args, @"enabled", true)], false);
        if ([tool isEqualToString:@"song_set_time_signature"]) return action(tool, @"/live/song/set/signature_numerator", @"Set time signature", @[@(intValue(args, @"numerator", 4)), @(intValue(args, @"denominator", 4))], false);
        if ([tool isEqualToString:@"song_set_global_quantization"]) return action(tool, @"/live/song/set/clip_trigger_quantization", @"Set global quantization", @[@(intValue(args, @"quantization", 4))], false);
        if ([tool isEqualToString:@"song_set_count_in"]) return action(tool, @"/live/song/set/count_in_duration", @"Set count-in", @[@(intValue(args, @"count_in", 1))], false);
        if ([tool isEqualToString:@"track_rename"]) return action(tool, @"/live/track/set/name", @"Rename track", @[@(intValue(args, @"track_index", 0)), stringValue(args, @"name", @"Track")], false);
        if ([tool isEqualToString:@"track_delete"]) return action(tool, @"/live/song/delete_track", @"Delete track", @[@(intValue(args, @"track_index", 0))], true);
        if ([tool isEqualToString:@"track_duplicate"]) return action(tool, @"/live/song/duplicate_track", @"Duplicate track", @[@(intValue(args, @"track_index", 0))], false);
        if ([tool isEqualToString:@"track_set_pan"]) return action(tool, @"/live/track/set/panning", @"Set track pan", @[@(intValue(args, @"track_index", 0)), @(numberValue(args, @"pan", 0.0))], false);
        if ([tool isEqualToString:@"track_set_send"]) return action(tool, @"/live/track/set/send", @"Set send level", @[@(intValue(args, @"track_index", 0)), @(intValue(args, @"send_index", 0)), @(numberValue(args, @"level", 0.0))], false);
        if ([tool isEqualToString:@"scene_create"]) return action(tool, @"/live/song/create_scene", @"Create scene", @[@(intValue(args, @"scene_index", -1))], false);
        if ([tool isEqualToString:@"scene_delete"]) return action(tool, @"/live/song/delete_scene", @"Delete scene", @[@(intValue(args, @"scene_index", 0))], true);
        if ([tool isEqualToString:@"scene_rename"]) return action(tool, @"/live/scene/set/name", @"Rename scene", @[@(intValue(args, @"scene_index", 0)), stringValue(args, @"name", @"Scene")], false);
        if ([tool isEqualToString:@"clip_create"]) return action(tool, @"/live/clip_slot/create_clip", @"Create clip", @[@(intValue(args, @"track_index", 0)), @(intValue(args, @"clip_index", 0)), @(numberValue(args, @"length_beats", 4.0))], false);
        if ([tool isEqualToString:@"clip_delete"]) return action(tool, @"/live/clip_slot/delete_clip", @"Delete clip", @[@(intValue(args, @"track_index", 0)), @(intValue(args, @"clip_index", 0))], true);
        if ([tool isEqualToString:@"clip_duplicate_loop"]) return action(tool, @"/live/clip/duplicate_loop", @"Duplicate clip loop", @[@(intValue(args, @"track_index", 0)), @(intValue(args, @"clip_index", 0))], false);
        if ([tool isEqualToString:@"clip_duplicate_to"]) return action(tool, @"/live/clip_slot/duplicate_clip_to", @"Duplicate clip to slot", @[@(intValue(args, @"track_index", 0)), @(intValue(args, @"clip_index", 0)), @(intValue(args, @"target_track_index", 0)), @(intValue(args, @"target_clip_index", 0))], false);
        if ([tool isEqualToString:@"clip_rename"]) return action(tool, @"/live/clip/set/name", @"Rename clip", @[@(intValue(args, @"track_index", 0)), @(intValue(args, @"clip_index", 0)), stringValue(args, @"name", @"Clip")], false);
        NSDictionary *simpleClipMap = @{
            @"clip_set_color": @[@"/live/clip/set/color", @"color", @"Set clip color"],
            @"clip_set_color_index": @[@"/live/clip/set/color_index", @"color_index", @"Set clip color index"],
            @"clip_set_start_marker": @[@"/live/clip/set/start_marker", @"start_marker", @"Set clip start marker"],
            @"clip_set_end_marker": @[@"/live/clip/set/end_marker", @"end_marker", @"Set clip end marker"],
            @"clip_set_loop_start": @[@"/live/clip/set/loop_start", @"loop_start", @"Set clip loop start"],
            @"clip_set_loop_end": @[@"/live/clip/set/loop_end", @"loop_end", @"Set clip loop end"],
            @"clip_set_position": @[@"/live/clip/set/position", @"position", @"Set clip position"],
            @"clip_set_gain": @[@"/live/clip/set/gain", @"gain", @"Set clip gain"],
            @"clip_set_pitch_coarse": @[@"/live/clip/set/pitch_coarse", @"semitones", @"Set coarse pitch"],
            @"clip_set_pitch_fine": @[@"/live/clip/set/pitch_fine", @"cents", @"Set fine pitch"],
            @"clip_set_warp_mode": @[@"/live/clip/set/warp_mode", @"warp_mode", @"Set warp mode"],
            @"clip_set_launch_mode": @[@"/live/clip/set/launch_mode", @"launch_mode", @"Set launch mode"],
            @"clip_set_launch_quantization": @[@"/live/clip/set/launch_quantization", @"launch_quantization", @"Set launch quantization"],
            @"clip_set_velocity_amount": @[@"/live/clip/set/velocity_amount", @"velocity_amount", @"Set velocity amount"],
        };
        NSArray *mapped = [simpleClipMap objectForKey:tool];
        if (mapped) return action(tool, mapped[0], mapped[2], @[@(intValue(args, @"track_index", 0)), @(intValue(args, @"clip_index", 0)), @(numberValue(args, mapped[1], 0.0))], false);
        if ([tool isEqualToString:@"clip_set_looping"]) return action(tool, @"/live/clip/set/looping", @"Toggle clip looping", @[@(intValue(args, @"track_index", 0)), @(intValue(args, @"clip_index", 0)), boolNumber(args, @"looping", true)], false);
        if ([tool isEqualToString:@"clip_set_warping"]) return action(tool, @"/live/clip/set/warping", @"Toggle warping", @[@(intValue(args, @"track_index", 0)), @(intValue(args, @"clip_index", 0)), boolNumber(args, @"warping", true)], false);
        if ([tool isEqualToString:@"clip_set_ram_mode"]) return action(tool, @"/live/clip/set/ram_mode", @"Toggle RAM mode", @[@(intValue(args, @"track_index", 0)), @(intValue(args, @"clip_index", 0)), boolNumber(args, @"ram_mode", true)], false);
        if ([tool isEqualToString:@"clip_set_muted"]) return action(tool, @"/live/clip/set/muted", @"Mute clip", @[@(intValue(args, @"track_index", 0)), @(intValue(args, @"clip_index", 0)), boolNumber(args, @"muted", true)], false);
        if ([tool isEqualToString:@"midi_notes_get"]) return midiRangeAction(tool, @"/live/clip/get/notes", @"Request MIDI notes", args, false);
        if ([tool isEqualToString:@"midi_notes_remove"]) return midiRangeAction(tool, @"/live/clip/remove/notes", @"Remove MIDI notes", args, true);
        if ([tool isEqualToString:@"midi_notes_clear"]) return action(tool, @"/live/clip/remove/notes", @"Clear MIDI notes", @[@(intValue(args, @"track_index", 0)), @(intValue(args, @"clip_index", 0))], true);
        if ([tool isEqualToString:@"midi_notes_add"]) return midiAddAction(tool, args);
        if ([tool hasPrefix:@"device_get_parameter"]) return deviceGetAction(tool, args);
        if ([tool isEqualToString:@"device_load"]) return deviceLoadAction(tool, args);
        if ([tool isEqualToString:@"device_set_parameter"]) return action(tool, @"/live/device/set/parameter/value", @"Set device parameter", @[@(intValue(args, @"track_index", 0)), @(intValue(args, @"device_index", 0)), @(semanticParameterIndex(args, intValue(args, @"parameter_index", 0))), @(clampedNumberValue(args, @"value", 0.0, 0.0, 1.0))], false);
        if ([tool isEqualToString:@"device_set_parameters"]) return deviceSetParametersAction(tool, args);
        if ([tool isEqualToString:@"device_delete"]) return action(tool, @"/live/track/delete_device", @"Delete device", @[@(intValue(args, @"track_index", 0)), @(intValue(args, @"device_index", 0))], true);
        if ([tool isEqualToString:@"utility_undo"]) return action(tool, @"/live/song/undo", @"Undo", @[], false);
        if ([tool isEqualToString:@"utility_redo"]) return action(tool, @"/live/song/redo", @"Redo", @[], false);
        return nil;
    }

    NSDictionary *midiRangeAction(NSString *tool, NSString *address, NSString *description, NSDictionary *args, bool destructive)
    {
        NSMutableArray *payload = [NSMutableArray arrayWithObjects:@(intValue(args, @"track_index", 0)), @(intValue(args, @"clip_index", 0)), nil];
        if ([args objectForKey:@"start_pitch"] || [args objectForKey:@"pitch_span"] ||
            [args objectForKey:@"start_time"] || [args objectForKey:@"time_span"]) {
            [payload addObject:@(intValue(args, @"start_pitch", 0))];
            [payload addObject:@(intValue(args, @"pitch_span", 128))];
            [payload addObject:@(numberValue(args, @"start_time", 0.0))];
            [payload addObject:@(numberValue(args, @"time_span", 16384.0))];
        }
        return action(tool, address, description, payload, destructive);
    }

    NSDictionary *midiAddAction(NSString *tool, NSDictionary *args)
    {
        NSMutableArray *payload = [NSMutableArray arrayWithObjects:@(intValue(args, @"track_index", 0)), @(intValue(args, @"clip_index", 0)), nil];
        NSArray *notes = [args objectForKey:@"notes"];
        if (![notes isKindOfClass:[NSArray class]] || [notes count] == 0) {
            return nil;
        }
        for (NSDictionary *note in notes) {
            if (![note isKindOfClass:[NSDictionary class]]) {
                continue;
            }
            [payload addObject:@(intValue(note, @"pitch", 60))];
            [payload addObject:@(numberValue(note, @"start_time", 0.0))];
            [payload addObject:@(numberValue(note, @"duration", 0.25))];
            [payload addObject:@(numberValue(note, @"velocity", 100.0))];
            [payload addObject:boolNumber(note, @"mute", false)];
        }
        return action(tool, @"/live/clip/add/notes", @"Add MIDI notes", payload, false);
    }

    NSDictionary *deviceGetAction(NSString *tool, NSDictionary *args)
    {
        NSDictionary *addresses = @{
            @"device_get_parameters": @"/live/device/get/parameters/value",
            @"device_get_parameter": @"/live/device/get/parameter/value",
            @"device_get_parameter_name": @"/live/device/get/parameter/name",
            @"device_get_parameter_value_string": @"/live/device/get/parameter/value_string",
            @"device_get_parameter_names": @"/live/device/get/parameters/name",
            @"device_get_parameter_min_values": @"/live/device/get/parameters/min",
            @"device_get_parameter_max_values": @"/live/device/get/parameters/max",
        };
        NSMutableArray *payload = [NSMutableArray arrayWithObjects:@(intValue(args, @"track_index", 0)), @(intValue(args, @"device_index", 0)), nil];
        if ([tool isEqualToString:@"device_get_parameter"] ||
            [tool isEqualToString:@"device_get_parameter_name"] ||
            [tool isEqualToString:@"device_get_parameter_value_string"]) {
            [payload addObject:@(intValue(args, @"parameter_index", 0))];
        }
        return action(tool, [addresses objectForKey:tool], @"Device query", payload, false);
    }

    NSDictionary *deviceSetParametersAction(NSString *tool, NSDictionary *args)
    {
        NSMutableArray *payload = [NSMutableArray arrayWithObjects:@(intValue(args, @"track_index", 0)), @(intValue(args, @"device_index", 0)), nil];
        for (id value in [args objectForKey:@"values"]) {
            double normalized = [value doubleValue];
            if (normalized < 0.0) normalized = 0.0;
            if (normalized > 1.0) normalized = 1.0;
            [payload addObject:@(normalized)];
        }
        return action(tool, @"/live/device/set/parameters/value", @"Set device parameters", payload, false);
    }

    // ─── AbletonOSC detection & install ──────────────────────────

    static NSString *midiRemoteScriptsPath()
    {
        NSFileManager *fm = [NSFileManager defaultManager];
        NSArray<NSString *> *apps = [fm contentsOfDirectoryAtPath:@"/Applications" error:nil];
        for (NSString *app in apps) {
            if (![app hasPrefix:@"Ableton Live"]) continue;
            NSString *scripts = [NSString stringWithFormat:
                @"/Applications/%@/Contents/App-Resources/MIDI Remote Scripts", app];
            BOOL isDir = NO;
            if ([fm fileExistsAtPath:scripts isDirectory:&isDir] && isDir) {
                return scripts;
            }
        }
        return nil;
    }

    static bool abletonOSCInstalled()
    {
        NSString *scripts = midiRemoteScriptsPath();
        if (!scripts) return false;
        BOOL isDir = NO;
        NSString *path = [scripts stringByAppendingPathComponent:@"AbletonOSC"];
        return [[NSFileManager defaultManager] fileExistsAtPath:path isDirectory:&isDir] && isDir;
    }

    void installAbletonOSC(NSString *scriptsPath)
    {
        setStatus(@"Downloading AbletonOSC…");
        addRef();
        dispatch_async(dispatch_get_global_queue(QOS_CLASS_UTILITY, 0), ^{
            NSString *tmpZip  = @"/tmp/llmr_AbletonOSC.zip";
            NSString *tmpDir  = @"/tmp/llmr_aosc_extract";

            // Download via NSURLSession (avoids child-process sandbox restrictions)
            __block NSError *dlError = nil;
            __block BOOL dlDone = NO;
            dispatch_semaphore_t sema = dispatch_semaphore_create(0);

            NSURL *archiveURL = [NSURL URLWithString:
                @"https://github.com/ideoforms/AbletonOSC/archive/refs/heads/master.zip"];
            NSURLSessionDownloadTask *dlTask =
                [[NSURLSession sharedSession]
                    downloadTaskWithURL:archiveURL
                    completionHandler:^(NSURL *location, NSURLResponse *resp, NSError *err) {
                        if (err) {
                            dlError = [err retain];
                        } else {
                            NSHTTPURLResponse *http = (NSHTTPURLResponse *)resp;
                            if ([http statusCode] == 200 && location) {
                                [[NSFileManager defaultManager]
                                    removeItemAtPath:tmpZip error:nil];
                                [[NSFileManager defaultManager]
                                    moveItemAtURL:location
                                    toURL:[NSURL fileURLWithPath:tmpZip]
                                    error:&dlError];
                                if (!dlError) dlDone = YES;
                            } else {
                                dlError = [[NSError alloc]
                                    initWithDomain:@"HTTP"
                                    code:([http statusCode] ?: 0)
                                    userInfo:nil];
                            }
                        }
                        dispatch_semaphore_signal(sema);
                    }];
            [dlTask resume];
            dispatch_semaphore_wait(sema,
                dispatch_time(DISPATCH_TIME_NOW, 60LL * NSEC_PER_SEC));

            if (!dlDone) {
                NSString *errMsg = dlError
                    ? [dlError localizedDescription]
                    : @"Request timed out.";
                [dlError release];
                dispatch_async(dispatch_get_main_queue(), ^{
                    setStatus(@"AbletonOSC download failed.");
                    NSAlert *a = [[NSAlert alloc] init];
                    [a setMessageText:@"Download Failed"];
                    [a setInformativeText:[NSString stringWithFormat:
                        @"Could not download AbletonOSC: %@\n\n"
                        @"Please install manually from https://github.com/ideoforms/AbletonOSC",
                        errMsg]];
                    [a runModal]; [a release];
                    release();
                });
                return;
            }
            [dlError release];

            // Extract
            [[NSFileManager defaultManager] removeItemAtPath:tmpDir error:nil];
            NSTask *unzip = [[NSTask alloc] init];
            [unzip setLaunchPath:@"/usr/bin/unzip"];
            [unzip setArguments:@[@"-o", @"-q", tmpZip, @"-d", tmpDir]];
            [unzip launch];
            [unzip waitUntilExit];
            int unzipExit = [unzip terminationStatus];
            [unzip release];

            if (unzipExit != 0) {
                dispatch_async(dispatch_get_main_queue(), ^{
                    setStatus(@"AbletonOSC extraction failed.");
                    NSAlert *a = [[NSAlert alloc] init];
                    [a setMessageText:@"Extraction Failed"];
                    [a setInformativeText:@"Could not unzip the downloaded AbletonOSC archive. Please install manually from https://github.com/ideoforms/AbletonOSC"];
                    [a runModal]; [a release];
                    release();
                });
                return;
            }

            // Find the top-level extracted folder (e.g. AbletonOSC-master/) —
            // the archive root itself is the MIDI Remote Script (contains __init__.py)
            NSString *src = nil;
            NSArray *topLevel = [[NSFileManager defaultManager]
                contentsOfDirectoryAtPath:tmpDir error:nil];
            for (NSString *item in topLevel) {
                if ([item hasPrefix:@"AbletonOSC"]) {
                    NSString *candidate = [tmpDir stringByAppendingPathComponent:item];
                    BOOL isDir = NO;
                    if ([[NSFileManager defaultManager]
                             fileExistsAtPath:candidate isDirectory:&isDir] && isDir) {
                        src = candidate;
                        break;
                    }
                }
            }

            if (!src) {
                dispatch_async(dispatch_get_main_queue(), ^{
                    setStatus(@"AbletonOSC extraction failed.");
                    NSAlert *a = [[NSAlert alloc] init];
                    [a setMessageText:@"Extraction Failed"];
                    [a setInformativeText:@"Could not find the AbletonOSC folder in the downloaded archive. Please install manually from https://github.com/ideoforms/AbletonOSC"];
                    [a runModal]; [a release];
                    release();
                });
                return;
            }

            // Copy (try directly first, then via temp shell script with admin privileges)
            NSString *dst = [scriptsPath stringByAppendingPathComponent:@"AbletonOSC"];
            NSError *copyErr = nil;
            BOOL copied = [[NSFileManager defaultManager] copyItemAtPath:src toPath:dst error:&copyErr];

            if (!copied) {
                // Write a temp shell script to avoid path-escaping issues in AppleScript
                NSString *scriptPath = @"/tmp/llmr_install_aosc.sh";
                NSString *scriptContent = [NSString stringWithFormat:
                    @"#!/bin/sh\ncp -r \"%@\" \"%@\"\n", src, dst];
                [scriptContent writeToFile:scriptPath
                               atomically:YES
                                 encoding:NSUTF8StringEncoding
                                    error:nil];
                NSTask *chmod = [[NSTask alloc] init];
                [chmod setLaunchPath:@"/bin/chmod"];
                [chmod setArguments:@[@"+x", scriptPath]];
                [chmod launch]; [chmod waitUntilExit]; [chmod release];

                NSTask *osa = [[NSTask alloc] init];
                [osa setLaunchPath:@"/usr/bin/osascript"];
                [osa setArguments:@[@"-e",
                    @"do shell script \"/tmp/llmr_install_aosc.sh\" with administrator privileges"]];
                [osa launch];
                [osa waitUntilExit];
                copied = ([osa terminationStatus] == 0);
                [osa release];
            }

            dispatch_async(dispatch_get_main_queue(), ^{
                if (copied) {
                    setStatus(@"AbletonOSC installed — enable it in Ableton MIDI preferences.");
                    NSAlert *a = [[NSAlert alloc] init];
                    [a setMessageText:@"AbletonOSC Installed"];
                    [a setInformativeText:
                        @"AbletonOSC has been installed successfully.\n\n"
                        @"⚠️ You must restart Ableton Live for the installation to take effect.\n\n"
                        @"Then enable it:\n"
                        @"1. Open Ableton Live → Preferences → Link/Tempo/MIDI\n"
                        @"2. Set a Control Surface slot to ‘AbletonOSC’\n"
                        @"3. Click OK — LLM-r will start working immediately."];
                    [a runModal]; [a release];
                } else {
                    setStatus(@"AbletonOSC installation failed.");
                    NSAlert *a = [[NSAlert alloc] init];
                    [a setMessageText:@"Installation Failed"];
                    [a setInformativeText:
                        @"Could not install AbletonOSC automatically.\n\n"
                        @"To install manually:\n"
                        @"1. Download from https://github.com/ideoforms/AbletonOSC\n"
                        @"2. Copy the AbletonOSC folder to:\n"
                        @"   Ableton Live.app/Contents/App-Resources/MIDI Remote Scripts/\n"
                        @"3. Restart Ableton Live and enable it in Preferences → Link/Tempo/MIDI."];
                    [a runModal]; [a release];
                }
                release();
            });
        });
    }

    void checkAbletonOSCOnFirstUse()
    {
        static bool s_checked = false;
        if (s_checked) return;
        s_checked = true;
        if (abletonOSCInstalled()) return;

        NSString *scriptsPath = midiRemoteScriptsPath();
        if (!scriptsPath) return; // Can't find Ableton — don't bother

        NSAlert *alert = [[NSAlert alloc] init];
        [alert setMessageText:@"AbletonOSC Not Found"];
        [alert setInformativeText:
            @"LLM-r needs AbletonOSC to send commands to Ableton Live, "
            @"but it is not installed.\n\n"
            @"Would you like to install it automatically now?"];
        [alert addButtonWithTitle:@"Install AbletonOSC"];
        [alert addButtonWithTitle:@"Not Now"];
        [alert setAlertStyle:NSAlertStyleInformational];

        NSModalResponse resp = [alert runModal];
        [alert release];

        if (resp == NSAlertFirstButtonReturn) {
            installAbletonOSC(scriptsPath);
        }
    }

    static NSString *bridgeFolderName()
    {
        return @"LLMR_Bridge";
    }

    static NSString *legacyBridgeFolderName()
    {
        return @"LLMRDeviceBridge";
    }

    static NSString *bridgeUserLibrarySettingsKey()
    {
        return @"llmr.vst3.bridge_user_library_path";
    }

    static NSString *normalizedPath(NSString *path)
    {
        NSString *raw = path ?: @"";
        NSString *trimmed = [raw stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
        if ([trimmed length] == 0) return @"";
        return [trimmed stringByStandardizingPath];
    }

    static NSString *remoteScriptsPathForUserLibrary(NSString *userLibraryPath)
    {
        NSString *library = normalizedPath(userLibraryPath);
        if ([library length] == 0) return @"";
        return [library stringByAppendingPathComponent:@"Remote Scripts"];
    }

    static NSString *bridgeInstallTargetForUserLibrary(NSString *userLibraryPath)
    {
        NSString *scripts = remoteScriptsPathForUserLibrary(userLibraryPath);
        if ([scripts length] == 0) return @"";
        return [scripts stringByAppendingPathComponent:bridgeFolderName()];
    }

    static NSString *bridgeInitPathForUserLibrary(NSString *userLibraryPath)
    {
        NSString *target = bridgeInstallTargetForUserLibrary(userLibraryPath);
        if ([target length] == 0) return @"";
        return [target stringByAppendingPathComponent:@"__init__.py"];
    }

    static NSString *bridgeDoubleNestedInitPathForUserLibrary(NSString *userLibraryPath)
    {
        NSString *target = bridgeInstallTargetForUserLibrary(userLibraryPath);
        if ([target length] == 0) return @"";
        return [[target stringByAppendingPathComponent:bridgeFolderName()] stringByAppendingPathComponent:@"__init__.py"];
    }

    static void addDetectedLibraryCandidate(NSMutableArray<NSString *> *paths, NSString *candidate)
    {
        NSFileManager *fm = [NSFileManager defaultManager];
        NSString *normalized = normalizedPath(candidate);
        if ([normalized length] == 0) return;
        BOOL isDir = NO;
        if (![fm fileExistsAtPath:normalized isDirectory:&isDir] || !isDir) return;
        if (![paths containsObject:normalized]) {
            [paths addObject:normalized];
        }
    }

    static NSArray<NSString *> *detectedUserLibraryCandidates()
    {
        NSFileManager *fm = [NSFileManager defaultManager];
        NSMutableArray<NSString *> *paths = [NSMutableArray array];

        NSString *music = [NSSearchPathForDirectoriesInDomains(NSMusicDirectory, NSUserDomainMask, YES) firstObject];
        if ([music length] == 0) {
            music = [NSHomeDirectory() stringByAppendingPathComponent:@"Music"];
        }
        addDetectedLibraryCandidate(paths, [music stringByAppendingPathComponent:@"Ableton/User Library"]);

        NSString *volumesRoot = @"/Volumes";
        NSArray<NSString *> *volumes = [fm contentsOfDirectoryAtPath:volumesRoot error:nil] ?: @[];
        for (NSString *volume in volumes) {
            NSString *root = [volumesRoot stringByAppendingPathComponent:volume];
            BOOL isDir = NO;
            if (![fm fileExistsAtPath:root isDirectory:&isDir] || !isDir) continue;

            addDetectedLibraryCandidate(paths, [root stringByAppendingPathComponent:@"Ableton/User Library"]);

            NSArray<NSString *> *firstLevel = [fm contentsOfDirectoryAtPath:root error:nil] ?: @[];
            for (NSString *a in firstLevel) {
                NSString *aPath = [root stringByAppendingPathComponent:a];
                if (![fm fileExistsAtPath:aPath isDirectory:&isDir] || !isDir) continue;
                NSArray<NSString *> *secondLevel = [fm contentsOfDirectoryAtPath:aPath error:nil] ?: @[];
                for (NSString *b in secondLevel) {
                    NSString *bPath = [aPath stringByAppendingPathComponent:b];
                    if (![fm fileExistsAtPath:bPath isDirectory:&isDir] || !isDir) continue;
                    NSString *lowerA = [a lowercaseString];
                    NSString *lowerB = [b lowercaseString];
                    if ([lowerA containsString:@"ableton"] && [lowerB containsString:@"user library"]) {
                        addDetectedLibraryCandidate(paths, bPath);
                    }
                }
            }

            NSDirectoryEnumerator *enumerator = [fm enumeratorAtURL:[NSURL fileURLWithPath:root]
                                          includingPropertiesForKeys:@[NSURLIsDirectoryKey, NSURLPathKey]
                                                             options:NSDirectoryEnumerationSkipsHiddenFiles
                                                        errorHandler:nil];
            for (NSURL *entry in enumerator) {
                NSNumber *isDirectory = nil;
                [entry getResourceValue:&isDirectory forKey:NSURLIsDirectoryKey error:nil];
                if (![isDirectory boolValue]) continue;
                NSString *last = [[entry path] lastPathComponent];
                if ([last isEqualToString:@"Remote Scripts"]) {
                    addDetectedLibraryCandidate(paths, [[entry path] stringByDeletingLastPathComponent]);
                }
            }
        }

        return paths;
    }

    NSString *llmrDeviceBridgeInstallSource()
    {
        NSString *bundlePath = [[NSBundle bundleWithIdentifier:@"net.tomaslaurenzo.llm-r.vst3"] resourcePath];
        NSString *scriptPath = [[bundlePath stringByAppendingPathComponent:@"RemoteScripts"]
            stringByAppendingPathComponent:@"LLMRDeviceBridge"];
        BOOL isDir = NO;
        if ([[NSFileManager defaultManager] fileExistsAtPath:scriptPath isDirectory:&isDir] && isDir) {
            return scriptPath;
        }

        const char *home = getenv("HOME");
        NSString *devPath = [NSString stringWithFormat:
            @"%s/devel/ml-llm/llm/LLM-r/remote_scripts/LLMRDeviceBridge",
            home ? home : ""];
        if ([[NSFileManager defaultManager] fileExistsAtPath:devPath isDirectory:&isDir] && isDir) {
            return devPath;
        }
        return nil;
    }

    bool bridgeFolderExistsAtPath(NSString *path)
    {
        BOOL isDir = NO;
        return [[NSFileManager defaultManager] fileExistsAtPath:path isDirectory:&isDir] && isDir;
    }

    bool bridgeInitFileExistsForUserLibrary(NSString *userLibraryPath)
    {
        return [[NSFileManager defaultManager] fileExistsAtPath:bridgeInitPathForUserLibrary(userLibraryPath)];
    }

    bool bridgeDoubleNestedForUserLibrary(NSString *userLibraryPath)
    {
        return [[NSFileManager defaultManager] fileExistsAtPath:bridgeDoubleNestedInitPathForUserLibrary(userLibraryPath)];
    }

    NSString *bridgeInstallStatusForUserLibrary(NSString *userLibraryPath)
    {
        NSString *library = normalizedPath(userLibraryPath);
        if ([library length] == 0) {
            return @"Bridge status: Not installed\nChoose your Ableton User Library first. In Live, right-click User Library in the Browser and choose Show in Finder.";
        }
        if (bridgeInitFileExistsForUserLibrary(library)) {
            return @"Bridge status: Installed";
        }
        if (bridgeDoubleNestedForUserLibrary(library)) {
            return @"Bridge status: Installed but invalid structure\nBridge appears to be double-nested. Reinstalling will replace it with the correct folder structure.";
        }
        return @"Bridge status: Not installed";
    }

    bool installLLMRBridgeToUserLibrary(NSString *userLibraryPath, NSString **errorText)
    {
        NSString *library = normalizedPath(userLibraryPath);
        if ([library length] == 0) {
            if (errorText) *errorText = @"Choose your Ableton User Library first.";
            return false;
        }

        NSString *src = llmrDeviceBridgeInstallSource();
        if (!src) {
            if (errorText) *errorText = @"Bundled LLMRDeviceBridge Remote Script was not found.";
            return false;
        }

        NSFileManager *fm = [NSFileManager defaultManager];
        NSString *scriptsPath = remoteScriptsPathForUserLibrary(library);
        NSString *target = bridgeInstallTargetForUserLibrary(library);
        NSString *legacy = [scriptsPath stringByAppendingPathComponent:legacyBridgeFolderName()];
        NSError *err = nil;

        if (![fm createDirectoryAtPath:scriptsPath withIntermediateDirectories:YES attributes:nil error:&err]) {
            if (errorText) *errorText = [err localizedDescription] ?: @"Could not create Remote Scripts directory.";
            return false;
        }

        if ([fm fileExistsAtPath:target]) {
            if (![fm removeItemAtPath:target error:&err]) {
                if (errorText) *errorText = [err localizedDescription] ?: @"Could not replace existing bridge install.";
                return false;
            }
        }
        if (bridgeDoubleNestedForUserLibrary(library)) {
            [fm removeItemAtPath:[target stringByAppendingPathComponent:bridgeFolderName()] error:nil];
        }
        if ([fm fileExistsAtPath:legacy]) {
            [fm removeItemAtPath:legacy error:nil];
        }

        if (![fm copyItemAtPath:src toPath:target error:&err]) {
            if (errorText) *errorText = [err localizedDescription] ?: @"Could not copy bridge files to selected User Library.";
            return false;
        }
        if (!bridgeInitFileExistsForUserLibrary(library)) {
            if (errorText) *errorText = @"Installed bridge folder is missing __init__.py.";
            return false;
        }
        return true;
    }

    bool llmrBridgeInstalledAnywhere()
    {
        for (NSString *library in detectedUserLibraryCandidates()) {
            if (bridgeInitFileExistsForUserLibrary(library)) {
                return true;
            }
        }
        return false;
    }

    void checkLLMRDeviceBridgeOnFirstUse()
    {
        static bool s_checked = false;
        if (s_checked) return;
        s_checked = true;
        if (llmrBridgeInstalledAnywhere()) return;
        if (!llmrDeviceBridgeInstallSource()) return;

        NSString *selectedLibrary = normalizedPath([[NSUserDefaults standardUserDefaults] stringForKey:bridgeUserLibrarySettingsKey()]);
        if ([selectedLibrary length] == 0) {
            setStatus(@"Choose your Ableton User Library in Settings before installing Bridge.");
            return;
        }

        NSAlert *alert = [[NSAlert alloc] init];
        [alert setMessageText:@"LLM-r Device Bridge Not Found"];
        [alert setInformativeText:
            @"Loading instruments, audio effects, MIDI effects, and plug-ins requires "
            @"the LLM-r Device Bridge Remote Script.\n\n"
            @"Install it now? After installing, restart Ableton Live and enable "
            @"LLMR_Bridge in an empty Control Surface slot."];
        [alert addButtonWithTitle:@"Install Device Bridge"];
        [alert addButtonWithTitle:@"Not Now"];
        [alert setAlertStyle:NSAlertStyleInformational];

        NSModalResponse resp = [alert runModal];
        [alert release];
        if (resp != NSAlertFirstButtonReturn) return;

        NSString *error = nil;
        bool ok = installLLMRBridgeToUserLibrary(selectedLibrary, &error);
        NSAlert *done = [[NSAlert alloc] init];
        if (ok) {
            [done setMessageText:@"LLM-r Device Bridge Installed"];
            [done setInformativeText:
                @"Restart Ableton Live, then open Preferences -> Link/Tempo/MIDI "
                @"and set a Control Surface slot to LLMR_Bridge."];
            setStatus(@"Device Bridge installed - restart Ableton Live and enable it.");
        } else {
            [done setMessageText:@"Device Bridge Installation Failed"];
            [done setInformativeText:error ?: @"Could not install LLMR_Bridge."];
            setStatus(@"Device Bridge installation failed.");
        }
        [done runModal];
        [done release];
    }

    static void appendPaddedString(NSMutableData *data, NSString *string)
    {
        NSData *utf8 = [string dataUsingEncoding:NSUTF8StringEncoding];
        [data appendData:utf8];
        uint8_t zero = 0;
        [data appendBytes:&zero length:1];
        while ([data length] % 4 != 0) {
            [data appendBytes:&zero length:1];
        }
    }

    static void appendInt32(NSMutableData *data, int value)
    {
        uint32_t net = htonl(static_cast<uint32_t>(value));
        [data appendBytes:&net length:sizeof(net)];
    }

    static void appendFloat32(NSMutableData *data, double value)
    {
        float f = static_cast<float>(value);
        uint32_t raw = 0;
        std::memcpy(&raw, &f, sizeof(raw));
        raw = htonl(raw);
        [data appendBytes:&raw length:sizeof(raw)];
    }

    bool sendOsc(NSString *host, int port, NSString *address, NSArray *args, NSString **error)
    {
        NSMutableData *packet = [NSMutableData data];
        appendPaddedString(packet, address);
        NSMutableString *types = [NSMutableString stringWithString:@","];
        for (id value in args) {
            if ([value isKindOfClass:[NSString class]]) {
                NSString *sv = (NSString *)value;
                if ([sv containsString:@"."]) {
                    [types appendString:@"f"];
                } else if ([sv length] > 0 && ([sv doubleValue] != 0.0 || [sv isEqualToString:@"0"])) {
                    [types appendString:@"i"];
                } else {
                    [types appendString:@"s"];
                }
            } else if ([value isKindOfClass:[NSDecimalNumber class]]) {
                [types appendString:@"f"];
            } else if (CFNumberIsFloatType((CFNumberRef)value)) {
                [types appendString:@"f"];
            } else {
                [types appendString:@"i"];
            }
        }
        appendPaddedString(packet, types);
        for (id value in args) {
            if ([value isKindOfClass:[NSString class]]) {
                NSString *sv = (NSString *)value;
                if ([sv containsString:@"."]) {
                    appendFloat32(packet, [sv doubleValue]);
                } else if ([sv length] > 0 && ([sv doubleValue] != 0.0 || [sv isEqualToString:@"0"])) {
                    appendInt32(packet, (int32_t)[sv integerValue]);
                } else {
                    appendPaddedString(packet, sv);
                }
            } else if ([value isKindOfClass:[NSDecimalNumber class]]) {
                appendFloat32(packet, [value doubleValue]);
            } else if (CFNumberIsFloatType((CFNumberRef)value)) {
                appendFloat32(packet, [value doubleValue]);
            } else {
                appendInt32(packet, [value intValue]);
            }
        }

        int sock = socket(AF_INET, SOCK_DGRAM, 0);
        if (sock < 0) {
            if (error) {
                *error = @"Could not create UDP socket.";
            }
            return false;
        }

        struct sockaddr_in addr {};
        addr.sin_family = AF_INET;
        addr.sin_port = htons(static_cast<uint16_t>(port));
        if (inet_pton(AF_INET, [host UTF8String], &addr.sin_addr) != 1) {
            struct hostent *he = gethostbyname([host UTF8String]);
            if (!he || he->h_addrtype != AF_INET) {
                close(sock);
                if (error) {
                    *error = @"Could not resolve AbletonOSC host.";
                }
                return false;
            }
            std::memcpy(&addr.sin_addr, he->h_addr_list[0], sizeof(addr.sin_addr));
        }

        ssize_t sent = sendto(sock, [packet bytes], [packet length], 0,
                              reinterpret_cast<struct sockaddr *>(&addr), sizeof(addr));
        close(sock);
        if (sent < 0 || static_cast<NSUInteger>(sent) != [packet length]) {
            if (error) {
                *error = @"Could not send OSC packet.";
            }
            return false;
        }
        return true;
    }
#endif

    std::atomic<uint32> refCount_{1};
    ViewRect rect_{0, 0, 960, 720};
    IPlugFrame *plugFrame_{nullptr};
#if defined(__APPLE__)
    NSView *view_{nullptr};
    NSMutableArray *targets_{nullptr};
    NSArray *lastActions_{nullptr};
    NSMutableAttributedString *chatHistory_{nullptr}; // survives removed/attached
    NSString *lastRawResponse_{nullptr};
    bool activeRawTab_{false};

    // Chat view
    NSView *chatView_{nullptr};
    NSTextView *chatHistoryView_{nullptr};
    NSTextView *rawResponseView_{nullptr};
    NSTextView *chatInputView_{nullptr};
    NSScrollView *chatInputScrollView_{nullptr};
    NSTextField *chatPromptPlaceholderLabel_{nullptr};
    NSTextField *chatStatusLabel_{nullptr};
    NSTextField *chatModelLabel_{nullptr};
    NSTextField *chatOscLabel_{nullptr};
    NSTextField *chatBridgeLabel_{nullptr};
    NSTextField *chatDryRunLabel_{nullptr};
    NSButton *chatSendButton_{nullptr};
    NSButton *chatCancelButton_{nullptr};
    NSButton *chatExecuteButton_{nullptr};
    NSButton *chatPreviewButton_{nullptr};
    NSButton *chatAutoApproveButton_{nullptr};
    NSButton *chatSettingsButton_{nullptr};
    NSButton *chatTabButton_{nullptr};
    NSButton *rawTabButton_{nullptr};

    // Settings overlay
    NSView *settingsView_{nullptr};
    NSWindow *settingsWindow_{nullptr};
    NSPopUpButton *settingsProviderCombo_{nullptr};
    NSPopUpButton *settingsModelField_{nullptr};
    NSTextField *settingsCustomModelField_{nullptr};
    NSTextField *settingsModelStatusLabel_{nullptr};
    NSTextField *settingsEndpointField_{nullptr};
    NSTextField *settingsApiKeyField_{nullptr};
    NSTextField *settingsOscHostField_{nullptr};
    NSTextField *settingsOscPortField_{nullptr};
    NSTextField *settingsBridgeHostField_{nullptr};
    NSTextField *settingsBridgePortField_{nullptr};
    NSPopUpButton *settingsBridgeLibraryCandidatesCombo_{nullptr};
    NSTextField *settingsBridgeLibraryLabel_{nullptr};
    NSTextField *settingsBridgeInstallTargetLabel_{nullptr};
    NSButton *settingsBridgeInstallButton_{nullptr};
    NSButton *settingsBridgeRevealButton_{nullptr};
    NSButton *settingsExtraPromptButton_{nullptr};
    NSButton *settingsDestructiveButton_{nullptr};
    NSButton *settingsDryRunButton_{nullptr};
    NSButton *settingsAutoApproveButton_{nullptr};
    NSView *settingsMainView_{nullptr};
    NSView *settingsAdvancedView_{nullptr};

    // Ollama controls (inside settings)
    NSTextField *ollamaStatusLabel_{nullptr};
    NSTextField *deviceBridgeStatusLabel_{nullptr};
    NSPopUpButton *ollamaModelField_{nullptr};
    NSPopUpButton *ollamaModelsCombo_{nullptr};
    bool ollamaOnlineModelsLoaded_{false};
    bool ollamaOnlineLoadInFlight_{false};
    bool ollamaListInFlight_{false};
    bool deviceBridgeCheckInFlight_{false};
    bool deviceBridgeChecked_{false};
    bool deviceBridgeReachable_{false};
    NSString *bridgeUserLibraryPath_{nullptr};
    bool hasDryRunCurrentPlan_{false};
    std::atomic<bool> operationCancelRequested_{false};
    std::atomic<bool> operationBusy_{false};

    NSWindow *systemPromptsWindow_{nullptr};
    NSPopUpButton *systemPromptPresetCombo_{nullptr};
    NSTextView *systemPromptEditor_{nullptr};

    // Local Remote Script bridge for browser/device loading.
    int deviceBridgePort_{8788};
#endif
};

class LlmrController final : public IEditController {
public:
    LlmrController() = default;

    tresult queryInterface(const TUID iid, void **obj) override
    {
        if (!obj) {
            return kInvalidArgument;
        }
        if (iidEqual(iid, kFUnknownIID) || iidEqual(iid, kIPluginBaseIID) ||
            iidEqual(iid, kIEditControllerIID)) {
            addRef();
            *obj = static_cast<IEditController *>(this);
            return kResultOk;
        }
        *obj = nullptr;
        return kNoInterface;
    }

    uint32 addRef() override { return ++refCount_; }
    uint32 release() override
    {
        const auto count = --refCount_;
        if (count == 0) {
            delete this;
        }
        return count;
    }

    tresult initialize(FUnknown *context) override
    {
        (void)context;
        return kResultOk;
    }

    tresult terminate() override { return kResultOk; }

    tresult setComponentState(IBStream *state) override
    {
        (void)state;
        return kResultOk;
    }

    tresult setState(IBStream *state) override
    {
        (void)state;
        return kResultOk;
    }

    tresult getState(IBStream *state) override
    {
        (void)state;
        return kResultOk;
    }

    int32 getParameterCount() override { return 0; }

    tresult getParameterInfo(int32 paramIndex, ParameterInfo &info) override
    {
        (void)paramIndex;
        std::memset(&info, 0, sizeof(info));
        return kInvalidArgument;
    }

    tresult getParamStringByValue(ParamID id, ParamValue valueNormalized,
                                  String128 string) override
    {
        (void)id;
        (void)valueNormalized;
        if (string) {
            string[0] = 0;
        }
        return kResultFalse;
    }

    tresult getParamValueByString(ParamID id, TChar *string,
                                  ParamValue &valueNormalized) override
    {
        (void)id;
        (void)string;
        valueNormalized = 0.0;
        return kResultFalse;
    }

    ParamValue normalizedParamToPlain(ParamID id, ParamValue valueNormalized) override
    {
        (void)id;
        return valueNormalized;
    }

    ParamValue plainParamToNormalized(ParamID id, ParamValue plainValue) override
    {
        (void)id;
        return plainValue;
    }

    ParamValue getParamNormalized(ParamID id) override
    {
        (void)id;
        return 0.0;
    }

    tresult setParamNormalized(ParamID id, ParamValue value) override
    {
        (void)id;
        (void)value;
        return kResultFalse;
    }

    tresult setComponentHandler(IComponentHandler *handler) override
    {
        (void)handler;
        return kResultOk;
    }

    IPlugView *createView(FIDString name) override
    {
        if (!name || std::strcmp(name, "editor") == 0) {
            return new LlmrEditorView();
        }
        return nullptr;
    }

private:
    std::atomic<uint32> refCount_{1};
};

} // namespace Vst

class LlmrPluginFactory final : public IPluginFactory3 {
public:
    tresult queryInterface(const TUID iid, void **obj) override
    {
        if (!obj) {
            return kInvalidArgument;
        }
        if (iidEqual(iid, kFUnknownIID) || iidEqual(iid, kIPluginFactoryIID) ||
            iidEqual(iid, kIPluginFactory2IID) || iidEqual(iid, kIPluginFactory3IID)) {
            addRef();
            *obj = static_cast<IPluginFactory3 *>(this);
            return kResultOk;
        }
        *obj = nullptr;
        return kNoInterface;
    }

    uint32 addRef() override { return ++refCount_; }
    uint32 release() override
    {
        const auto count = --refCount_;
        return count;
    }

    tresult getFactoryInfo(PFactoryInfo *info) override
    {
        if (!info) {
            return kInvalidArgument;
        }
        std::memset(info, 0, sizeof(*info));
        copyString(info->vendor, "Tomas Laurenzo");
        copyString(info->url, "https://github.com/krahd/LLM-r");
        copyString(info->email, "tomas@laurenzo.net");
        info->flags = PFactoryInfo::kUnicode;
        return kResultOk;
    }

    int32 countClasses() override { return 2; }

    tresult getClassInfo(int32 index, PClassInfo *info) override
    {
        if ((index != 0 && index != 1) || !info) {
            return kInvalidArgument;
        }
        std::memset(info, 0, sizeof(*info));
        copyTuid(info->cid, index == 0 ? kLlmrProcessorCID : kLlmrControllerCID);
        info->cardinality = kManyInstances;
        copyString(info->category, index == 0 ? "Audio Module Class" : "Component Controller Class");
        copyString(info->name, index == 0 ? "LLM-r" : "LLM-r Controller");
        return kResultOk;
    }

    tresult getClassInfo2(int32 index, PClassInfo2 *info) override
    {
        if ((index != 0 && index != 1) || !info) {
            return kInvalidArgument;
        }
        std::memset(info, 0, sizeof(*info));
        copyTuid(info->cid, index == 0 ? kLlmrProcessorCID : kLlmrControllerCID);
        info->cardinality = kManyInstances;
        copyString(info->category, index == 0 ? "Audio Module Class" : "Component Controller Class");
        copyString(info->name, index == 0 ? "LLM-r" : "LLM-r Controller");
        info->classFlags = 0;
        copyString(info->subCategories, index == 0 ? "Instrument|Synth" : "");
        copyString(info->vendor, "Tomas Laurenzo");
        copyString(info->version, LLMR_VERSION);
        copyString(info->sdkVersion, "VST 3.8");
        return kResultOk;
    }

    tresult getClassInfoUnicode(int32 index, PClassInfoW *info) override
    {
        if ((index != 0 && index != 1) || !info) {
            return kInvalidArgument;
        }
        std::memset(info, 0, sizeof(*info));
        copyTuid(info->cid, index == 0 ? kLlmrProcessorCID : kLlmrControllerCID);
        info->cardinality = kManyInstances;
        copyString(info->category, index == 0 ? "Audio Module Class" : "Component Controller Class");
        copyString16(info->name, index == 0 ? "LLM-r" : "LLM-r Controller");
        info->classFlags = 0;
        copyString(info->subCategories, index == 0 ? "Instrument|Synth" : "");
        copyString16(info->vendor, "Tomas Laurenzo");
        copyString16(info->version, LLMR_VERSION);
        copyString16(info->sdkVersion, "VST 3.8");
        return kResultOk;
    }

    tresult setHostContext(FUnknown *context) override
    {
        (void)context;
        return kResultOk;
    }

    tresult createInstance(FIDString cid, FIDString iid, void **obj) override
    {
        if (!cid || !iid || !obj) {
            return kInvalidArgument;
        }
        *obj = nullptr;
        if (std::memcmp(cid, kLlmrProcessorCID, 16) == 0) {
            auto *component = new Vst::LlmrComponent();
            const auto result = component->queryInterface(iid, obj);
            component->release();
            return result;
        }
        if (std::memcmp(cid, kLlmrControllerCID, 16) == 0) {
            auto *controller = new Vst::LlmrController();
            const auto result = controller->queryInterface(iid, obj);
            controller->release();
            return result;
        }
        return kNoInterface;
    }

private:
    std::atomic<uint32> refCount_{1};
};

LlmrPluginFactory gFactory;

} // namespace Steinberg

#if defined(__APPLE__)
@implementation LlmrEditorTarget
- (instancetype)initWithOwner:(void *)owner action:(NSInteger)action
{
    self = [super init];
    if (self) {
        _owner = owner;
        _action = action;
    }
    return self;
}

- (void)performAction:(id)sender
{
    (void)sender;
    llmrEditorHandleAction(_owner, _action);
}
@end

@implementation LlmrCopyTextView
- (BOOL)performKeyEquivalent:(NSEvent *)event
{
    if (([event modifierFlags] & NSEventModifierFlagCommand) == NSEventModifierFlagCommand) {
        NSString *key = [[event charactersIgnoringModifiers] lowercaseString];
        if ([key isEqualToString:@"c"]) {
            [self copy:nil];
            return YES;
        }
        if ([key isEqualToString:@"a"]) {
            [self selectAll:nil];
            return YES;
        }
    }
    return [super performKeyEquivalent:event];
}
@end

@implementation LlmrPromptTextView
- (void)setLlmrPlaceholderLabel:(NSTextField *)label
{
    _llmrPlaceholderLabel = label;
    [self updateLlmrPlaceholder];
}
- (void)updateLlmrPlaceholder
{
    if (!_llmrPlaceholderLabel) return;
    NSString *raw = [self string] ?: @"";
    BOOL empty = [[raw stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]] length] == 0;
    [_llmrPlaceholderLabel setHidden:!empty];
}
- (void)setString:(NSString *)string
{
    [super setString:string ?: @""];
    [self updateLlmrPlaceholder];
}
- (void)didChangeText
{
    [super didChangeText];
    [self updateLlmrPlaceholder];
}
- (BOOL)performKeyEquivalent:(NSEvent *)event
{
    NSEventModifierFlags mods = [event modifierFlags] & NSEventModifierFlagDeviceIndependentFlagsMask;
    if (mods == NSEventModifierFlagCommand) {
        NSString *chars = [[event charactersIgnoringModifiers] lowercaseString] ?: @"";
        if ([chars isEqualToString:@"a"]) {
            [self selectAll:nil];
            return YES;
        }
        if ([chars isEqualToString:@"c"]) {
            [self copy:nil];
            return YES;
        }
        if ([chars isEqualToString:@"x"]) {
            [self cut:nil];
            return YES;
        }
        if ([chars isEqualToString:@"v"]) {
            [self paste:nil];
            return YES;
        }
    }
    return [super performKeyEquivalent:event];
}
- (void)keyDown:(NSEvent *)event
{
    NSString *chars = [event charactersIgnoringModifiers] ?: @"";
    unichar ch = [chars length] > 0 ? [chars characterAtIndex:0] : 0;
    if (ch == NSCarriageReturnCharacter || ch == NSEnterCharacter || ch == NSNewlineCharacter) {
        NSEventModifierFlags mods = [event modifierFlags] & NSEventModifierFlagDeviceIndependentFlagsMask;
        if ((mods & NSEventModifierFlagShift) || (mods & NSEventModifierFlagOption)) {
            [super keyDown:event];
            return;
        }
        [super insertNewline:nil];
        [self updateLlmrPlaceholder];
        return;
    }
    [super keyDown:event];
    [self updateLlmrPlaceholder];
}
@end

@implementation LlmrTextField
- (BOOL)performKeyEquivalent:(NSEvent *)event
{
    NSEventModifierFlags mods = [event modifierFlags] & NSEventModifierFlagDeviceIndependentFlagsMask;
    if (mods == NSEventModifierFlagCommand) {
        NSString *chars = [event charactersIgnoringModifiers] ?: @"";
        if ([chars isEqualToString:@"a"]) {
            [self selectText:self];
            NSText *editor = [[self window] fieldEditor:YES forObject:self];
            if (editor) {
                [editor selectAll:self];
            }
            return YES;
        }
    }
    return [super performKeyEquivalent:event];
}
@end

@implementation FullClickComboBox
- (BOOL)acceptsFirstMouse:(NSEvent *)event
{
    (void)event;
    return YES;
}
- (void)mouseDown:(NSEvent *)event
{
    [super mouseDown:event];
}
@end

static void llmrEditorHandleAction(void *owner, NSInteger action)
{
    if (!owner) {
        return;
    }
    auto *view = static_cast<Steinberg::Vst::LlmrEditorView *>(owner);
    view->handleEditorAction(action);
}
#endif

extern "C" {

__attribute__((visibility("default"))) bool bundleEntry(void *sharedLibraryHandle)
{
    (void)sharedLibraryHandle;
    return true;
}

__attribute__((visibility("default"))) bool bundleExit(void)
{
    return true;
}

__attribute__((visibility("default"))) Steinberg::IPluginFactory *GetPluginFactory(void)
{
    Steinberg::gFactory.addRef();
    return &Steinberg::gFactory;
}

}

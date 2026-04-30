#include <atomic>
#include <arpa/inet.h>
#include <cstdint>
#include <cstring>
#include <netdb.h>
#include <sys/socket.h>
#include <unistd.h>

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
};

static void llmrEditorHandleAction(void *owner, NSInteger action);

@interface LlmrEditorTarget : NSObject {
    void *_owner;
    NSInteger _action;
}
- (instancetype)initWithOwner:(void *)owner action:(NSInteger)action;
- (void)performAction:(id)sender;
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
        chatInputField_ = nullptr;
        chatStatusLabel_ = nullptr;
        chatSendButton_ = nullptr;
        chatExecuteButton_ = nullptr;
        chatDryRunButton_ = nullptr;
        chatSettingsButton_ = nullptr;
        settingsProviderCombo_ = nullptr;
        settingsModelField_ = nullptr;
        settingsEndpointField_ = nullptr;
        settingsApiKeyField_ = nullptr;
        settingsOscHostField_ = nullptr;
        settingsOscPortField_ = nullptr;
        settingsExtraPromptButton_ = nullptr;
        settingsDestructiveButton_ = nullptr;
        settingsDryRunButton_ = nullptr;
        ollamaStatusLabel_ = nullptr;
        ollamaModelField_ = nullptr;
        ollamaModelsCombo_ = nullptr;
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

    tresult canResize() override { return kResultTrue; }

    tresult checkSizeConstraint(ViewRect *rect) override
    {
        if (!rect) {
            return kInvalidArgument;
        }
        constexpr int kMinW = 600, kMinH = 420;
        if (rect->right - rect->left < kMinW) rect->right = rect->left + kMinW;
        if (rect->bottom - rect->top < kMinH) rect->bottom = rect->top + kMinH;
        return kResultOk;
    }

#if defined(__APPLE__)
    void handleEditorAction(NSInteger action)
    {
        switch (action) {
        case kLlmrEditorActionPlan:          planFromPrompt(); break;
        case kLlmrEditorActionExecute:       executeLastPlan(); break;
        case kLlmrEditorActionSaveSettings:  saveSettings(); hideSettings(); break;
        case kLlmrEditorActionOpenSettings:  showSettings(); break;
        case kLlmrEditorActionCloseSettings: saveSettings(); hideSettings(); break;
        case kLlmrEditorActionOllamaStart:   ollamaStart(); break;
        case kLlmrEditorActionOllamaStop:    ollamaStop(); break;
        case kLlmrEditorActionOllamaInstall: ollamaInstall(); break;
        case kLlmrEditorActionOllamaListModels:    ollamaListModels(); break;
        case kLlmrEditorActionOllamaDownloadModel: ollamaDownloadModel(); break;
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
        NSString *p = [provider lowercaseString];
        if ([p isEqualToString:@"ollama"]) {
            return @"http://127.0.0.1:11434/api/chat";
        }
        if ([p isEqualToString:@"anthropic"]) {
            return @"https://api.anthropic.com/v1/messages";
        }
        return @"https://api.openai.com/v1/chat/completions";
    }

    static NSString *controlString(NSTextField *field)
    {
        NSString *value = field ? [field stringValue] : @"";
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

    static NSString *stringValue(NSDictionary *dict, NSString *key, NSString *fallback)
    {
        id value = [dict objectForKey:key];
        if ([value isKindOfClass:[NSString class]] && [value length] > 0) {
            return value;
        }
        return fallback;
    }

    // ─── Color helpers ────────────────────────────────────────
    static NSColor *cBg()     { return [NSColor colorWithCalibratedRed:0.10 green:0.11 blue:0.12 alpha:1.0]; }
    static NSColor *cHdr()    { return [NSColor colorWithCalibratedRed:0.14 green:0.15 blue:0.17 alpha:1.0]; }
    static NSColor *cPanel()  { return [NSColor colorWithCalibratedRed:0.145 green:0.155 blue:0.17 alpha:1.0]; }
    static NSColor *cPri()    { return [NSColor colorWithCalibratedWhite:0.96 alpha:1.0]; }
    static NSColor *cSec()    { return [NSColor colorWithCalibratedWhite:0.60 alpha:1.0]; }
    static NSColor *cAccent() { return [NSColor colorWithCalibratedRed:0.43 green:0.76 blue:0.96 alpha:1.0]; }
    static NSColor *cChatBg() { return [NSColor colorWithCalibratedRed:0.07 green:0.075 blue:0.085 alpha:1.0]; }

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
    NSTextField *fieldIn(NSView *p, NSRect f, NSString *ph, BOOL secure)
    {
        NSTextField *v = secure ? [[NSSecureTextField alloc] initWithFrame:f]
                                : [[NSTextField alloc] initWithFrame:f];
        [v setPlaceholderString:ph]; [v setFont:[NSFont systemFontOfSize:12.0]];
        [p addSubview:v]; [v release]; return v;
    }
    NSComboBox *comboIn(NSView *p, NSRect f, NSArray *items)
    {
        NSComboBox *v = [[NSComboBox alloc] initWithFrame:f];
        [v addItemsWithObjectValues:items]; [v setCompletes:YES];
        [v setFont:[NSFont systemFontOfSize:12.0]];
        [p addSubview:v]; [v release]; return v;
    }
    NSButton *checkIn(NSView *p, NSRect f, NSString *title, bool on)
    {
        NSButton *v = [[NSButton alloc] initWithFrame:f];
        [v setButtonType:NSButtonTypeSwitch]; [v setTitle:title];
        [v setState:on ? NSControlStateValueOn : NSControlStateValueOff];
        [v setFont:[NSFont systemFontOfSize:12.0]];
        [p addSubview:v]; [v release]; return v;
    }
    NSButton *btnIn(NSView *p, NSRect f, NSString *title, NSInteger action)
    {
        NSButton *v = [[NSButton alloc] initWithFrame:f];
        [v setTitle:title]; [v setBezelStyle:NSBezelStyleRounded];
        [v setFont:[NSFont systemFontOfSize:12.0]];
        LlmrEditorTarget *t = [[LlmrEditorTarget alloc] initWithOwner:this action:action];
        [targets_ addObject:t]; [t release];
        [v setTarget:t]; [v setAction:@selector(performAction:)];
        [p addSubview:v]; [v release]; return v;
    }
    NSTextView *chatTextViewIn(NSView *p, NSRect scrollF)
    {
        NSScrollView *sc = [[NSScrollView alloc] initWithFrame:scrollF];
        [sc setHasVerticalScroller:YES]; [sc setBorderType:NSNoBorder];
        [sc setAutoresizingMask:NSViewWidthSizable | NSViewHeightSizable];
        NSTextView *tv = [[NSTextView alloc] initWithFrame:NSMakeRect(0,0,scrollF.size.width,scrollF.size.height)];
        [tv setEditable:NO]; [tv setRichText:YES];
        [tv setBackgroundColor:cChatBg()];
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

        // Settings overlay (hidden by default)
        settingsView_ = [[NSView alloc] initWithFrame:NSMakeRect(0, 0, width, height)];
        [settingsView_ setAutoresizingMask:NSViewWidthSizable | NSViewHeightSizable];
        [settingsView_ setWantsLayer:YES];
        settingsView_.layer.backgroundColor = cBg().CGColor;
        [settingsView_ setHidden:YES];
        [view_ addSubview:settingsView_]; [settingsView_ release];
        buildSettingsView(width, height);

        loadSettings();
    }

    void buildChatView(CGFloat width, CGFloat height)
    {
        static const CGFloat kHdr = 44.0, kBtm = 90.0, kPad = 12.0;

        // Header bar (top-anchored)
        NSView *hdr = [[NSView alloc] initWithFrame:NSMakeRect(0, height - kHdr, width, kHdr)];
        [hdr setWantsLayer:YES]; hdr.layer.backgroundColor = cHdr().CGColor;
        [hdr setAutoresizingMask:NSViewWidthSizable | NSViewMinYMargin];
        [chatView_ addSubview:hdr]; [hdr release];

        labelIn(hdr, @"LLM-r", NSMakeRect(kPad, 9, 130, 26),
                [NSFont boldSystemFontOfSize:18.0], cPri());
        labelIn(hdr, @"Ableton Live LLM assistant",
                NSMakeRect(kPad + 140, 11, width - kPad - 240, 22),
                [NSFont systemFontOfSize:12.0], cAccent());

        chatSettingsButton_ = btnIn(hdr, NSMakeRect(width - 104, 8, 92, 28),
                                    @"⚙  Settings", kLlmrEditorActionOpenSettings);
        [chatSettingsButton_ setAutoresizingMask:NSViewMinXMargin | NSViewMaxYMargin];

        // Chat history scroll (fills middle, auto-resizes)
        chatHistoryView_ = chatTextViewIn(chatView_,
            NSMakeRect(0, kBtm, width, height - kHdr - kBtm));

        // Restore previous chat history
        if ([chatHistory_ length] > 0) {
            [[chatHistoryView_ textStorage] setAttributedString:chatHistory_];
        }

        // Bottom container (bottom-anchored, fixed height)
        NSView *btm = [[NSView alloc] initWithFrame:NSMakeRect(0, 0, width, kBtm)];
        [btm setAutoresizingMask:NSViewWidthSizable | NSViewMaxYMargin];
        [chatView_ addSubview:btm]; [btm release];

        // Status label
        chatStatusLabel_ = labelIn(btm, @"Ready. Type a request and press Send.",
                                   NSMakeRect(kPad, 4, width - kPad*2, 18),
                                   [NSFont systemFontOfSize:11.0], cSec());
        [chatStatusLabel_ setAutoresizingMask:NSViewWidthSizable | NSViewMaxYMargin];

        // Execute button + dry-run (second row)
        chatExecuteButton_ = btnIn(btm, NSMakeRect(kPad, 26, 88, 26),
                                   @"▶ Execute", kLlmrEditorActionExecute);
        [chatExecuteButton_ setEnabled:NO];
        chatDryRunButton_ = checkIn(btm, NSMakeRect(kPad + 96, 28, 96, 22), @"Dry run", true);

        // Input field + Send button (top row of bottom)
        chatInputField_ = fieldIn(btm, NSMakeRect(kPad, 58, width - kPad*2 - 80, 28),
                                  @"Describe what you want Ableton to do…", NO);
        [chatInputField_ setAutoresizingMask:NSViewWidthSizable | NSViewMaxYMargin];

        chatSendButton_ = btnIn(btm, NSMakeRect(width - kPad - 72, 58, 72, 28),
                                @"Send", kLlmrEditorActionPlan);
        [chatSendButton_ setAutoresizingMask:NSViewMinXMargin | NSViewMaxYMargin];
    }

    // ─── buildSettingsView ────────────────────────────────────
    void buildSettingsView(CGFloat width, CGFloat height)
    {
        static const CGFloat kHdr = 44.0, kPad = 16.0, kLblW = 96.0, kGap = 8.0;
        static const CGFloat kContentH = 660.0;
        const CGFloat fldW = width - 2.0*kPad - kLblW - kGap;

        // Header
        NSView *hdr = [[NSView alloc] initWithFrame:NSMakeRect(0, height - kHdr, width, kHdr)];
        [hdr setWantsLayer:YES]; hdr.layer.backgroundColor = cHdr().CGColor;
        [hdr setAutoresizingMask:NSViewWidthSizable | NSViewMinYMargin];
        [settingsView_ addSubview:hdr]; [hdr release];

        labelIn(hdr, @"Settings", NSMakeRect(kPad, 9, 160, 26),
                [NSFont boldSystemFontOfSize:16.0], cPri());
        NSButton *backBtn = btnIn(hdr, NSMakeRect(width - 96, 8, 80, 28),
                                  @"✓ Done", kLlmrEditorActionCloseSettings);
        [backBtn setAutoresizingMask:NSViewMinXMargin | NSViewMaxYMargin];

        // Scroll view for content
        NSScrollView *sc = [[NSScrollView alloc] initWithFrame:NSMakeRect(0, 0, width, height - kHdr)];
        [sc setHasVerticalScroller:YES]; [sc setBorderType:NSNoBorder];
        [sc setAutoresizingMask:NSViewWidthSizable | NSViewHeightSizable];
        [sc setBackgroundColor:cBg()];
        [settingsView_ addSubview:sc]; [sc release];

        NSView *cv = [[NSView alloc] initWithFrame:NSMakeRect(0, 0, width, kContentH)];
        [cv setAutoresizingMask:NSViewWidthSizable];
        [cv setWantsLayer:YES]; cv.layer.backgroundColor = cBg().CGColor;
        [sc setDocumentView:cv]; [cv release];

        // ── Position helper: topY counts down from top of content ──
        CGFloat y = kContentH; // cursor: bottom of next item

#define SECT(title) \
        y -= 14.0; \
        labelIn(cv, title, NSMakeRect(kPad, y - 22.0, width - 2*kPad, 22.0), \
                [NSFont boldSystemFontOfSize:12.0], cAccent()); \
        y -= 22.0;

#define ROW_LBL(lbl, field_expr) \
        y -= 8.0; \
        labelIn(cv, lbl, NSMakeRect(kPad, y - 28.0, kLblW, 28.0), \
                [NSFont systemFontOfSize:12.0], cSec()); \
        field_expr; \
        y -= 28.0;

        // ── LLM Provider ──────────────────────────────────────
        SECT(@"LLM Provider")
        ROW_LBL(@"Provider:",
            settingsProviderCombo_ = comboIn(cv,
                NSMakeRect(kPad + kLblW + kGap, y - 28.0, fldW, 28.0),
                @[@"openai", @"anthropic", @"ollama", @"custom"]))
        ROW_LBL(@"Model:",
            settingsModelField_ = fieldIn(cv,
                NSMakeRect(kPad + kLblW + kGap, y - 28.0, fldW, 28.0),
                @"e.g. gpt-4.1-mini  claude-3-sonnet  llama3", NO))
        ROW_LBL(@"Endpoint:",
            settingsEndpointField_ = fieldIn(cv,
                NSMakeRect(kPad + kLblW + kGap, y - 28.0, fldW, 28.0),
                @"Leave blank for default", NO))
        ROW_LBL(@"API Key:",
            settingsApiKeyField_ = fieldIn(cv,
                NSMakeRect(kPad + kLblW + kGap, y - 28.0, fldW, 28.0),
                @"API key (cloud providers)", YES))

        y -= 8.0;
        settingsExtraPromptButton_ = checkIn(cv,
            NSMakeRect(kPad + kLblW + kGap, y - 24.0, 220, 24), @"LLM-r guidance prompt", true);
        y -= 24.0;
        settingsDestructiveButton_ = checkIn(cv,
            NSMakeRect(kPad + kLblW + kGap, y - 24.0, 200, 24), @"Allow destructive actions", false);
        y -= 24.0;

        // ── AbletonOSC ────────────────────────────────────────
        SECT(@"AbletonOSC")
        y -= 8.0;
        labelIn(cv, @"Host:", NSMakeRect(kPad, y - 28.0, kLblW, 28.0),
                [NSFont systemFontOfSize:12.0], cSec());
        settingsOscHostField_ = fieldIn(cv,
            NSMakeRect(kPad + kLblW + kGap, y - 28.0, 160, 28.0), @"127.0.0.1", NO);
        labelIn(cv, @"Port:", NSMakeRect(kPad + kLblW + kGap + 168, y - 28.0, 44, 28.0),
                [NSFont systemFontOfSize:12.0], cSec());
        settingsOscPortField_ = fieldIn(cv,
            NSMakeRect(kPad + kLblW + kGap + 218, y - 28.0, 80, 28.0), @"11000", NO);
        y -= 28.0;
        y -= 8.0;
        settingsDryRunButton_ = checkIn(cv,
            NSMakeRect(kPad + kLblW + kGap, y - 24.0, 120, 24), @"Dry run default", true);
        y -= 24.0;

        // ── Ollama ────────────────────────────────────────────
        SECT(@"Ollama")
        y -= 6.0;
        ollamaStatusLabel_ = labelIn(cv,
            @"Status unknown. Click List Models to check.",
            NSMakeRect(kPad, y - 20.0, width - 2*kPad, 20.0),
            [NSFont systemFontOfSize:11.0], cSec());
        [ollamaStatusLabel_ setAutoresizingMask:NSViewWidthSizable | NSViewMaxYMargin];
        y -= 20.0;

        y -= 8.0;
        btnIn(cv, NSMakeRect(kPad,          y - 28.0, 100, 28), @"Start Ollama",   kLlmrEditorActionOllamaStart);
        btnIn(cv, NSMakeRect(kPad + 108,    y - 28.0, 100, 28), @"Stop Ollama",    kLlmrEditorActionOllamaStop);
        btnIn(cv, NSMakeRect(kPad + 216,    y - 28.0, 110, 28), @"Install Ollama", kLlmrEditorActionOllamaInstall);
        y -= 28.0;

        y -= 12.0;
        labelIn(cv, @"Installed models:", NSMakeRect(kPad, y - 20.0, 140, 20.0),
                [NSFont systemFontOfSize:11.0], cSec());
        btnIn(cv, NSMakeRect(kPad + 148, y - 24.0, 130, 24),
              @"↺ Refresh List", kLlmrEditorActionOllamaListModels);
        y -= 20.0;

        y -= 4.0;
        ollamaModelsCombo_ = comboIn(cv,
            NSMakeRect(kPad, y - 28.0, fldW + kLblW + kGap, 28.0), @[]);
        [ollamaModelsCombo_ setAutoresizingMask:NSViewWidthSizable | NSViewMaxYMargin];
        y -= 28.0;

        y -= 12.0;
        labelIn(cv, @"Download model:", NSMakeRect(kPad, y - 20.0, 120, 20.0),
                [NSFont systemFontOfSize:11.0], cSec());
        y -= 20.0;

        y -= 4.0;
        ollamaModelField_ = fieldIn(cv,
            NSMakeRect(kPad, y - 28.0, fldW, 28.0),
            @"e.g. llama3  mistral  codellama", NO);
        [ollamaModelField_ setAutoresizingMask:NSViewWidthSizable | NSViewMaxYMargin];
        btnIn(cv, NSMakeRect(kPad + fldW + kGap, y - 28.0, 110, 28),
              @"⬇ Download", kLlmrEditorActionOllamaDownloadModel);
        y -= 28.0;

        (void)y;
#undef SECT
#undef ROW_LBL
    }

    void setStatus(NSString *message)
    {
        if (chatStatusLabel_) {
            [chatStatusLabel_ setStringValue:message ?: @""];
        }
    }

    void setBusy(bool busy)
    {
        if (chatSendButton_) [chatSendButton_ setEnabled:!busy];
        if (chatExecuteButton_) {
            [chatExecuteButton_ setEnabled:!busy && lastActions_ && [lastActions_ count] > 0];
        }
    }

    void showSettings()
    {
        if (!settingsView_) return;
        [settingsView_ setHidden:NO];
        [chatView_ setHidden:YES];
    }

    void hideSettings()
    {
        if (!settingsView_) return;
        [settingsView_ setHidden:YES];
        [chatView_ setHidden:NO];
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
        NSString *prov = [d stringForKey:@"llmr.vst3.provider"] ?: @"openai";
        NSString *mdl  = [d stringForKey:@"llmr.vst3.model"] ?: @"gpt-4.1-mini";
        NSString *ep   = [d stringForKey:@"llmr.vst3.endpoint"] ?: defaultEndpointForProvider(prov);
        NSString *key  = [d stringForKey:@"llmr.vst3.api_key"] ?: @"";
        NSString *host = [d stringForKey:@"llmr.vst3.osc_host"] ?: @"127.0.0.1";
        NSInteger port = [d integerForKey:@"llmr.vst3.osc_port"];
        if (port <= 0) port = 11000;
        [settingsProviderCombo_ setStringValue:prov];
        [settingsModelField_    setStringValue:mdl];
        [settingsEndpointField_ setStringValue:ep];
        [settingsApiKeyField_   setStringValue:key];
        [settingsOscHostField_  setStringValue:host];
        [settingsOscPortField_  setStringValue:[NSString stringWithFormat:@"%ld", (long)port]];
        bool extraOn = [d objectForKey:@"llmr.vst3.extra_prompt_enabled"]
                       ? [d boolForKey:@"llmr.vst3.extra_prompt_enabled"] : true;
        bool dryOn   = [d objectForKey:@"llmr.vst3.dry_run"]
                       ? [d boolForKey:@"llmr.vst3.dry_run"] : true;
        [settingsExtraPromptButton_ setState:extraOn ? NSControlStateValueOn : NSControlStateValueOff];
        [settingsDestructiveButton_ setState:[d boolForKey:@"llmr.vst3.allow_destructive"]
                                               ? NSControlStateValueOn : NSControlStateValueOff];
        [settingsDryRunButton_      setState:dryOn  ? NSControlStateValueOn : NSControlStateValueOff];
        if (chatDryRunButton_) {
            [chatDryRunButton_ setState:dryOn ? NSControlStateValueOn : NSControlStateValueOff];
        }
    }

    void saveSettings()
    {
        if (!settingsProviderCombo_) return;
        NSUserDefaults *d = [NSUserDefaults standardUserDefaults];
        [d setObject:controlString(settingsProviderCombo_) forKey:@"llmr.vst3.provider"];
        [d setObject:controlString(settingsModelField_)    forKey:@"llmr.vst3.model"];
        [d setObject:controlString(settingsEndpointField_) forKey:@"llmr.vst3.endpoint"];
        [d setObject:controlString(settingsApiKeyField_)   forKey:@"llmr.vst3.api_key"];
        [d setObject:controlString(settingsOscHostField_)  forKey:@"llmr.vst3.osc_host"];
        [d setInteger:[controlString(settingsOscPortField_) integerValue] forKey:@"llmr.vst3.osc_port"];
        [d setBool:buttonOn(settingsExtraPromptButton_) forKey:@"llmr.vst3.extra_prompt_enabled"];
        [d setBool:buttonOn(settingsDestructiveButton_) forKey:@"llmr.vst3.allow_destructive"];
        [d setBool:buttonOn(settingsDryRunButton_)      forKey:@"llmr.vst3.dry_run"];
        [d synchronize];
        // keep chat dry-run checkbox in sync
        if (chatDryRunButton_) {
            [chatDryRunButton_ setState:buttonOn(settingsDryRunButton_)
                                         ? NSControlStateValueOn : NSControlStateValueOff];
        }
    }

    // ─── Ollama operations ────────────────────────────────────
    void ollamaStart()
    {
        if (ollamaStatusLabel_) [ollamaStatusLabel_ setStringValue:@"Starting Ollama…"];
        dispatch_async(dispatch_get_global_queue(QOS_CLASS_UTILITY, 0), ^{
            @autoreleasepool {
                NSTask *task = [[NSTask alloc] init];
                [task setLaunchPath:@"/bin/sh"];
                [task setArguments:@[@"-l", @"-c", @"ollama serve >/dev/null 2>&1 &"]];
                @try { [task launch]; } @catch (NSException *) {}
                [task release];
                [NSThread sleepForTimeInterval:1.2];
                dispatch_async(dispatch_get_main_queue(), ^{
                    if (ollamaStatusLabel_)
                        [ollamaStatusLabel_ setStringValue:@"Ollama launched. Use List Models to verify."];
                });
            }
        });
    }

    void ollamaStop()
    {
        if (ollamaStatusLabel_) [ollamaStatusLabel_ setStringValue:@"Stopping Ollama…"];
        dispatch_async(dispatch_get_global_queue(QOS_CLASS_UTILITY, 0), ^{
            @autoreleasepool {
                NSTask *task = [[NSTask alloc] init];
                [task setLaunchPath:@"/bin/sh"];
                [task setArguments:@[@"-l", @"-c", @"pkill -x ollama || true"]];
                @try { [task launch]; [task waitUntilExit]; } @catch (NSException *) {}
                [task release];
                dispatch_async(dispatch_get_main_queue(), ^{
                    if (ollamaStatusLabel_) [ollamaStatusLabel_ setStringValue:@"Ollama stopped."];
                });
            }
        });
    }

    void ollamaInstall()
    {
        [[NSWorkspace sharedWorkspace] openURL:[NSURL URLWithString:@"https://ollama.ai"]];
        if (ollamaStatusLabel_)
            [ollamaStatusLabel_ setStringValue:@"Opening ollama.ai — install, then click Start Ollama."];
    }

    void ollamaListModels()
    {
        if (ollamaStatusLabel_) [ollamaStatusLabel_ setStringValue:@"Listing installed models…"];
        addRef();
        dispatch_async(dispatch_get_global_queue(QOS_CLASS_UTILITY, 0), ^{
            @autoreleasepool {
                NSTask *task = [[NSTask alloc] init];
                [task setLaunchPath:@"/bin/sh"];
                [task setArguments:@[@"-l", @"-c", @"ollama list 2>&1"]];
                NSPipe *pipe = [NSPipe pipe];
                [task setStandardOutput:pipe];
                [task setStandardError:pipe];
                NSString *output = nil;
                @try {
                    [task launch];
                    [task waitUntilExit];
                    NSData *data = [[pipe fileHandleForReading] readDataToEndOfFile];
                    output = [[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding];
                } @catch (NSException *) {
                    output = [@"ollama not found. Install from ollama.ai." retain];
                }
                [task release];
                if (!output) output = [@"" retain];

                NSMutableArray *models = [NSMutableArray array];
                for (NSString *line in [output componentsSeparatedByCharactersInSet:
                        [NSCharacterSet newlineCharacterSet]]) {
                    NSString *t = [line stringByTrimmingCharactersInSet:
                                   [NSCharacterSet whitespaceCharacterSet]];
                    if ([t length] == 0 || [t hasPrefix:@"NAME"]) continue;
                    NSArray *parts = [t componentsSeparatedByString:@" "];
                    if ([parts count] > 0 && [[parts objectAtIndex:0] length] > 0)
                        [models addObject:[parts objectAtIndex:0]];
                }
                NSString *status = [models count] > 0
                    ? [NSString stringWithFormat:@"%lu model(s) installed.", (unsigned long)[models count]]
                    : @"No models found or Ollama not running.";
                __block NSArray *rm = [models retain];
                __block NSString *rs = [status retain];
                [output release];
                dispatch_async(dispatch_get_main_queue(), ^{
                    if (ollamaModelsCombo_) {
                        [ollamaModelsCombo_ removeAllItems];
                        [ollamaModelsCombo_ addItemsWithObjectValues:rm];
                        if ([rm count] > 0) [ollamaModelsCombo_ selectItemAtIndex:0];
                    }
                    if (ollamaStatusLabel_) [ollamaStatusLabel_ setStringValue:rs];
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
            if (ollamaModelsCombo_) name = [[ollamaModelsCombo_ stringValue] copy];
        }
        if (!name || [name length] == 0) {
            if (ollamaStatusLabel_) [ollamaStatusLabel_ setStringValue:@"Enter a model name to download."];
            [name release]; return;
        }
        if (ollamaStatusLabel_)
            [ollamaStatusLabel_ setStringValue:[NSString stringWithFormat:@"Pulling %@…", name]];
        addRef();
        dispatch_async(dispatch_get_global_queue(QOS_CLASS_UTILITY, 0), ^{
            @autoreleasepool {
                NSTask *task = [[NSTask alloc] init];
                [task setLaunchPath:@"/bin/sh"];
                [task setArguments:@[@"-l", @"-c",
                    [NSString stringWithFormat:@"ollama pull %@", name]]];
                NSPipe *pipe = [NSPipe pipe];
                [task setStandardOutput:pipe]; [task setStandardError:pipe];
                NSString *out = nil;
                @try {
                    [task launch]; [task waitUntilExit];
                    NSData *d = [[pipe fileHandleForReading] readDataToEndOfFile];
                    out = [[NSString alloc] initWithData:d encoding:NSUTF8StringEncoding];
                } @catch (NSException *) {
                    out = [@"ollama not found. Install from ollama.ai." retain];
                }
                [task release];
                if (!out) out = [@"" retain];
                BOOL ok = [out containsString:@"success"] || [out containsString:@"up to date"];
                NSString *status = ok
                    ? [NSString stringWithFormat:@"%@ downloaded successfully.", name]
                    : [NSString stringWithFormat:@"Pull %@: %@", name,
                        [[out stringByTrimmingCharactersInSet:[NSCharacterSet newlineCharacterSet]]
                         substringToIndex:MIN((NSUInteger)80, [out length])]];
                __block NSString *rs = [status retain];
                [out release]; [name release];
                dispatch_async(dispatch_get_main_queue(), ^{
                    if (ollamaStatusLabel_) [ollamaStatusLabel_ setStringValue:rs];
                    [rs release];
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
               "- device_get_parameters/device_get_parameter/device_get_parameter_name/device_get_parameter_value_string/device_get_parameter_names/device_get_parameter_min_values/device_get_parameter_max_values {track_index,device_index,parameter_index?}; device_set_parameters {track_index,device_index,values}; device_set_parameter {track_index,device_index,parameter_index,value}; device_delete {track_index,device_index} destructive; utility_undo {}; utility_redo {}.\n";
    }

    NSString *systemPrompt()
    {
        NSMutableString *prompt = [NSMutableString stringWithString:
            @"You are the LLM-r planner running inside the LLM-r VST3 plug-in in Ableton Live. "
             "Return ONLY valid JSON matching this schema: "
             "{\"explanation\":\"short explanation\",\"confidence\":0.0,\"calls\":[{\"tool\":\"set_tempo\",\"args\":{\"bpm\":128}}]}. "
             "Plan only executable LLM-r tools. Do not claim to export/render, master, load plug-ins, analyze loudness, or inspect unavailable Live state unless a listed tool supports it. "
             "For composition requests, create tracks/clips and MIDI notes when enough musical detail is provided. For mixing requests, use exposed mixer/device parameter tools only.\n"];
        [prompt appendString:toolCatalogPrompt()];
        if (buttonOn(settingsExtraPromptButton_)) {
            [prompt appendString:@"Additional guidance: be explicit about limitations, keep plans conservative for destructive edits, and prefer dry-run review before executing.\n"];
        }
        return prompt;
    }

    void planFromPrompt()
    {
        NSString *rawInput = chatInputField_ ? [[chatInputField_ stringValue] copy] : [@"" copy];
        NSString *userPrompt = [[rawInput stringByTrimmingCharactersInSet:
            [NSCharacterSet whitespaceAndNewlineCharacterSet]] retain];
        [rawInput release];
        if ([userPrompt length] == 0) {
            setStatus(@"Enter a request first.");
            [userPrompt release];
            return;
        }
        // Clear input field and add to chat history
        if (chatInputField_) [chatInputField_ setStringValue:@""];
        appendToChat(@"user", userPrompt);
        setBusy(true);
        setStatus(@"Planning with LLM…");

        NSString *provider = [controlString(settingsProviderCombo_) copy];
        NSString *model = [controlString(settingsModelField_) copy];
        NSString *endpoint = [controlString(settingsEndpointField_) copy];
        NSString *apiKey = [controlString(settingsApiKeyField_) copy];
        NSString *system = [systemPrompt() copy];

        addRef();
        dispatch_async(dispatch_get_global_queue(QOS_CLASS_USER_INITIATED, 0), ^{
            @autoreleasepool {
                NSString *error = nil;
                NSString *content = callLLM(provider, model, endpoint, apiKey, system, userPrompt, &error);
                NSDictionary *plan = content ? parsePlan(content, &error) : nil;
                NSArray *actions = plan ? buildActions(plan[@"calls"], &error) : nil;
                NSString *display = nil;
                NSString *status = nil;
                if (actions && [actions count] > 0) {
                    display = [renderPlan(plan, content, actions) retain];
                    status = [@"Plan ready. Review it, then Execute or keep Dry run enabled." retain];
                } else {
                    display = [(error ?: @"No executable actions were returned.") retain];
                    status = [@"No executable actions." retain];
                }
                __block NSArray *retainedActions = [actions retain];
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
                        setStatus(status);
                        setBusy(false);
                    }
                    [retainedActions release];
                    [display release];
                    [status release];
                    this->release();
                });
            }
        });
    }

    void executeLastPlan()
    {
        if (!lastActions_ || [lastActions_ count] == 0) {
            setStatus(@"Create a plan first.");
            return;
        }
        bool dryRun = buttonOn(chatDryRunButton_);
        bool allowDestructive = buttonOn(settingsDestructiveButton_);
        NSString *host = controlString(settingsOscHostField_);
        int port = static_cast<int>([controlString(settingsOscPortField_) integerValue]);
        NSMutableString *report = [NSMutableString string];
        for (NSDictionary *act in lastActions_) {
            bool destructive = [[act objectForKey:@"destructive"] boolValue];
            if (destructive && !dryRun && !allowDestructive) {
                [report appendFormat:@"Skipped destructive: %@\n", [act objectForKey:@"tool"]];
                continue;
            }
            if (dryRun) {
                [report appendFormat:@"DRY RUN %@ %@\n",
                    [act objectForKey:@"address"], [[act objectForKey:@"args"] description]];
                continue;
            }
            NSString *err = nil;
            bool ok = sendOsc(host, port, [act objectForKey:@"address"],
                              [act objectForKey:@"args"], &err);
            [report appendFormat:@"%@ %@ %@\n", ok ? @"SENT" : @"ERROR",
                [act objectForKey:@"address"],
                ok ? [[act objectForKey:@"args"] description] : err];
        }
        NSString *statusMsg = dryRun ? @"Dry run complete." : @"Execution complete.";
        appendToChat(@"assistant", [NSString stringWithFormat:@"%@\n%@", statusMsg, report]);
        setStatus(statusMsg);
    }

    NSString *callLLM(NSString *provider, NSString *model, NSString *endpoint, NSString *apiKey,
                      NSString *system, NSString *userPrompt, NSString **error)
    {
        NSString *p = [[provider lowercaseString] length] ? [provider lowercaseString] : @"openai";
        NSString *urlString = [endpoint length] ? endpoint : defaultEndpointForProvider(p);
        NSURL *url = [NSURL URLWithString:urlString];
        if (!url) {
            if (error) {
                *error = @"Invalid LLM endpoint URL.";
            }
            return nil;
        }

        NSMutableURLRequest *request = [NSMutableURLRequest requestWithURL:url];
        [request setHTTPMethod:@"POST"];
        [request setValue:@"application/json" forHTTPHeaderField:@"Content-Type"];

        NSDictionary *body = nil;
        if ([p isEqualToString:@"ollama"]) {
            body = @{
                @"model": [model length] ? model : @"llama3",
                @"stream": @NO,
                @"messages": @[
                    @{@"role": @"system", @"content": system},
                    @{@"role": @"user", @"content": userPrompt},
                ],
            };
        } else if ([p isEqualToString:@"anthropic"]) {
            [request setValue:apiKey forHTTPHeaderField:@"x-api-key"];
            [request setValue:@"2023-06-01" forHTTPHeaderField:@"anthropic-version"];
            body = @{
                @"model": [model length] ? model : @"claude-3-5-sonnet-latest",
                @"max_tokens": @4096,
                @"system": system,
                @"messages": @[@{@"role": @"user", @"content": userPrompt}],
            };
        } else {
            if ([apiKey length] > 0) {
                [request setValue:[NSString stringWithFormat:@"Bearer %@", apiKey] forHTTPHeaderField:@"Authorization"];
            }
            body = @{
                @"model": [model length] ? model : @"gpt-4.1-mini",
                @"temperature": @0.2,
                @"messages": @[
                    @{@"role": @"system", @"content": system},
                    @{@"role": @"user", @"content": userPrompt},
                ],
            };
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
        dispatch_semaphore_wait(semaphore, DISPATCH_TIME_FOREVER);

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

    NSString *renderPlan(NSDictionary *plan, NSString *raw, NSArray *actions)
    {
        NSMutableDictionary *payload = [NSMutableDictionary dictionary];
        [payload setObject:[plan objectForKey:@"explanation"] ?: @"" forKey:@"explanation"];
        [payload setObject:[plan objectForKey:@"confidence"] ?: @0 forKey:@"confidence"];
        [payload setObject:actions forKey:@"actions"];
        [payload setObject:raw ?: @"" forKey:@"llm_raw"];
        NSData *data = [NSJSONSerialization dataWithJSONObject:payload options:NSJSONWritingPrettyPrinted error:nil];
        return [[[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding] autorelease] ?: [payload description];
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
            NSDictionary *action = actionForTool([call objectForKey:@"tool"], [call objectForKey:@"args"] ?: @{});
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
        if ([tool isEqualToString:@"device_set_parameter"]) return action(tool, @"/live/device/set/parameter/value", @"Set device parameter", @[@(intValue(args, @"track_index", 0)), @(intValue(args, @"device_index", 0)), @(intValue(args, @"parameter_index", 0)), @(numberValue(args, @"value", 0.0))], false);
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
            [payload addObject:@([value doubleValue])];
        }
        return action(tool, @"/live/device/set/parameters/value", @"Set device parameters", payload, false);
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
                [types appendString:@"s"];
            } else if (CFNumberIsFloatType((CFNumberRef)value)) {
                [types appendString:@"f"];
            } else {
                [types appendString:@"i"];
            }
        }
        appendPaddedString(packet, types);
        for (id value in args) {
            if ([value isKindOfClass:[NSString class]]) {
                appendPaddedString(packet, value);
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
    ViewRect rect_{0, 0, 820, 660};
    IPlugFrame *plugFrame_{nullptr};
#if defined(__APPLE__)
    NSView *view_{nullptr};
    NSMutableArray *targets_{nullptr};
    NSArray *lastActions_{nullptr};
    NSMutableAttributedString *chatHistory_{nullptr}; // survives removed/attached

    // Chat view
    NSView *chatView_{nullptr};
    NSTextView *chatHistoryView_{nullptr};
    NSTextField *chatInputField_{nullptr};
    NSTextField *chatStatusLabel_{nullptr};
    NSButton *chatSendButton_{nullptr};
    NSButton *chatExecuteButton_{nullptr};
    NSButton *chatDryRunButton_{nullptr};
    NSButton *chatSettingsButton_{nullptr};

    // Settings overlay
    NSView *settingsView_{nullptr};
    NSComboBox *settingsProviderCombo_{nullptr};
    NSTextField *settingsModelField_{nullptr};
    NSTextField *settingsEndpointField_{nullptr};
    NSTextField *settingsApiKeyField_{nullptr};
    NSTextField *settingsOscHostField_{nullptr};
    NSTextField *settingsOscPortField_{nullptr};
    NSButton *settingsExtraPromptButton_{nullptr};
    NSButton *settingsDestructiveButton_{nullptr};
    NSButton *settingsDryRunButton_{nullptr};

    // Ollama controls (inside settings)
    NSTextField *ollamaStatusLabel_{nullptr};
    NSTextField *ollamaModelField_{nullptr};
    NSComboBox *ollamaModelsCombo_{nullptr};
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
        copyString(info->version, "0.6.0");
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
        copyString16(info->version, "0.6.0");
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

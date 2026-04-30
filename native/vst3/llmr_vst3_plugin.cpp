#include <atomic>
#include <cstdint>
#include <cstring>

#if defined(__APPLE__)
#import <Cocoa/Cocoa.h>
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
    ~LlmrEditorView() { removed(); }

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

            auto addLabel = [this](NSString *text, NSRect labelFrame, NSFont *font, NSColor *color) {
                NSTextField *label = [[NSTextField alloc] initWithFrame:labelFrame];
                [label setStringValue:text];
                [label setBezeled:NO];
                [label setDrawsBackground:NO];
                [label setEditable:NO];
                [label setSelectable:NO];
                [label setLineBreakMode:NSLineBreakByWordWrapping];
                [label setFont:font];
                [label setTextColor:color];
                [view_ addSubview:label];
                [label release];
            };

            NSColor *primary = [NSColor colorWithCalibratedWhite:0.96 alpha:1.0];
            NSColor *secondary = [NSColor colorWithCalibratedWhite:0.72 alpha:1.0];
            NSColor *accent = [NSColor colorWithCalibratedRed:0.43 green:0.76 blue:0.96 alpha:1.0];

            addLabel(@"LLM-r", NSMakeRect(24.0, height - 62.0, width - 48.0, 34.0),
                     [NSFont boldSystemFontOfSize:28.0], primary);
            addLabel(@"Ableton Live LLM bridge",
                     NSMakeRect(26.0, height - 91.0, width - 52.0, 22.0),
                     [NSFont systemFontOfSize:14.0], accent);
            addLabel(@"Vendor: Tomas Laurenzo",
                     NSMakeRect(26.0, height - 128.0, width - 52.0, 22.0),
                     [NSFont systemFontOfSize:13.0], secondary);
            addLabel(@"Loaded as a VST3 instrument. Use the LLM-r desktop app or API for control.",
                     NSMakeRect(26.0, height - 166.0, width - 52.0, 44.0),
                     [NSFont systemFontOfSize:13.0], secondary);

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
        (void)frame;
        return kResultOk;
    }

    tresult canResize() override { return kResultFalse; }

    tresult checkSizeConstraint(ViewRect *rect) override
    {
        if (!rect) {
            return kInvalidArgument;
        }
        *rect = rect_;
        return kResultOk;
    }

private:
    static bool isNsViewType(FIDString type)
    {
        return type && std::strcmp(type, kPlatformTypeNSView) == 0;
    }

    std::atomic<uint32> refCount_{1};
    ViewRect rect_{0, 0, 420, 220};
#if defined(__APPLE__)
    NSView *view_{nullptr};
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
        copyString(info->version, "0.5.4");
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
        copyString16(info->version, "0.5.4");
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

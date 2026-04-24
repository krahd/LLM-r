// Example Max `js` helper for parsing simple OSC-like messages passed as
// JSON strings from a `udpreceive` -> `route` chain. This is a development
// helper; adapt for real Max message plumbing.

function parse(jsonStr) {
    try {
        var data = JSON.parse(jsonStr);
        // expected format: { address: "/live/device/set/parameter", args: [0,0,1,0.5] }
        if (data.address) {
            post("address:", data.address, "\n");
            if (data.args) post("args:", JSON.stringify(data.args), "\n");
            outlet(0, [data.address, JSON.stringify(data.args || [])]);
        }
    } catch (e) {
        post("parse error:", e, "\n");
    }
}

// Expose the function to Max
exports.parse = parse;

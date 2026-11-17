// Snapshot presents on a queue of their own (DM_PRESENT_QUEUE=1, nvn_mtl.m present_queue_on). Real Metal 4 queues and offscreen drawables; the link's callback is called by
// hand (no window, no game files). A present held on its queue (a gate there stands for a drawable the screen still holds) must not hold the game's queue, and the next copy
// into a ring slot must still come after the slot's last present, so each drawable shows the picture of its own present.
#include "../nvn/nvn_mtl.m"
@interface FakeLinkUpdate : NSObject
@property id<CAMetalDrawable> drawable;
@property CFTimeInterval targetPresentationTimestamp;
@property CFTimeInterval targetTimestamp;   // the late latch reads it (nvn_link_latch.h)
@end
@implementation FakeLinkUpdate
@end
static CAMetalLayer *g_test_layer;
void *front_metal_layer(void) { return (__bridge void *)g_test_layer; }
module_t *module_of(const void *p) { (void)p; return NULL; }
module_t *g_mod; int g_nmod;
void svc_thread_dump(void) {}
uint64_t now_ns(void) { return bp_now(); }
static int checks, failed;
#define CHECK(name, ok) do { int pass = !!(ok); checks++; failed += !pass; printf("%s: %s\n", name, pass ? "PASS" : "FAIL"); } while (0)
static tex_t source(unsigned serial, uint8_t v) {   // 8x8 grey of one value
    MTLTextureDescriptor *d = [MTLTextureDescriptor texture2DDescriptorWithPixelFormat:MTLPixelFormatRGBA8Unorm width:8 height:8 mipmapped:NO];
    d.storageMode = MTLStorageModeShared; d.usage = MTLTextureUsageShaderRead;
    id<MTLTexture> mt = [g_dev newTextureWithDescriptor:d]; uint8_t bytes[256];
    for (int i = 0; i < 64; i++) { bytes[4 * i] = bytes[4 * i + 1] = bytes[4 * i + 2] = v; bytes[4 * i + 3] = 255; }
    [mt replaceRegion:MTLRegionMake2D(0, 0, 8, 8) mipmapLevel:0 withBytes:bytes bytesPerRow:32];
    tex_t t = {.magic=MAGIC('T','E','X',0), .serial=serial};
    t.d.width = t.d.height = 8; t.d.depth = t.d.levels = t.d.samples = 1;
    t.d.target = NVN_TEXTURE_TARGET_2D; t.d.format = NVN_FORMAT_RGBA8;
    serial_put(t.serial, mt); res_add(mt); res_commit(); return t;
}
// Every present gets a drawable of its own layer (t_present_alloc.m: one layer handed a drawable's surface back while its present was still held)
static NSMutableArray *g_layers;
static id<CAMetalDrawable> drawable(void) {
    CAMetalLayer *l = [CAMetalLayer layer]; l.device = g_dev; l.pixelFormat = MTLPixelFormatBGRA8Unorm; l.framebufferOnly = NO; l.drawableSize = CGSizeMake(8, 8);
    [g_layers addObject:l]; return [l nextDrawable];
}
static NvMetalDisplayLinkDelegate *g_delegate;
static id<CAMetalDrawable> tick(void) {   // one display-link callback (it does not look at the link)
    id<CAMetalDrawable> dr = drawable();
    FakeLinkUpdate *u = [FakeLinkUpdate new]; u.drawable = dr; u.targetPresentationTimestamp = CACurrentMediaTime() + 0.016; u.targetTimestamp = CACurrentMediaTime() + 0.008;
    [g_delegate metalDisplayLink:(CAMetalDisplayLink *)(id)u needsUpdate:(CAMetalDisplayLinkUpdate *)u];
    return dr;
}
static int idle(void) {   // every present committed has run
    pthread_mutex_lock(&g_pq_mu); struct timespec ts; clock_gettime(CLOCK_REALTIME, &ts); ts.tv_sec += 5;
    while (g_pq_inflight && pthread_cond_timedwait(&g_pq_cv, &g_pq_mu, &ts) != ETIMEDOUT) {}
    int left = g_pq_inflight; pthread_mutex_unlock(&g_pq_mu); return left == 0;
}
static int bad_pixels(id<MTLTexture> t, uint8_t v) {
    id<MTLBuffer> out = [g_dev newBufferWithLength:256 options:MTLResourceStorageModeShared];
    if (!out) return 64;   // no buffer to read back into: every pixel counts as wrong
    id<MTLCommandBuffer> cb = [g_q commandBuffer]; id<MTLBlitCommandEncoder> b = [cb blitCommandEncoder];
    [b copyFromTexture:t sourceSlice:0 sourceLevel:0 sourceOrigin:MTLOriginMake(0, 0, 0) sourceSize:MTLSizeMake(8, 8, 1)
        toBuffer:out destinationOffset:0 destinationBytesPerRow:32 destinationBytesPerImage:256];
    [b endEncoding]; [cb commit]; [cb waitUntilCompleted];
    const uint8_t *p = out.contents; int bad = 0;
    for (int i = 0; i < 64; i++) bad += p[4 * i] != v || p[4 * i + 1] != v || p[4 * i + 2] != v;
    if (bad) printf("first pixel %u (want %u)\n", p[0], v);
    return bad;
}
int main(void) { @autoreleasepool {
    alarm(30); setvbuf(stdout, NULL, _IONBF, 0);
    setenv("DM_PRESENT_HZ", "0", 1); setenv("DM_PRESENT_SNAP", "1", 1); setenv("DM_PRESENT_QUEUE", "1", 1); setenv("DM_NVN_ENC_THREAD", "0", 1);
    mtl_init();
    g_test_layer = [CAMetalLayer layer]; g_layers = [NSMutableArray new];
    mtl_present_layer(8, 8);   // a layer of the drawables' shape, so the picture fills them
    g_dm_present_link = 1; g_link_started = 1; g_link_owns_layer = 1; g_delegate = [NvMetalDisplayLinkDelegate new];   // display-link mode without a link thread (t_present_alloc.m)
    CHECK("snapshots and the presents' queue are on", mtl_snap_on() && present_queue_on() && g_q4p != nil);
    char name[160];

    // Six presents, one per tick: every one a snapshot, committed on the presents' queue, each ring slot used three times
    static const uint8_t grey[6] = {20, 55, 90, 125, 160, 195};
    tex_t s[6]; id<CAMetalDrawable> d[6];
    for (int i = 0; i < 6; i++) { s[i] = source(92001 + (unsigned)i, grey[i]); mtl_snap_acquire_wait(); present_enqueue(&s[i], 1. / 60, NULL, 0, NULL); d[i] = tick(); }
    CHECK("the six presents ran", idle());
    CHECK("all six were committed on the presents' queue", g_q4p_v == 6);
    for (int i = 0; i < 6; i++) { snprintf(name, sizeof name, "present %d shows its own picture", i + 1); CHECK(name, bad_pixels(d[i].texture, grey[i]) == 0); }

    // A present held on its queue: the game's queue goes on, and a copy into the held present's slot waits for it
    id<MTLSharedEvent> gate = [g_dev newSharedEvent], probe = [g_dev newSharedEvent];
    [g_q4p waitForEvent:gate value:1];   // nothing committed to the presents' queue from here runs until the gate opens
    tex_t a = source(92011, 60), b = source(92012, 110), c = source(92013, 210);
    mtl_snap_acquire_wait(); present_enqueue(&a, 1. / 60, NULL, 0, NULL); id<CAMetalDrawable> da = tick();
    [g_q4 signalEvent:probe value:1];
    CHECK("the game's queue runs while a present waits on its own", [probe waitUntilSignaledValue:1 timeoutMS:2000]);
    pthread_mutex_lock(&g_pq_mu); int held = g_pq_inflight; pthread_mutex_unlock(&g_pq_mu);
    CHECK("that present has not run", held == 1);
    mtl_snap_acquire_wait(); present_enqueue(&b, 1. / 60, NULL, 0, NULL); id<CAMetalDrawable> db = tick();   // the other slot
    present_enqueue(&c, 1. / 60, NULL, 0, NULL);   // the first present's slot again: its copy is on the game's queue
    CHECK("the third present took a snapshot", atomic_load(&g_snap_next) == 9);
    [g_q4 signalEvent:probe value:2];
    CHECK("the copy into a slot waits for the slot's last present", ![probe waitUntilSignaledValue:2 timeoutMS:300]);
    gate.signaledValue = 1;
    CHECK("and runs once that present has", [probe waitUntilSignaledValue:2 timeoutMS:5000]);
    id<CAMetalDrawable> dc = tick();
    CHECK("the three presents ran", idle());
    CHECK("the held present shows its own picture, not the slot's next", bad_pixels(da.texture, 60) == 0);
    CHECK("the second shows its own picture", bad_pixels(db.texture, 110) == 0);
    CHECK("the third shows its own picture", bad_pixels(dc.texture, 210) == 0);
    printf("presents' queue: %d checks, %d failed\n", checks, failed); return failed != 0;
} }

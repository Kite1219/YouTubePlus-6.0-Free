#import <UIKit/UIKit.h>
#import <objc/runtime.h>
#import <objc/message.h>
#include <string.h>
#include <math.h>

// Uses the host's own edge-extension layout, not a safeAreaInsets override.
static const char *TPFields[] = {
    "_watchNextExtendsToScreenEdgeEnabled", "_engagementPanelExtendsToScreenEdgeEnabled"
};
static char TPStateKey;
static IMP TPOriginal;
@interface TPDuoWatchState : NSObject
@property BOOL feed;
@property BOOL panel;
@end
@implementation TPDuoWatchState
@end

static BOOL *TPFlag(id object, const char *name) {
    Ivar ivar = class_getInstanceVariable(object_getClass(object), name);
    if (!ivar || strcmp(ivar_getTypeEncoding(ivar), @encode(BOOL)) != 0) return NULL;
    return (BOOL *)((uint8_t *)(__bridge void *)object + ivar_getOffset(ivar));
}

BOOL TPDuoEligible(CGSize size, UIEdgeInsets safe, BOOL phone, BOOL fullscreen, BOOL rtl) {
    // Large landscape phone only. Ordinary phones, tablets, portrait and fullscreen are untouched.
    return phone && !fullscreen && !rtl && isfinite(size.width) && isfinite(size.height)
        && size.width >= 700 && size.height >= 500 && size.width > size.height
        && isfinite(safe.right) && safe.right >= 48 && safe.right <= 200
        && safe.right < size.width * 0.25;
}

static void TPPrepare(UIView *view) {
    BOOL *feed=TPFlag(view,TPFields[0]), *panel=TPFlag(view,TPFields[1]);
    if (!feed || !panel) return; // Unknown host version: leave it alone.
    SEL fullscreen=NSSelectorFromString(@"isFullscreen");
    BOOL hasFullscreen=[view respondsToSelector:fullscreen];
    BOOL full=hasFullscreen ? ((BOOL(*)(id,SEL))objc_msgSend)(view,fullscreen) : YES;
    UIWindow *window=view.window;
    BOOL phone=UIDevice.currentDevice.userInterfaceIdiom==UIUserInterfaceIdiomPhone;
    BOOL rtl=view.effectiveUserInterfaceLayoutDirection==UIUserInterfaceLayoutDirectionRightToLeft;
    BOOL eligible=window && TPDuoEligible(window.bounds.size,window.safeAreaInsets,phone,full,rtl)
        && !view.hidden && view.alpha>0.01
        && CGRectGetWidth(view.bounds)>=CGRectGetWidth(window.bounds)*0.80
        && CGRectGetHeight(view.bounds)>=CGRectGetHeight(window.bounds)*0.80;
    TPDuoWatchState *state=objc_getAssociatedObject(view,&TPStateKey);
    if (eligible) {
        if (!state) {
            state=[TPDuoWatchState new];state.feed=*feed;state.panel=*panel;
            objc_setAssociatedObject(view,&TPStateKey,state,OBJC_ASSOCIATION_RETAIN_NONATOMIC);
        }
        *feed=YES;*panel=YES;
    } else if (state) {
        *feed=state.feed;*panel=state.panel;
        objc_setAssociatedObject(view,&TPStateKey,nil,OBJC_ASSOCIATION_RETAIN_NONATOMIC);
    }
}

static void TPLayout(UIView *view,SEL selector) {
    TPPrepare(view);
    if (TPOriginal) ((void(*)(id,SEL))TPOriginal)(view,selector);
}

BOOL TPInstallDuoWatchLayout(void) {
    if (TPOriginal) return YES;
    Class host=NSClassFromString(@"YTWatchView");
    SEL layout=@selector(layoutSubviews);
    Method method=class_getInstanceMethod(host,layout);
    if (!host || !method || strcmp(method_getTypeEncoding(method),"v16@0:8")!=0) return NO;
    // Validate both exact BOOL fields before replacing any method.
    for (int i=0;i<2;i++) {
        Ivar ivar=class_getInstanceVariable(host,TPFields[i]);
        if (!ivar || strcmp(ivar_getTypeEncoding(ivar),@encode(BOOL))!=0) return NO;
    }
    TPOriginal=method_getImplementation(method);
    class_replaceMethod(host,layout,(IMP)TPLayout,method_getTypeEncoding(method));
    return YES;
}

#ifndef TP_FIXTURE
__attribute__((constructor)) static void TPInitialize(void) {
    dispatch_async(dispatch_get_main_queue(), ^{ TPInstallDuoWatchLayout(); });
}
#endif

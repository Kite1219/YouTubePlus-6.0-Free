#import <UIKit/UIKit.h>
#import <objc/runtime.h>
#import <objc/message.h>
#include <math.h>
#include <string.h>

static IMP TPRegularOriginal, TPInsetsOriginal;
static __thread UIView *TPLayoutOwner;
static char TPGeometryKey,TPStripKey;
@interface TPWatchGeometryState : NSObject
@property(nonatomic,weak) UIView *parent;
@property(nonatomic,strong) NSArray<NSLayoutConstraint *> *displaced;
@property(nonatomic,strong) NSArray<NSLayoutConstraint *> *installed;
@property(nonatomic) CGRect previousFrame;
@property(nonatomic) CGRect installedFrame;
@property(nonatomic) CGRect parentBounds;
@property(nonatomic) BOOL manual;
@end
@implementation TPWatchGeometryState
@end

static UIView *TPObjectView(id object,const char *name) {
    Ivar field=class_getInstanceVariable(object_getClass(object),name);
    if(!field || ivar_getTypeEncoding(field)[0]!='@')return nil;
    id value=object_getIvar(object,field);
    return [value isKindOfClass:UIView.class] ? value : nil;
}
static BOOL TPIsFullscreen(UIView *view) {
    SEL selector=NSSelectorFromString(@"isFullscreen");
    return ![view respondsToSelector:selector] || ((BOOL(*)(id,SEL))objc_msgSend)(view,selector);
}
BOOL TPWatchGeometryEligible(UIView *view) {
    UIWindow *window=view.window;
    if(!NSThread.isMainThread || !window || view.hidden || view.alpha<0.01 || TPIsFullscreen(view))return NO;
    if(window.windowScene && window.windowScene.activationState!=UISceneActivationStateForegroundActive)return NO;
    CGSize size=window.bounds.size;
    if(!isfinite(size.width) || !isfinite(size.height) || size.width<700 || size.height<500 || size.width<=size.height)return NO;
    // Neither the device idiom nor UIWindow's own safe insets describe the watch viewport reliably.
    for(UIView *v=view;v && v!=window;v=v.superview)
        if(!CGAffineTransformIsIdentity(v.transform))return NO;
    CGRect rect=[view convertRect:view.bounds toView:window];
    if(rect.size.width<size.width*0.75 || rect.size.height<size.height*0.75)return NO;
    UIEdgeInsets native=TPInsetsOriginal ? ((UIEdgeInsets(*)(id,SEL))TPInsetsOriginal)(view,NSSelectorFromString(@"watchNextSafeAreaInsets")) : view.safeAreaInsets;
    CGFloat reserve=MAX(native.right,MAX(view.safeAreaInsets.right,window.safeAreaInsets.right));
    CGFloat gap=CGRectGetMaxX(window.bounds)-CGRectGetMaxX(rect);
    TPWatchGeometryState *state=objc_getAssociatedObject(view,&TPGeometryKey);
    BOOL alreadyExtended=state && state.parent==view.superview;
    return (reserve>=32 && reserve<=200) || alreadyExtended
        || (gap>=32 && gap<=200 && fabs(CGRectGetMinX(rect)-CGRectGetMinX(window.bounds))<2);
}
static BOOL TPPlacement(NSLayoutConstraint *c,UIView *view,UIView *parent) {
    id own=nil,other=nil;NSLayoutAttribute attr=NSLayoutAttributeNotAnAttribute;
    if(c.firstItem==view){own=c.firstItem;other=c.secondItem;attr=c.firstAttribute;}
    else if(c.secondItem==view){own=c.secondItem;other=c.firstItem;attr=c.secondAttribute;}
    if(!own || c.relation!=NSLayoutRelationEqual)return NO;
    BOOL horizontal=attr==NSLayoutAttributeLeading || attr==NSLayoutAttributeTrailing || attr==NSLayoutAttributeLeft
        || attr==NSLayoutAttributeRight || attr==NSLayoutAttributeCenterX || attr==NSLayoutAttributeWidth;
    return horizontal && (other==parent || other==parent.safeAreaLayoutGuide || (!other && attr==NSLayoutAttributeWidth));
}
static void TPRestore(UIView *view) {
    TPWatchGeometryState *state=objc_getAssociatedObject(view,&TPGeometryKey);
    if(!state)return;
    [NSLayoutConstraint deactivateConstraints:state.installed ?: @[]];
    if(view.superview==state.parent){
        if(state.manual){
            if(CGRectEqualToRect(view.frame,state.installedFrame) && CGRectEqualToRect(view.superview.bounds,state.parentBounds))view.frame=state.previousFrame;
        } else [NSLayoutConstraint activateConstraints:state.displaced ?: @[]];
    }
    objc_setAssociatedObject(view,&TPGeometryKey,nil,OBJC_ASSOCIATION_RETAIN_NONATOMIC);
}
// Use the view's actual owning window. Keep the original left and vertical placement.
BOOL TPWatchExpandTrailing(UIView *view,UIWindow *window) {
    UIView *parent=view.superview;
    if(!parent || parent.window!=window || view.hidden || view.alpha<0.01 || !CGAffineTransformIsIdentity(view.transform))return NO;
    CGRect before=[view convertRect:view.bounds toView:window];
    CGFloat gap=CGRectGetMaxX(window.bounds)-CGRectGetMaxX(before);
    TPWatchGeometryState *state=objc_getAssociatedObject(view,&TPGeometryKey);
    if(state && state.parent!=parent){TPRestore(view);state=nil;}
    if(!isfinite(gap) || gap<32 || gap>200 || before.size.width<150 || before.size.height<window.bounds.size.height*0.60)return NO;
    CGRect target=[parent convertRect:window.bounds fromView:window];
    CGFloat right=CGRectGetMaxX(target);
    if(!isfinite(right) || right<=CGRectGetMinX(view.frame))return NO;
    if(!state){
        state=[TPWatchGeometryState new];state.parent=parent;state.previousFrame=view.frame;state.parentBounds=parent.bounds;
        state.manual=view.translatesAutoresizingMaskIntoConstraints;
        if(!state.manual){
            NSMutableArray *displaced=[NSMutableArray new];
            for(NSLayoutConstraint *c in [parent.constraints arrayByAddingObjectsFromArray:view.constraints])
                if(c.active && TPPlacement(c,view,parent))[displaced addObject:c];
            if(!displaced.count)return NO; // Unknown constraint ownership: do not write frames.
            state.displaced=displaced;[NSLayoutConstraint deactivateConstraints:displaced];
            NSLayoutConstraint *leading=[view.leadingAnchor constraintEqualToAnchor:parent.leadingAnchor constant:CGRectGetMinX(view.frame)-CGRectGetMinX(parent.bounds)];
            NSLayoutConstraint *trailing=[view.trailingAnchor constraintEqualToAnchor:parent.trailingAnchor constant:right-CGRectGetMaxX(parent.bounds)];
            leading.identifier=@"YouTubePlus.watch.leading";trailing.identifier=@"YouTubePlus.watch.trailing";
            state.installed=@[leading,trailing];[NSLayoutConstraint activateConstraints:state.installed];
        }
        objc_setAssociatedObject(view,&TPGeometryKey,state,OBJC_ASSOCIATION_RETAIN_NONATOMIC);
    }
    if(state.manual){
        CGRect frame=view.frame;frame.size.width=right-CGRectGetMinX(frame);
        if(fabs(frame.size.width-view.frame.size.width)>0.5)view.frame=frame;
        state.installedFrame=frame;
    } else {
        NSLayoutConstraint *trailing=state.installed.lastObject;
        CGFloat constant=right-CGRectGetMaxX(parent.bounds);
        if(fabs(trailing.constant-constant)>0.5)trailing.constant=constant;
    }
    return YES;
}
static UIEdgeInsets TPWatchInsets(UIView *view,SEL selector) {
    UIEdgeInsets insets=TPInsetsOriginal ? ((UIEdgeInsets(*)(id,SEL))TPInsetsOriginal)(view,selector) : UIEdgeInsetsZero;
    // Only the app's private column-frame calculation is changed. UIKit safe areas are untouched.
    if(TPLayoutOwner==view && TPWatchGeometryEligible(view) && insets.right>=32 && insets.right<=200)insets.right=0;
    return insets;
}
static void TPClearAppStrip(UIView *watch,BOOL eligible) {
    UIWindow *window=watch.window;
    for(UIView *parent=watch.superview;parent && parent!=window;parent=parent.superview){
        if(![parent isKindOfClass:NSClassFromString(@"YTWatchLayerView")])continue;
        UIView *strip=TPObjectView(parent,"_statusBarView");
        if(!strip)return;
        NSDictionary *saved=objc_getAssociatedObject(strip,&TPStripKey);
        CGRect rect=[strip convertRect:strip.bounds toView:window];
        BOOL matches=eligible && !strip.subviews.count && rect.size.width>=32 && rect.size.width<=200 && rect.size.height>window.bounds.size.height*0.8
            && fabs(CGRectGetMaxX(rect)-CGRectGetMaxX(window.bounds))<2;
        if(matches){
            if(!saved)objc_setAssociatedObject(strip,&TPStripKey,@{@"color":strip.backgroundColor ?: NSNull.null,@"opaque":@(strip.opaque)},OBJC_ASSOCIATION_RETAIN_NONATOMIC);
            strip.backgroundColor=UIColor.clearColor;strip.opaque=NO;
        } else if(saved){strip.backgroundColor=saved[@"color"]==NSNull.null?nil:saved[@"color"];strip.opaque=[saved[@"opaque"]boolValue];objc_setAssociatedObject(strip,&TPStripKey,nil,OBJC_ASSOCIATION_RETAIN_NONATOMIC);}
    }
}
static NSDictionary *TPGeometrySnapshot(UIView *view) {
    UIWindow *window=view.window;if(!window)return @{};
    NSMutableArray *ancestors=[NSMutableArray new],*controllers=[NSMutableArray new],*constraints=[NSMutableArray new];
    for(UIView *v=view;v && ancestors.count<16;v=v.superview){
        [ancestors addObject:@{@"class":NSStringFromClass(v.class),@"bounds":NSStringFromCGRect(v.bounds),@"frame":NSStringFromCGRect(v.frame),@"windowRect":NSStringFromCGRect([v convertRect:v.bounds toView:window]),@"safeInsets":NSStringFromUIEdgeInsets(v.safeAreaInsets),@"transform":NSStringFromCGAffineTransform(v.transform),@"clips":@(v.clipsToBounds),@"layerMasks":@(v.layer.masksToBounds),@"hasMask":@(v.layer.mask!=nil),@"cornerRadius":@(v.layer.cornerRadius)}];
        if(v==window)break;
    }
    for(UIResponder *r=view;r && controllers.count<24;r=r.nextResponder)
        if([r isKindOfClass:UIViewController.class])[controllers addObject:NSStringFromClass(r.class)];
    for(NSLayoutConstraint *c in [view.constraints arrayByAddingObjectsFromArray:view.superview.constraints ?: @[]]){
        if(!c.active || constraints.count>=64)continue;
        [constraints addObject:@{@"first":c.firstItem?NSStringFromClass([c.firstItem class]):@"nil",@"second":c.secondItem?NSStringFromClass([c.secondItem class]):@"nil",@"firstAttribute":@(c.firstAttribute),@"secondAttribute":@(c.secondAttribute),@"constant":@(c.constant),@"priority":@(c.priority)}];
    }
    UIView *feed=TPObjectView(view,"_watchNextWrapperView"),*panel=TPObjectView(view,"_engagementPanelView");
    return @{@"windowBounds":NSStringFromCGRect(window.bounds),@"windowInsets":NSStringFromUIEdgeInsets(window.safeAreaInsets),@"screenBounds":NSStringFromCGRect(window.screen.bounds),@"rootController":window.rootViewController?NSStringFromClass(window.rootViewController.class):@"nil",@"presentedController":window.rootViewController.presentedViewController?NSStringFromClass(window.rootViewController.presentedViewController.class):@"nil",@"horizontalSizeClass":@(view.traitCollection.horizontalSizeClass),@"verticalSizeClass":@(view.traitCollection.verticalSizeClass),@"ancestors":ancestors,@"controllers":controllers,@"constraints":constraints,@"feedWindowRect":feed?NSStringFromCGRect([feed convertRect:feed.bounds toView:window]):@"nil",@"panelWindowRect":panel?NSStringFromCGRect([panel convertRect:panel.bounds toView:window]):@"nil"};
}
static void TPRegularLayout(UIView *view,SEL selector) {
    if(TPLayoutOwner==view){((void(*)(id,SEL))TPRegularOriginal)(view,selector);return;}
    BOOL eligible=TPWatchGeometryEligible(view);
    static NSString *lastSignature;
    NSString *signature=view.window?[NSString stringWithFormat:@"%@/%@/%@/%d",NSStringFromCGRect(view.window.bounds),NSStringFromCGRect(view.frame),NSStringFromUIEdgeInsets(view.safeAreaInsets),eligible]:@"detached";
    BOOL record=view.window && ![signature isEqualToString:lastSignature];
    NSDictionary *before=record?TPGeometrySnapshot(view):nil;
    UIView *feed=TPObjectView(view,"_watchNextWrapperView"),*panel=TPObjectView(view,"_engagementPanelView");
    NSMutableArray<UIView *> *layers=[NSMutableArray new];
    for(UIView *v=view.superview;v && v!=view.window;v=v.superview)
        if([v isKindOfClass:NSClassFromString(@"YTWatchLayerView")])[layers insertObject:v atIndex:0];
    if(!eligible){TPRestore(feed);TPRestore(panel);TPRestore(view);for(UIView *layer in layers)TPRestore(layer);}
    if(eligible){
        for(UIView *layer in layers)TPWatchExpandTrailing(layer,view.window);
        TPWatchExpandTrailing(view,view.window);
    }
    UIView *previous=TPLayoutOwner;TPLayoutOwner=eligible?view:nil;
    @try{((void(*)(id,SEL))TPRegularOriginal)(view,selector);}
    @finally{TPLayoutOwner=previous;}
    if(eligible){TPWatchExpandTrailing(feed,view.window);TPWatchExpandTrailing(panel,view.window);}
    TPClearAppStrip(view,eligible);
    if(record){lastSignature=signature;[NSUserDefaults.standardUserDefaults setObject:@{@"build":@"test.6",@"eligible":@(eligible),@"before":before,@"after":TPGeometrySnapshot(view)} forKey:@"YouTubePlusWatchGeometry"];} // Geometry only; no account, URL or text data.
}
BOOL TPInstallDuoWatchLayout(void) {
    if(TPRegularOriginal)return YES;
    Class host=NSClassFromString(@"YTWatchView");
    Method regular=class_getInstanceMethod(host,NSSelectorFromString(@"layoutSubviews_regular"));
    Method insets=class_getInstanceMethod(host,NSSelectorFromString(@"watchNextSafeAreaInsets"));
    if(!host || !regular || !insets || strcmp(method_getTypeEncoding(regular),"v16@0:8")!=0)return NO;
    char *returnType=method_copyReturnType(insets);
    BOOL valid=strcmp(returnType,@encode(UIEdgeInsets))==0;free(returnType);if(!valid)return NO;
    TPRegularOriginal=method_getImplementation(regular);TPInsetsOriginal=method_getImplementation(insets);
    class_replaceMethod(host,NSSelectorFromString(@"watchNextSafeAreaInsets"),(IMP)TPWatchInsets,method_getTypeEncoding(insets));
    class_replaceMethod(host,NSSelectorFromString(@"layoutSubviews_regular"),(IMP)TPRegularLayout,method_getTypeEncoding(regular));
    return YES;
}
#ifndef TP_FIXTURE
__attribute__((constructor)) static void TPInitialize(void) {dispatch_async(dispatch_get_main_queue(),^{ TPInstallDuoWatchLayout(); });}
#endif

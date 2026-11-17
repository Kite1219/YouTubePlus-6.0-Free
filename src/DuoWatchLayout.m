#import <UIKit/UIKit.h>
#import <objc/runtime.h>
#import <objc/message.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>

// test.8 preserves test.7's edge-to-edge content while reserving native header width for comments.
// Native column sizing is reused with the full available width; system indicators stay genuine.
static IMP TPFeedOriginal,TPPanelRectOriginal,TPChatOriginal;
static IMP TPFeedMovedOriginal,TPChatMovedOriginal;
static IMP TPExpandedSizeOriginal,TPAppInsetsOriginal;
static IMP TPPanelLayoutOriginal,TPPanelAddedOriginal,TPPanelRemovedOriginal;
static __thread __unsafe_unretained UIView *TPSizeOwner;
static char TPScrollPolicyKey,TPCommentsOpenKey;

static id TPObjectValue(id object,const char *name) {
    if(!object)return nil;
    Ivar field=class_getInstanceVariable(object_getClass(object),name);
    if(!field || ivar_getTypeEncoding(field)[0]!='@')return nil;
    return object_getIvar(object,field);
}
static UIView *TPObjectView(id object,const char *name) {
    id value=TPObjectValue(object,name);
    return [value isKindOfClass:UIView.class]?value:nil;
}
static BOOL TPFinite(CGRect r) {
    return isfinite(r.origin.x)&&isfinite(r.origin.y)&&isfinite(r.size.width)&&isfinite(r.size.height);
}
static UIView *TPWatchAncestor(UIView *view) {
    Class c=NSClassFromString(@"YTWatchView");
    for(UIView *v=view;v;v=v.superview)if(c&&[v isKindOfClass:c])return v;
    return nil;
}
BOOL TPWatchGeometryEligible(UIView *watch) {
    UIWindow *window=watch.window;
    if(!NSThread.isMainThread||!window||!watch)return NO;
    if(window.windowScene&&window.windowScene.activationState!=UISceneActivationStateForegroundActive)return NO;
    SEL full=NSSelectorFromString(@"isFullscreen");
    if(![watch respondsToSelector:full]||((BOOL(*)(id,SEL))objc_msgSend)(watch,full))return NO;
    CGRect wb=window.bounds;
    if(!TPFinite(wb)||wb.size.width<700||wb.size.height<500||wb.size.width<=wb.size.height)return NO;
    CGFloat right=window.safeAreaInsets.right;
    if(!isfinite(right)||right<32||right>200)return NO;
    for(UIView *v=watch;v&&v!=window;v=v.superview)
        if(v.hidden||v.alpha<0.01||!CGAffineTransformIsIdentity(v.transform))return NO;
    CGRect wr=[watch convertRect:watch.bounds toView:window];
    return TPFinite(wr)&&wr.size.width>=wb.size.width*.90&&wr.size.height>=wb.size.height*.75
        &&fabs(CGRectGetMinX(wr)-CGRectGetMinX(wb))<2
        &&fabs(CGRectGetMaxX(wr)-CGRectGetMaxX(wb))<2;
}
// expandedPlayerSize originally subtracts the 84-point reserve before applying the
// native split and minimum feed width. Suppress that duplicate subtraction only
// during this size query, so the original algorithm enlarges the video and reflows
// everything below it. UIKit safe areas and all other inset consumers stay native.
static UIEdgeInsets TPAppInsets(UIView *watch,SEL selector) {
    UIEdgeInsets insets=((UIEdgeInsets(*)(id,SEL))TPAppInsetsOriginal)(watch,selector);
    if(TPSizeOwner==watch&&insets.right>=32&&insets.right<=200)insets.right=0;
    return insets;
}
// Match the app's panel identifier rather than visible/localized title text.
// Only inspect the top navigation panel, so a covered comments panel is not counted.
static BOOL TPCommentsPanelOpen(UIView *watch) {
    UIView *container=TPObjectView(watch,"_engagementPanelView");
    SEL top=NSSelectorFromString(@"topEngagementPanelNavigationView");
    Method getter=class_getInstanceMethod(object_getClass(container),top);
    if(!getter||strcmp(method_getTypeEncoding(getter),"@16@0:8"))return NO;
    id navigation=((id(*)(id,SEL))objc_msgSend)(container,top);
    if(![navigation isKindOfClass:UIView.class]||[navigation isHidden])return NO;
    Class panelClass=NSClassFromString(@"YTEngagementPanelView");
    NSMutableArray<UIView *> *queue=[NSMutableArray arrayWithObject:navigation];
    NSUInteger visited=0;
    while(queue.count&&visited++<80){
        UIView *v=queue.firstObject;[queue removeObjectAtIndex:0];
        if(v.hidden)continue;
        if([v isKindOfClass:panelClass]){
            id identifier=TPObjectValue(v,"_panelIdentifier");
            SEL equal=NSSelectorFromString(@"equalToIdentifierString:");
            Method m=class_getInstanceMethod(object_getClass(identifier),equal);
            if(m&&!strcmp(method_getTypeEncoding(m),"B24@0:8@16"))
                return ((BOOL(*)(id,SEL,id))objc_msgSend)(identifier,equal,@"engagement-panel-comments-section");
            return NO;
        }
        // UIKit navigation wrappers only; do not walk collection cells or their content.
        if(![v isKindOfClass:UIScrollView.class])[queue addObjectsFromArray:v.subviews];
    }
    return NO;
}
static CGSize TPExpandedSize(UIView *watch,SEL selector) {
    CGSize native=((CGSize(*)(id,SEL))TPExpandedSizeOriginal)(watch,selector);
    if(!TPWatchGeometryEligible(watch))return native;
    // The native minimum feed width is also the width needed by the comments title,
    // information/close controls and filter row, after reserving the system indicators.
    // Keep that native minimum when comments are open instead of squeezing the header.
    if(TPCommentsPanelOpen(watch))return native;
    UIView *previous=TPSizeOwner;
    TPSizeOwner=watch;CGSize enlarged=native;
    @try{enlarged=((CGSize(*)(id,SEL))TPExpandedSizeOriginal)(watch,selector);}
    @finally{TPSizeOwner=previous;}
    // Flexible-player mode can return a cached, fixed height. Grow that container
    // proportionally too; leave the player's rendering gravity/content mode alone.
    if(native.width>0&&native.height>0&&isfinite(enlarged.width)&&enlarged.width>native.width+.5
       &&fabs(enlarged.height-native.height)<.5){
        CGFloat scale=watch.window.screen.scale ?: 1;
        enlarged.height=round(native.height*enlarged.width/native.width*scale)/scale;
    }
    return enlarged;
}
// A real trailing watch column, not Home, a player or a fullscreen panel.
static BOOL TPColumnEligible(UIView *column) {
    UIView *watch=TPWatchAncestor(column);if(!TPWatchGeometryEligible(watch))return NO;
    UIWindow *window=column.window;
    for(UIView *v=column;v&&v!=watch;v=v.superview)
        if(v.hidden||v.alpha<0.01||!CGAffineTransformIsIdentity(v.transform))return NO;
    CGRect r=[column convertRect:column.bounds toView:window],w=window.bounds;
    return TPFinite(r)&&r.size.width>=200&&r.size.width<=w.size.width*.60
        &&r.size.height>=w.size.height*.40
        &&CGRectGetMinX(r)>=CGRectGetMinX(w)+w.size.width*.35
        &&fabs(CGRectGetMaxX(r)-CGRectGetMaxX(w))<2;
}
// Retain vertical safe-area handling without adding a horizontal inset to a vertical feed.
// Never change the caller's contentInset or safeAreaInsets.
static void TPScrollPolicy(UIView *view,BOOL enabled) {
    if(![view isKindOfClass:UIScrollView.class])return;
    UIScrollView *scroll=(id)view;NSNumber *saved=objc_getAssociatedObject(scroll,&TPScrollPolicyKey);
    if(enabled){
        if(scroll.contentInsetAdjustmentBehavior==UIScrollViewContentInsetAdjustmentNever)return;
        if(!saved){saved=@(scroll.contentInsetAdjustmentBehavior);objc_setAssociatedObject(scroll,&TPScrollPolicyKey,saved,OBJC_ASSOCIATION_RETAIN_NONATOMIC);}
        scroll.contentInsetAdjustmentBehavior=UIScrollViewContentInsetAdjustmentScrollableAxes;
    }else if(saved){
        if(scroll.contentInsetAdjustmentBehavior==UIScrollViewContentInsetAdjustmentScrollableAxes)scroll.contentInsetAdjustmentBehavior=saved.integerValue;
        objc_setAssociatedObject(scroll,&TPScrollPolicyKey,nil,OBJC_ASSOCIATION_RETAIN_NONATOMIC);
    }
}
static CGRect TPExtendInnerRect(UIView *column,CGRect nativeRect) {
    if(!TPColumnEligible(column)||!TPFinite(nativeRect)||nativeRect.size.height<100)return nativeRect;
    CGFloat gap=CGRectGetMaxX(column.bounds)-CGRectGetMaxX(nativeRect);
    CGFloat reserve=column.window.safeAreaInsets.right;
    // Exactly the duplicate inset measured on the device, not intentional narrow content.
    if(gap<32||gap>200||fabs(gap-reserve)>2||nativeRect.size.width<150)return nativeRect;
    nativeRect.size.width+=gap;return nativeRect;
}
static void TPFeedLayout(UIView *feed,SEL selector) {
    ((void(*)(id,SEL))TPFeedOriginal)(feed,selector);
    UIView *results=TPObjectView(feed,"_watchNextResultsView");
    BOOL eligible=TPColumnEligible(feed)&&results.superview==feed&&results.translatesAutoresizingMaskIntoConstraints;
    TPScrollPolicy(results,eligible);
    if(!eligible)return;
    CGRect native=results.frame,target=TPExtendInnerRect(feed,native);
    if(!CGRectEqualToRect(native,target)){
        results.frame=target;
        if([results isKindOfClass:UICollectionView.class])[((UICollectionView *)results).collectionViewLayout invalidateLayout];
        [results setNeedsLayout];
    }
}
// The native method passes this rectangle to _contentContainerView and sizes _contentView
// from its bounds. Header/footer buttons keep their original safe placement.
static CGRect TPPanelContentRect(UIView *panel,SEL selector,CGRect header,CGRect footer,CGFloat safeX) {
    CGRect native=((CGRect(*)(id,SEL,CGRect,CGRect,CGFloat))TPPanelRectOriginal)(panel,selector,header,footer,safeX);
    UIView *container=TPObjectView(panel,"_contentContainerView");
    if(!container.translatesAutoresizingMaskIntoConstraints)return native;
    return TPExtendInnerRect(panel,native);
}
static void TPChatLayout(UIView *chat,SEL selector) {
    UIView *collection=TPObjectView(chat,"_collectionView");
    TPScrollPolicy(collection,TPColumnEligible(chat));
    ((void(*)(id,SEL))TPChatOriginal)(chat,selector);
    TPScrollPolicy(collection,TPColumnEligible(chat));
}
static void TPFeedMoved(UIView *feed,SEL selector) {
    ((void(*)(id,SEL))TPFeedMovedOriginal)(feed,selector);
    if(!TPColumnEligible(feed))TPScrollPolicy(TPObjectView(feed,"_watchNextResultsView"),NO);
}
static void TPChatMoved(UIView *chat,SEL selector) {
    ((void(*)(id,SEL))TPChatMovedOriginal)(chat,selector);
    if(!TPColumnEligible(chat))TPScrollPolicy(TPObjectView(chat,"_collectionView"),NO);
}
static void TPCommentsWidthChanged(UIView *container,BOOL hierarchyChanged) {
    UIView *watch=TPWatchAncestor(container);
    if(!TPWatchGeometryEligible(watch)||TPObjectView(watch,"_engagementPanelView")!=container)return;
    BOOL open=TPCommentsPanelOpen(watch);
    NSNumber *previous=objc_getAssociatedObject(container,&TPCommentsOpenKey);
    objc_setAssociatedObject(container,&TPCommentsOpenKey,@(open),OBJC_ASSOCIATION_RETAIN_NONATOMIC);
    if((previous&&previous.boolValue!=open)||(!previous&&open)||hierarchyChanged)
        [watch setNeedsLayout];
}
static void TPPanelLayout(UIView *container,SEL selector) {
    ((void(*)(id,SEL))TPPanelLayoutOriginal)(container,selector);
    TPCommentsWidthChanged(container,NO);
}
static void TPPanelAdded(UIView *container,SEL selector,UIView *child) {
    ((void(*)(id,SEL,id))TPPanelAddedOriginal)(container,selector,child);
    TPCommentsWidthChanged(container,YES);
}
static void TPPanelRemoved(UIView *container,SEL selector,UIView *child) {
    ((void(*)(id,SEL,id))TPPanelRemovedOriginal)(container,selector,child);
    // Removal completes before the queued parent layout, which then sees the new top panel.
    TPCommentsWidthChanged(container,YES);
}
static void TPInstallCommentsWidth(void) {
    Class c=NSClassFromString(@"YTEngagementPanelContainerView");
    SEL layout=@selector(layoutSubviews),added=@selector(didAddSubview:),removed=@selector(willRemoveSubview:);
    Method lm=class_getInstanceMethod(c,layout),am=class_getInstanceMethod(c,added),rm=class_getInstanceMethod(c,removed);
    if(!lm||!am||!rm||strcmp(method_getTypeEncoding(lm),"v16@0:8")
       ||strcmp(method_getTypeEncoding(am),"v24@0:8@16")||strcmp(method_getTypeEncoding(rm),"v24@0:8@16"))return;
    TPPanelLayoutOriginal=method_getImplementation(lm);TPPanelAddedOriginal=method_getImplementation(am);TPPanelRemovedOriginal=method_getImplementation(rm);
    class_replaceMethod(c,layout,(IMP)TPPanelLayout,method_getTypeEncoding(lm));
    class_replaceMethod(c,added,(IMP)TPPanelAdded,method_getTypeEncoding(am));
    class_replaceMethod(c,removed,(IMP)TPPanelRemoved,method_getTypeEncoding(rm));
}
static BOOL TPHasViewIvar(Class c,const char *name) {
    Ivar iv=class_getInstanceVariable(c,name);return iv&&ivar_getTypeEncoding(iv)[0]=='@';
}
static BOOL TPVoidMethod(Class c,SEL selector) {
    Method m=class_getInstanceMethod(c,selector);return m&&strcmp(method_getTypeEncoding(m),"v16@0:8")==0;
}
BOOL TPInstallDuoWatchLayout(void) {
    if(TPFeedOriginal)return YES;
    Class feed=NSClassFromString(@"YTWatchNextView"),panel=NSClassFromString(@"YTEngagementPanelView"),chat=NSClassFromString(@"YCHLiveChatView"),watch=NSClassFromString(@"YTWatchView");
    SEL layout=@selector(layoutSubviews),moved=@selector(didMoveToWindow);
    SEL rect=NSSelectorFromString(@"contentViewRectForHeaderFrame:footerFrame:safeX:");
    Method method=class_getInstanceMethod(panel,rect);
    Method expanded=class_getInstanceMethod(watch,NSSelectorFromString(@"expandedPlayerSize"));
    Method appInsets=class_getInstanceMethod(watch,NSSelectorFromString(@"yt_safeAreaInsets"));
    if(!watch||!expanded||!appInsets||!feed||!panel||!chat||!TPVoidMethod(feed,layout)||!TPVoidMethod(chat,layout)
       ||!TPVoidMethod(feed,moved)||!TPVoidMethod(chat,moved)
       ||!TPHasViewIvar(feed,"_watchNextResultsView")||!TPHasViewIvar(panel,"_contentContainerView")||!TPHasViewIvar(chat,"_collectionView")||!method)return NO;
    NSMethodSignature *sig=[NSMethodSignature signatureWithObjCTypes:method_getTypeEncoding(method)];
    if(sig.numberOfArguments!=5||strcmp(sig.methodReturnType,@encode(CGRect))
       ||strcmp([sig getArgumentTypeAtIndex:2],@encode(CGRect))||strcmp([sig getArgumentTypeAtIndex:3],@encode(CGRect))
       ||strcmp([sig getArgumentTypeAtIndex:4],@encode(CGFloat)))return NO;
    NSMethodSignature *sizeSig=[NSMethodSignature signatureWithObjCTypes:method_getTypeEncoding(expanded)];
    NSMethodSignature *insetSig=[NSMethodSignature signatureWithObjCTypes:method_getTypeEncoding(appInsets)];
    if(sizeSig.numberOfArguments!=2||strcmp(sizeSig.methodReturnType,@encode(CGSize))
       ||insetSig.numberOfArguments!=2||strcmp(insetSig.methodReturnType,@encode(UIEdgeInsets)))return NO;
    TPFeedOriginal=method_getImplementation(class_getInstanceMethod(feed,layout));
    TPPanelRectOriginal=method_getImplementation(method);TPChatOriginal=method_getImplementation(class_getInstanceMethod(chat,layout));
    TPFeedMovedOriginal=method_getImplementation(class_getInstanceMethod(feed,moved));TPChatMovedOriginal=method_getImplementation(class_getInstanceMethod(chat,moved));
    TPExpandedSizeOriginal=method_getImplementation(expanded);TPAppInsetsOriginal=method_getImplementation(appInsets);
    class_replaceMethod(watch,NSSelectorFromString(@"yt_safeAreaInsets"),(IMP)TPAppInsets,method_getTypeEncoding(appInsets));
    class_replaceMethod(watch,NSSelectorFromString(@"expandedPlayerSize"),(IMP)TPExpandedSize,method_getTypeEncoding(expanded));
    class_replaceMethod(feed,layout,(IMP)TPFeedLayout,"v16@0:8");
    class_replaceMethod(panel,rect,(IMP)TPPanelContentRect,method_getTypeEncoding(method));
    class_replaceMethod(chat,layout,(IMP)TPChatLayout,"v16@0:8");
    class_replaceMethod(feed,moved,(IMP)TPFeedMoved,"v16@0:8");class_replaceMethod(chat,moved,(IMP)TPChatMoved,"v16@0:8");
    TPInstallCommentsWidth();
    return YES;
}
#ifndef TP_FIXTURE
__attribute__((constructor)) static void TPInitialize(void) {dispatch_async(dispatch_get_main_queue(),^{ TPInstallDuoWatchLayout(); });}
#endif

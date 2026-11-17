#import <UIKit/UIKit.h>
#import <QuartzCore/QuartzCore.h>
#import <AVFoundation/AVFoundation.h>
#import <objc/runtime.h>
#import <dlfcn.h>
#import <mach-o/dyld.h>
#import <mach-o/loader.h>
#include <sys/utsname.h>
#include <math.h>
#include <string.h>

// Read-only diagnostic observers. Forward native layout calls; never set content frames or safe areas.
static NSString *const TPDiagVersion=@"YouTubePlus-layout-diagnostics.1";
static char TPButtonKey;
static NSTimer *TPTimer;
static NSMutableArray *TPHistory;
static NSString *TPLastMode;
static IMP TPObservedOuter,TPObservedRegular,TPObservedCompact;
static NSUInteger TPOuterCalls,TPRegularCalls,TPCompactCalls;
static NSMutableArray *TPLayoutHistory;
static NSTimeInterval TPLastCapture[3];
static id SafeJSON(id value){
    if([value isKindOfClass:NSNumber.class])return isfinite([value doubleValue])?value:NSNull.null;
    if([value isKindOfClass:NSString.class]||value==NSNull.null)return value;
    if([value isKindOfClass:NSArray.class]){NSMutableArray *r=[NSMutableArray new];for(id v in value)[r addObject:SafeJSON(v) ?: NSNull.null];return r;}
    if([value isKindOfClass:NSDictionary.class]){NSMutableDictionary *r=[NSMutableDictionary new];for(id k in value)if([k isKindOfClass:NSString.class])r[k]=SafeJSON(value[k]) ?: NSNull.null;return r;}
    return NSNull.null;
}
NSData *TPDiagnosticsJSON(NSDictionary *value){return [NSJSONSerialization dataWithJSONObject:SafeJSON(value) options:NSJSONWritingSortedKeys error:nil];}
static NSArray *R(CGRect r){return @[@(r.origin.x),@(r.origin.y),@(r.size.width),@(r.size.height)];}
static NSArray *E(UIEdgeInsets e){return @[@(e.top),@(e.left),@(e.bottom),@(e.right)];}
static NSArray *T(CGAffineTransform t){return @[@(t.a),@(t.b),@(t.c),@(t.d),@(t.tx),@(t.ty)];}
static NSString *Name(id o){return o?NSStringFromClass([o class]):@"nil";}
static NSString *ImageForPointer(const void *p){Dl_info d={0};return p&&dladdr(p,&d)&&d.dli_fname?[@(d.dli_fname) lastPathComponent]:@"unknown";}
static BOOL Finite(CGRect r){return isfinite(r.origin.x)&&isfinite(r.origin.y)&&isfinite(r.size.width)&&isfinite(r.size.height);}

static NSInvocation *Invocation(id object,NSString *name){
    SEL s=NSSelectorFromString(name);if(!object||![object respondsToSelector:s])return nil;
    NSMethodSignature *sig=[object methodSignatureForSelector:s];if(!sig)return nil;
    NSInvocation *i=[NSInvocation invocationWithMethodSignature:sig];i.target=object;i.selector=s;return i;
}
static id ObjectGetter(id object,NSString *name){
    NSInvocation *i=Invocation(object,name);if(!i||i.methodSignature.numberOfArguments!=2||i.methodSignature.methodReturnType[0]!='@')return nil;
    @try{[i invoke];__unsafe_unretained id value=nil;[i getReturnValue:&value];return value;}@catch(NSException *e){return nil;}
}
static id ScalarGetter(id object,NSString *name){
    NSInvocation *i=Invocation(object,name);if(!i||i.methodSignature.numberOfArguments!=2)return NSNull.null;
    const char *type=i.methodSignature.methodReturnType;
    @try{
        if((type[0]=='B'||type[0]=='c')&&i.methodSignature.methodReturnLength==1){unsigned char v=0;[i invoke];[i getReturnValue:&v];return @(v!=0);}
        if(type[0]=='d'&&i.methodSignature.methodReturnLength==sizeof(double)){double v=0;[i invoke];[i getReturnValue:&v];return isfinite(v)?@(v):NSNull.null;}
        if((type[0]=='q'||type[0]=='Q')&&i.methodSignature.methodReturnLength==8){long long v=0;[i invoke];[i getReturnValue:&v];return @(v);}
    }@catch(NSException *e){}
    return NSNull.null;
}
static id RectGetter(id object,NSString *name){
    NSInvocation *i=Invocation(object,name);if(!i||i.methodSignature.numberOfArguments!=2||i.methodSignature.methodReturnLength!=sizeof(CGRect)||!strstr(i.methodSignature.methodReturnType,"CGRect"))return NSNull.null;
    @try{CGRect r=CGRectZero;[i invoke];[i getReturnValue:&r];return Finite(r)?R(r):NSNull.null;}@catch(NSException *e){return NSNull.null;}
}
static id InsetsGetter(id object,NSString *name){
    NSInvocation *i=Invocation(object,name);if(!i||i.methodSignature.numberOfArguments!=2||i.methodSignature.methodReturnLength!=sizeof(UIEdgeInsets)||!strstr(i.methodSignature.methodReturnType,"UIEdgeInsets"))return NSNull.null;
    @try{UIEdgeInsets v=UIEdgeInsetsZero;[i invoke];[i getReturnValue:&v];return E(v);}@catch(NSException *e){return NSNull.null;}
}
static NSDictionary *RegionReport(UIView *view){
    NSInvocation *query=Invocation(view,@"reservedRegionsOfKind:options:");
    if(!query)return @{@"available":@NO};
    NSMutableDictionary *result=[@{@"available":@YES,@"signature":@(query.methodSignature.methodReturnType)} mutableCopy];
    if(query.methodSignature.numberOfArguments!=4||query.methodSignature.methodReturnType[0]!='@'||[query.methodSignature getArgumentTypeAtIndex:2][0]!='@')return result;
    const char *optionType=[query.methodSignature getArgumentTypeAtIndex:3];
    if(!strchr("QqLlIi",optionType[0]))return result;
    NSMutableArray *all=[NSMutableArray new],*queried=[NSMutableArray new];
    for(NSString *className in @[@"UIViewReservedRegion",@"UIReservedRegion"]){
        Class c=NSClassFromString(className);if(!c)continue;
        for(NSString *getter in @[@"occlusionRegionKind",@"divisionRegionKind"]){
            id kind=ObjectGetter(c,getter);if(!kind)continue;
            [queried addObject:@{@"factory":className,@"selector":getter,@"type":Name(kind)}];
            @try{
                NSUInteger options=0;__unsafe_unretained id argument=kind;
                [query setArgument:&argument atIndex:2];[query setArgument:&options atIndex:3];[query invoke];
                __unsafe_unretained id raw=nil;[query getReturnValue:&raw];
                if(![raw isKindOfClass:NSArray.class])continue;
                NSUInteger count=0;for(id region in raw){if(count++>=32)break;
                    [all addObject:@{@"kind":getter,@"class":Name(region),@"frame":RectGetter(region,@"frame"),@"margins":InsetsGetter(region,@"margins"),@"active":ScalarGetter(region,@"isActive")}];
                }
            }@catch(NSException *e){result[@"queryError"]=Name(e);}
        }
    }
    result[@"regions"]=all;result[@"queriedKinds"]=queried;return result;
}

static NSArray<UIWindow *> *Windows(void){
    NSMutableArray *result=[NSMutableArray new];
    for(UIScene *scene in UIApplication.sharedApplication.connectedScenes)
        if([scene isKindOfClass:UIWindowScene.class]&&scene.activationState==UISceneActivationStateForegroundActive)
            for(UIWindow *window in ((UIWindowScene *)scene).windows)if(!window.hidden&&window.alpha>0.01)[result addObject:window];
    // Legacy lifecycle: the app delegate's own window, never an arbitrary screen or scene.
    if(!result.count&&UIApplication.sharedApplication.applicationState==UIApplicationStateActive){id window=ObjectGetter(UIApplication.sharedApplication.delegate,@"window");if([window isKindOfClass:UIWindow.class]&&![window isHidden]&&[window alpha]>0.01)[result addObject:window];}
    return result;
}
static NSDictionary *BuildVersion(const struct mach_header *header){
    if(!header||header->magic!=MH_MAGIC_64)return @{};
    const uint8_t *cursor=(const uint8_t *)header+sizeof(struct mach_header_64);
    const uint8_t *end=cursor+header->sizeofcmds;
    for(uint32_t n=0;n<header->ncmds&&cursor+sizeof(struct load_command)<=end;n++){
        const struct load_command *command=(const void *)cursor;
        if(command->cmdsize<sizeof(*command)||cursor+command->cmdsize>end)break;
        if(command->cmd==LC_BUILD_VERSION&&command->cmdsize>=sizeof(struct build_version_command)){
            const struct build_version_command *v=(const void *)cursor;
            return @{@"platform":@(v->platform),@"minOS":@(v->minos),@"sdk":@(v->sdk)};
        }cursor+=command->cmdsize;
    }return @{};
}
static NSArray *Images(void){
    NSMutableArray *r=[NSMutableArray new];
    for(uint32_t n=0;n<_dyld_image_count();n++){
        const char *raw=_dyld_get_image_name(n);if(!raw)continue;NSString *path=@(raw);
        if([path containsString:@".app/"]||[path containsString:@"CoreSimulator"]||[path hasSuffix:@"/UIKitCore"])
            [r addObject:@{@"name":path.lastPathComponent,@"build":BuildVersion(_dyld_get_image_header(n))}];
    }return r;
}
static NSArray *Methods(void){
    NSDictionary *wanted=@{
        @"YTWatchView":@[@"layoutSubviews",@"layoutSubviews_regular",@"layoutSubviews_compact",@"watchNextSafeAreaInsets",@"isFullscreen",@"setFrame:"],
        @"YTWatchLayerView":@[@"layoutSubviews",@"safeAreaInsets"],
        @"YTWatchViewController":@[@"viewDidLayoutSubviews",@"prefersStatusBarHidden"],
        @"YTAppViewControllerImpl":@[@"viewDidLayoutSubviews"],
        @"UIView":@[@"safeAreaInsets",@"reservedRegionsOfKind:options:"]};
    NSMutableArray *r=[NSMutableArray new];for(NSString *name in wanted){Class c=NSClassFromString(name);
        for(NSString *selector in wanted[name]){Method m=class_getInstanceMethod(c,NSSelectorFromString(selector));
            [r addObject:@{@"class":name,@"selector":selector,@"present":@(m!=NULL),@"type":m?@(method_getTypeEncoding(m)):@"",@"ownerImage":m?ImageForPointer((const void *)method_getImplementation(m)):@""}];
        }
    }return r;
}
static NSDictionary *DisplayPreferences(void){
    NSMutableDictionary *r=[NSMutableDictionary new];NSDictionary *prefs=NSUserDefaults.standardUserDefaults.dictionaryRepresentation;
    NSRegularExpression *pattern=[NSRegularExpression regularExpressionWithPattern:@"layout|ipad|tablet|duo|statusbar|safearea|fullscreen|rotation|hinge" options:NSRegularExpressionCaseInsensitive error:nil];
    NSRegularExpression *privateKey=[NSRegularExpression regularExpressionWithPattern:@"user|account|auth|token|cookie|session|mail|number|serial|receipt|purchase|subscription|identifier|udid|name" options:NSRegularExpressionCaseInsensitive error:nil];
    for(NSString *key in prefs){
        if(![key isKindOfClass:NSString.class]||key.length>=100||![prefs[key] isKindOfClass:NSNumber.class])continue;
        double value=[prefs[key]doubleValue];if(!isfinite(value)||value<0||value>8||floor(value)!=value)continue;
        NSRange range=NSMakeRange(0,key.length);
        if([pattern firstMatchInString:key options:0 range:range]&&![privateKey firstMatchInString:key options:0 range:range])r[key]=prefs[key];
    }
    return r;
}
static id HelperEligibility(UIView *view){
    Class watch=NSClassFromString(@"YTWatchView");if(!watch||![view isKindOfClass:watch])return NSNull.null;
    void *function=dlsym(RTLD_DEFAULT,"TPWatchGeometryEligible");
    if(!function||![ImageForPointer(function)isEqualToString:@"DuoWatchLayout.dylib"])return NSNull.null;
    return @(((BOOL(*)(UIView *))function)(view));
}
static NSDictionary *SmallState(UIView *view){
    UIWindow *window=view.window;
    return @{@"class":Name(view),@"frame":R(view.frame),@"bounds":R(view.bounds),@"safe":E(view.safeAreaInsets),@"window":window?R(window.bounds):@[],@"windowSafe":window?E(window.safeAreaInsets):@[],@"windowRect":window?R([view convertRect:view.bounds toView:window]):@[],@"full":ScalarGetter(view,@"isFullscreen"),@"helperEligible":HelperEligibility(view)};
}
static void ObserveLayout(UIView *view,SEL selector){
    NSUInteger index=selector==NSSelectorFromString(@"layoutSubviews_regular")?1:selector==NSSelectorFromString(@"layoutSubviews_compact")?2:0;
    IMP original=index==1?TPObservedRegular:index==2?TPObservedCompact:TPObservedOuter;
    if(!original)return;
    if(NSThread.isMainThread){if(index==1)TPRegularCalls++;else if(index==2)TPCompactCalls++;else TPOuterCalls++;}
    NSTimeInterval now=NSDate.date.timeIntervalSince1970;
    BOOL capture=NSThread.isMainThread&&view.window&&now-TPLastCapture[index]>0.5;
    NSDictionary *before=capture?SmallState(view):nil;
    ((void(*)(id,SEL))original)(view,selector);
    if(capture){TPLastCapture[index]=now;if(!TPLayoutHistory)TPLayoutHistory=[NSMutableArray new];[TPLayoutHistory addObject:@{@"selector":NSStringFromSelector(selector),@"time":@(now),@"before":before,@"after":SmallState(view)}];if(TPLayoutHistory.count>18)[TPLayoutHistory removeObjectAtIndex:0];}
}
static void InstallObservers(void){
    Class c=NSClassFromString(@"YTWatchView");if(!c)return;
    NSArray *names=@[@"layoutSubviews",@"layoutSubviews_regular",@"layoutSubviews_compact"];
    IMP *slots[]={&TPObservedOuter,&TPObservedRegular,&TPObservedCompact};
    for(NSUInteger n=0;n<names.count;n++){
        if(*slots[n])continue;SEL s=NSSelectorFromString(names[n]);Method m=class_getInstanceMethod(c,s);
        if(!m||strcmp(method_getTypeEncoding(m),"v16@0:8"))continue;
        *slots[n]=method_getImplementation(m);class_replaceMethod(c,s,(IMP)ObserveLayout,method_getTypeEncoding(m));
    }
}
static NSDictionary *ObserverStatus(void){
    NSMutableDictionary *r=[NSMutableDictionary new];Class c=NSClassFromString(@"YTWatchView");
    NSArray *names=@[@"layoutSubviews",@"layoutSubviews_regular",@"layoutSubviews_compact"];
    IMP previous[]={TPObservedOuter,TPObservedRegular,TPObservedCompact};NSUInteger counts[]={TPOuterCalls,TPRegularCalls,TPCompactCalls};
    for(NSUInteger n=0;n<names.count;n++){Method m=class_getInstanceMethod(c,NSSelectorFromString(names[n]));IMP current=m?method_getImplementation(m):NULL;
        r[names[n]]=@{@"installed":@(previous[n]!=NULL),@"calls":@(counts[n]),@"previousOwner":ImageForPointer((const void *)previous[n]),@"currentOwner":ImageForPointer((const void *)current),@"stillObserving":@(current==(IMP)ObserveLayout)};
    }return r;
}

@interface TPReportCollector : NSObject
@property(nonatomic,strong) NSMapTable<id,NSNumber *> *ids;
@property(nonatomic,strong) NSMutableArray *nodes;
@property(nonatomic,strong) NSMutableArray *constraints;
@property(nonatomic,strong) NSMutableArray *controllers;
@property(nonatomic,strong) NSMutableArray *roles;
@property(nonatomic,strong) NSHashTable *seenControllers;
@property NSUInteger nextID;
@property BOOL truncated;
- (NSDictionary *)collect:(UIWindow *)selected;
@end
@implementation TPReportCollector
- (instancetype)init{if((self=[super init])){self.ids=[NSMapTable weakToStrongObjectsMapTable];self.nodes=[NSMutableArray new];self.constraints=[NSMutableArray new];self.controllers=[NSMutableArray new];self.roles=[NSMutableArray new];self.seenControllers=[NSHashTable weakObjectsHashTable];self.nextID=1;}return self;}
- (NSNumber *)number:(id)o{if(!o)return @0;NSNumber *n=[self.ids objectForKey:o];if(!n){n=@(self.nextID++);[self.ids setObject:n forKey:o];}return n;}
- (NSDictionary *)item:(id)o{
    if(!o)return @{@"id":@0};
    if([o isKindOfClass:UILayoutGuide.class]){UILayoutGuide *g=o;return @{@"id":[self number:o],@"class":Name(o),@"owner":[self number:g.owningView],@"frame":R(g.layoutFrame),@"safeGuide":@(g==g.owningView.safeAreaLayoutGuide),@"marginsGuide":@(g==g.owningView.layoutMarginsGuide)};}
    return @{@"id":[self number:o],@"class":Name(o)};
}
- (NSArray *)layer:(CALayer *)layer depth:(NSUInteger)depth{
    if(!layer||depth>2)return @[];NSMutableArray *r=[NSMutableArray new];NSUInteger count=0;
    for(CALayer *l in layer.sublayers){if(count++>=24){self.truncated=YES;break;}
        NSMutableDictionary *d=[@{@"class":Name(l),@"f":R(l.frame),@"b":R(l.bounds),@"clip":@(l.masksToBounds),@"a":@(l.opacity),@"hidden":@(l.hidden),@"corner":@(l.cornerRadius)} mutableCopy];
        if(l.mask)d[@"mask"]=@{@"class":Name(l.mask),@"f":R(l.mask.frame),@"b":R(l.mask.bounds)};
        if([l isKindOfClass:AVPlayerLayer.class]){AVPlayerLayer *p=(id)l;d[@"gravity"]=p.videoGravity ?: @"nil";d[@"videoRect"]=R(p.videoRect);d[@"ready"]=@(p.readyForDisplay);}
        if([l isKindOfClass:CAShapeLayer.class]&&((CAShapeLayer *)l).path)d[@"pathBounds"]=R(CGPathGetBoundingBox(((CAShapeLayer *)l).path));
        if(l.backgroundColor)d[@"bgAlpha"]=@(CGColorGetAlpha(l.backgroundColor));
        if(depth<2&&![l.delegate isKindOfClass:UIView.class])d[@"sub"]= [self layer:l depth:depth+1];
        [r addObject:d];
    }return r;
}
- (void)constraintsOf:(UIView *)view{
    for(NSLayoutConstraint *c in view.constraints){
        if(!c.active)continue;if(self.constraints.count>=1600){self.truncated=YES;return;}
        [self.constraints addObject:@{@"owner":[self number:view],@"first":[self item:c.firstItem],@"second":[self item:c.secondItem],@"fa":@(c.firstAttribute),@"sa":@(c.secondAttribute),@"rel":@(c.relation),@"k":@(c.constant),@"m":@(c.multiplier),@"priority":@(c.priority)}];
    }
}
- (void)roleFields:(UIView *)view{
    NSString *name=Name(view);if(![name containsString:@"Watch"]&&![name containsString:@"Player"]&&![name containsString:@"AppView"])return;
    NSMutableDictionary *r=[@{@"id":[self number:view],@"class":name} mutableCopy];
    NSMutableDictionary *fields=[NSMutableDictionary new];
    for(NSString *field in @[@"_watchNextWrapperView",@"_engagementPanelView",@"_playerView",@"_playerThumbnailContainerView",@"_cinematicContainerView",@"_hingeBackgroundView",@"_statusBarView",@"_backgroundScrim",@"_animationTransitionScrim",@"_watchCollectionView"]){
        Ivar iv=class_getInstanceVariable(object_getClass(view),field.UTF8String);if(!iv||ivar_getTypeEncoding(iv)[0]!='@')continue;
        id value=object_getIvar(view,iv);if([value isKindOfClass:UIView.class])fields[field]=[self item:value];
    }
    r[@"views"]=fields;r[@"nativeInsets"]=InsetsGetter(view,@"watchNextSafeAreaInsets");
    r[@"full"]=ScalarGetter(view,@"isFullscreen");r[@"regions"]=RegionReport(view);
    r[@"layoutHelperEligibleNow"]=HelperEligibility(view);
    NSMutableDictionary *flags=[NSMutableDictionary new];
    for(NSString *field in @[@"_fullscreen",@"_isWideLayout",@"_horizontalSafeAreaInsetSupportEnabled",@"_watchNextExtendsToScreenEdgeEnabled",@"_engagementPanelExtendsToScreenEdgeEnabled",@"_watchNextScreenEdgeExtension",@"_engagementPanelScreenEdgeExtension",@"_hingeLayoutMode"]){
        Ivar iv=class_getInstanceVariable(object_getClass(view),field.UTF8String);if(!iv)continue;const char *type=ivar_getTypeEncoding(iv);ptrdiff_t offset=ivar_getOffset(iv);size_t size=class_getInstanceSize(object_getClass(view));
        const uint8_t *base=(__bridge const void *)view;if(offset<0||(size_t)offset>=size)continue;
        if(type[0]=='B'||type[0]=='c')flags[field]=@(base[offset]!=0);
        else if(type[0]=='d'&&(size_t)offset+8<=size){double d=0;memcpy(&d,base+offset,8);if(isfinite(d))flags[field]=@(d);}
        else if(type[0]=='q'&&(size_t)offset+8<=size){long long q=0;memcpy(&q,base+offset,8);flags[field]=@(q);}
    }r[@"flags"]=flags;[self.roles addObject:r];
}
- (void)view:(UIView *)view parent:(UIView *)parent window:(UIWindow *)window depth:(NSUInteger)depth{
    if([view isKindOfClass:NSClassFromString(@"TPDiagButton")])return;
    if(depth>25||self.nodes.count>=650){self.truncated=YES;return;}
    CGRect wr=[view convertRect:view.bounds toView:window];
    NSMutableDictionary *d=[@{@"id":[self number:view],@"p":[self number:parent],@"c":Name(view),@"f":R(view.frame),@"b":R(view.bounds),@"wr":Finite(wr)?R(wr):@[],@"si":E(view.safeAreaInsets),@"lm":E(view.layoutMargins),@"clip":@(view.clipsToBounds),@"opaque":@(view.opaque),@"autoMask":@(view.translatesAutoresizingMaskIntoConstraints)} mutableCopy];
    if(view.hidden)d[@"hidden"]=@YES;if(view.alpha!=1)d[@"a"]=@(view.alpha);
    if(!CGAffineTransformIsIdentity(view.transform))d[@"t"]=T(view.transform);
    if(view.backgroundColor){UIColor *color=[view.backgroundColor resolvedColorWithTraitCollection:view.traitCollection];CGFloat r=0,g=0,b=0,a=0;if([color getRed:&r green:&g blue:&b alpha:&a])d[@"bg"]=@[@(r),@(g),@(b),@(a)];else if(color.CGColor)d[@"bgAlpha"]=@(CGColorGetAlpha(color.CGColor));}
    if(view.layer.mask){NSMutableDictionary *m=[@{@"c":Name(view.layer.mask),@"f":R(view.layer.mask.frame),@"b":R(view.layer.mask.bounds)}mutableCopy];if([view.layer.mask isKindOfClass:CAShapeLayer.class]&&((CAShapeLayer *)view.layer.mask).path)m[@"pathBounds"]=R(CGPathGetBoundingBox(((CAShapeLayer *)view.layer.mask).path));d[@"mask"]=m;}
    if(view.layer.zPosition)d[@"z"]=@(view.layer.zPosition);
    d[@"mode"]=@(view.contentMode);if(view.autoresizingMask)d[@"resize"]=@(view.autoresizingMask);
    CALayer *presentation=view.layer.presentationLayer;
    if(presentation&&(!CGRectEqualToRect(presentation.frame,view.layer.frame)||fabs(presentation.opacity-view.layer.opacity)>.01))d[@"presentation"]=@{@"f":R(presentation.frame),@"b":R(presentation.bounds),@"a":@(presentation.opacity)};
    if(view.layer.masksToBounds)d[@"layerClip"]=@YES;if(view.layer.cornerRadius)d[@"corner"]=@(view.layer.cornerRadius);
    if([view isKindOfClass:UIScrollView.class]){UIScrollView *s=(id)view;d[@"scroll"]=@{@"size":@[@(s.contentSize.width),@(s.contentSize.height)],@"offset":@[@(s.contentOffset.x),@(s.contentOffset.y)],@"inset":E(s.contentInset),@"adjusted":E(s.adjustedContentInset),@"adjustment":@(s.contentInsetAdjustmentBehavior)};}
    NSString *name=Name(view);
    if([name containsString:@"Player"]||[name containsString:@"Watch"]||view.layer.mask)d[@"layers"]= [self layer:view.layer depth:0];
    [self.nodes addObject:d];[self constraintsOf:view];[self roleFields:view];
    // Collection/table cell contents and text-input internals are irrelevant to this boundary and may contain private text.
    if(view.hidden||view.alpha<0.01||[view isKindOfClass:UICollectionViewCell.class]||[view isKindOfClass:UITableViewCell.class]||[view conformsToProtocol:@protocol(UITextInput)]){d[@"pruned"]=@YES;return;}
    for(UIView *child in view.subviews.reverseObjectEnumerator)[self view:child parent:view window:window depth:depth+1];
}
- (void)controller:(UIViewController *)vc parent:(UIViewController *)parent{
    if(!vc||[self.seenControllers containsObject:vc]||self.controllers.count>=120)return;[self.seenControllers addObject:vc];
    NSMutableDictionary *d=[@{@"id":[self number:vc],@"p":[self number:parent],@"class":Name(vc),@"loaded":@(vc.isViewLoaded),@"additionalInsets":E(vc.additionalSafeAreaInsets),@"edges":@(vc.edgesForExtendedLayout),@"opaqueBars":@(vc.extendedLayoutIncludesOpaqueBars),@"hSize":@(vc.traitCollection.horizontalSizeClass),@"vSize":@(vc.traitCollection.verticalSizeClass),@"preferredStatusHidden":@(vc.prefersStatusBarHidden)} mutableCopy];
    if(vc.isViewLoaded)d[@"view"]= [self number:vc.view];if(vc.presentedViewController)d[@"presented"]= [self number:vc.presentedViewController];
    [self.controllers addObject:d];for(UIViewController *child in vc.childViewControllers)[self controller:child parent:vc];[self controller:vc.presentedViewController parent:vc];
}
- (NSDictionary *)collect:(UIWindow *)selected{
    NSAssert(NSThread.isMainThread,@"UIKit collection must run on main thread");
    NSMutableArray *windows=[NSMutableArray new];NSMutableArray *ordered=[Windows() mutableCopy];if(selected){[ordered removeObject:selected];[ordered insertObject:selected atIndex:0];}
    for(UIWindow *window in ordered){
        NSMutableDictionary *d=[@{@"id":[self number:window],@"selected":@(window==selected),@"class":Name(window),@"key":@(window.isKeyWindow),@"level":@(window.windowLevel),@"bounds":R(window.bounds),@"frame":R(window.frame),@"safe":E(window.safeAreaInsets),@"screenBounds":R(window.screen.bounds),@"screenNativeBounds":R(window.screen.nativeBounds),@"screenScale":@(window.screen.scale),@"screenFrame":R([window convertRect:window.bounds toCoordinateSpace:window.screen.coordinateSpace]),@"hSize":@(window.traitCollection.horizontalSizeClass),@"vSize":@(window.traitCollection.verticalSizeClass)} mutableCopy];
        UIWindowScene *scene=window.windowScene;if(scene){d[@"sceneState"]=@(scene.activationState);d[@"orientation"]=@(scene.interfaceOrientation);d[@"sceneBounds"]=R(scene.coordinateSpace.bounds);UIStatusBarManager *status=scene.statusBarManager;if(status)d[@"systemStatus"]=@{@"frame":R(status.statusBarFrame),@"hidden":@(status.isStatusBarHidden)};}
        d[@"regions"]=RegionReport(window);[windows addObject:d];
        [self controller:window.rootViewController parent:nil];if(window.windowLevel==UIWindowLevelNormal)[self view:window parent:nil window:window depth:0];
    }
    struct utsname hardware;uname(&hardware);
    return @{@"diagnostic":TPDiagVersion,@"time":@((long long)NSDate.date.timeIntervalSince1970),@"device":@{@"modelIdentifier":@(hardware.machine),@"os":UIDevice.currentDevice.systemVersion,@"idiom":@(UIDevice.currentDevice.userInterfaceIdiom)},@"bundle":@{@"identifier":NSBundle.mainBundle.bundleIdentifier ?: @"",@"version":[NSBundle.mainBundle objectForInfoDictionaryKey:@"CFBundleShortVersionString"] ?: @"",@"build":[NSBundle.mainBundle objectForInfoDictionaryKey:@"CFBundleVersion"] ?: @""},@"windows":windows,@"controllers":self.controllers,@"views":self.nodes,@"constraints":self.constraints,@"roles":self.roles,@"methods":Methods(),@"images":Images(),@"displayPreferences":DisplayPreferences(),@"recentGeometry":TPHistory ?: @[],@"layoutObservers":ObserverStatus(),@"layoutCallHistory":TPLayoutHistory ?: @[],@"truncated":@(self.truncated),@"privacy":@"No view text, account data, cookies, auth tokens, screenshots, video URLs or network logs collected.",@"legend":@{@"rect":@"[x,y,width,height] points",@"insets":@"[top,left,bottom,right]",@"view":@"id=object ID,p=parent,c=class,f=frame,b=bounds,wr=rect in owning window,si=safe insets,lm=layout margins,t=transform",@"constraint":@"fa/sa=NSLayoutAttribute,rel=NSLayoutRelation,k=constant,m=multiplier; no private identifiers"}};
}
@end

@interface TPDiagButton : UIButton
@end
@implementation TPDiagButton
- (instancetype)initWithFrame:(CGRect)frame{if((self=[super initWithFrame:frame])){
    [self setTitle:@"Copy diagnostics" forState:UIControlStateNormal];self.titleLabel.font=[UIFont systemFontOfSize:13 weight:UIFontWeightSemibold];self.backgroundColor=[UIColor colorWithRed:.42 green:.20 blue:.75 alpha:.95];self.layer.cornerRadius=16;self.accessibilityLabel=@"Copy YouTubePlus layout diagnostics";
    [self setTitleColor:UIColor.whiteColor forState:UIControlStateNormal];
    [self addTarget:self action:@selector(copyReport) forControlEvents:UIControlEventTouchUpInside];objc_setAssociatedObject(self,&TPButtonKey,@YES,OBJC_ASSOCIATION_RETAIN_NONATOMIC);
}return self;}
- (void)copyReport{
    self.enabled=NO;[self setTitle:@"Collecting..." forState:UIControlStateNormal];
    dispatch_async(dispatch_get_main_queue(),^{
        @try{
            NSDictionary *report=[[TPReportCollector new]collect:self.window];
            NSData *data=TPDiagnosticsJSON(report);
            if(!data){[self setTitle:@"Copy failed" forState:UIControlStateNormal];self.enabled=YES;return;}
            NSString *json=[[NSString alloc]initWithData:data encoding:NSUTF8StringEncoding];
            UIPasteboard.generalPasteboard.string=[@"YouTubePlus Layout Diagnostics 1\n" stringByAppendingString:json];
            [self setTitle:[NSString stringWithFormat:@"Copied (%lu KB)",(unsigned long)((data.length+1023)/1024)] forState:UIControlStateNormal];
        }@catch(NSException *e){[self setTitle:@"Copy failed" forState:UIControlStateNormal];}
        self.enabled=YES;
        dispatch_after(dispatch_time(DISPATCH_TIME_NOW,3*NSEC_PER_SEC),dispatch_get_main_queue(),^{[self setTitle:@"Copy diagnostics" forState:UIControlStateNormal];});
    });
}
@end
static void Tick(void){
    if(UIApplication.sharedApplication.applicationState!=UIApplicationStateActive)return;
    InstallObservers();
    NSMutableArray *mode=[NSMutableArray new];
    for(UIWindow *window in Windows()){
        if(window.windowLevel!=UIWindowLevelNormal)continue;
        TPDiagButton *button=objc_getAssociatedObject(window,&TPButtonKey);
        if(!button){button=[[TPDiagButton alloc]initWithFrame:CGRectZero];objc_setAssociatedObject(window,&TPButtonKey,button,OBJC_ASSOCIATION_RETAIN_NONATOMIC);[window addSubview:button];}
        UIEdgeInsets safe=window.safeAreaInsets;button.frame=CGRectMake(CGRectGetMinX(window.bounds)+safe.left+10,CGRectGetMaxY(window.bounds)-safe.bottom-44,154,34);[window bringSubviewToFront:button];
        // Lightweight geometry history, with no content or text. Full capture occurs only on the user's tap.
        NSMutableArray *queue=[@[window] mutableCopy];NSUInteger seen=0;NSMutableArray *watch=[NSMutableArray new];
        while(queue.count&&seen++<900){UIView *v=queue.firstObject;[queue removeObjectAtIndex:0];if([Name(v) isEqualToString:@"YTWatchView"])[watch addObject:@{@"class":Name(v),@"wr":R([v convertRect:v.bounds toView:window]),@"safe":E(v.safeAreaInsets),@"full":ScalarGetter(v,@"isFullscreen"),@"hidden":@(v.hidden)}];if(![v isKindOfClass:UICollectionViewCell.class]&&![v isKindOfClass:UITableViewCell.class])[queue addObjectsFromArray:v.subviews];}
        [mode addObject:@{@"window":R(window.bounds),@"safe":E(safe),@"watch":watch}];
    }
    NSData *data=TPDiagnosticsJSON(@{@"windows":mode});NSString *signature=data?[[NSString alloc]initWithData:data encoding:NSUTF8StringEncoding]:@"";
    if(![signature isEqualToString:TPLastMode]){TPLastMode=signature;if(!TPHistory)TPHistory=[NSMutableArray new];[TPHistory addObject:@{@"time":@((long long)NSDate.date.timeIntervalSince1970),@"geometry":mode}];if(TPHistory.count>12)[TPHistory removeObjectAtIndex:0];}
}
#ifndef TP_DIAGNOSTIC_TEST
__attribute__((constructor)) static void TPStartDiagnostics(void){dispatch_async(dispatch_get_main_queue(),^{TPTimer=[NSTimer scheduledTimerWithTimeInterval:1.5 repeats:YES block:^(NSTimer *timer){Tick();}];[NSRunLoop.mainRunLoop addTimer:TPTimer forMode:NSRunLoopCommonModes];Tick();});}
#endif
NSDictionary *TPCollectDiagnostics(UIWindow *window){return [[TPReportCollector new]collect:window];}
void TPShowDiagnosticButton(void){Tick();}

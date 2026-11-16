#import <UIKit/UIKit.h>
extern BOOL TPWatchGeometryEligible(UIView *);
extern BOOL TPWatchExpandTrailing(UIView *,UIWindow *);
extern BOOL TPInstallDuoWatchLayout(void);
@interface TPFixtureWindow : UIWindow
@property UIEdgeInsets testInsets;
@end
@implementation TPFixtureWindow
- (UIEdgeInsets)safeAreaInsets{return self.testInsets;}
@end
@interface YTWatchLayerView : UIView
@end
@implementation YTWatchLayerView
@end
@interface YTWatchView : UIView {
@public UIView *_watchNextWrapperView;
@public UIView *_engagementPanelView;
}
@property BOOL fullscreen;
@property BOOL retainNativePadding;
@property NSInteger layoutCalls;
@property UIEdgeInsets hostInsets;
- (BOOL)isFullscreen;
- (UIEdgeInsets)watchNextSafeAreaInsets;
- (void)layoutSubviews_regular;
- (void)layoutSubviews_compact;
@end
@implementation YTWatchView
- (instancetype)initWithFrame:(CGRect)rect {
    if((self=[super initWithFrame:rect])){
        self.hostInsets=UIEdgeInsetsMake(0,0,0,84);
        _watchNextWrapperView=[UIView new];_engagementPanelView=[UIView new];
        [self addSubview:_watchNextWrapperView];[self addSubview:_engagementPanelView];
    }return self;
}
- (BOOL)isFullscreen{return self.fullscreen;}
- (UIEdgeInsets)safeAreaInsets{return self.hostInsets;}
- (UIEdgeInsets)watchNextSafeAreaInsets{return self.hostInsets;}
- (void)layoutSubviews_regular {
    self.layoutCalls++;
    CGFloat right=self.retainNativePadding?84:[self watchNextSafeAreaInsets].right;
    _watchNextWrapperView.frame=CGRectMake(550,0,self.bounds.size.width-550-right,self.bounds.size.height);
    _engagementPanelView.frame=_watchNextWrapperView.frame;
}
- (void)layoutSubviews_compact {
    self.layoutCalls++;
    CGFloat right=self.retainNativePadding?84:[self watchNextSafeAreaInsets].right;
    _watchNextWrapperView.frame=CGRectMake(550,0,self.bounds.size.width-550-right,self.bounds.size.height);
    _engagementPanelView.frame=_watchNextWrapperView.frame;
}
@end
@interface FixtureApp : UIResponder <UIApplicationDelegate>
@property(nonatomic,strong) TPFixtureWindow *window;
@end
@implementation FixtureApp
- (BOOL)application:(UIApplication*)app didFinishLaunchingWithOptions:(NSDictionary*)options {
    self.window=[[TPFixtureWindow alloc]initWithFrame:CGRectMake(0,0,951,669)];
    self.window.rootViewController=[UIViewController new];[self.window makeKeyAndVisible];
    dispatch_async(dispatch_get_main_queue(),^{[self runChecks];});return YES;
}
- (void)runChecks {
    NSMutableArray *checks=[NSMutableArray new];
    void(^check)(BOOL,NSString*)=^(BOOL ok,NSString *name){[checks addObject:@{@"name":name,@"passed":@(ok)}];};
    self.window.bounds=CGRectMake(0,0,951,669);self.window.testInsets=UIEdgeInsetsZero;
    YTWatchLayerView *layer=[[YTWatchLayerView alloc]initWithFrame:self.window.bounds];
    [self.window.rootViewController.view addSubview:layer];
    YTWatchView *watch=[[YTWatchView alloc]initWithFrame:layer.bounds];[layer addSubview:watch];
    [watch layoutSubviews_regular];
    CGRect before=watch->_watchNextWrapperView.frame;
    check(fabs(CGRectGetMaxX(before)-867)<0.5,@"reproduce 84-point native watch-column gap");
    check(TPInstallDuoWatchLayout(),@"verified regular-layout and native-inset hooks installed");
    check(TPWatchGeometryEligible(watch),@"watch eligible even when UIWindow right inset is zero");
    [watch layoutSubviews_regular];
    check(fabs(CGRectGetMaxX(watch->_watchNextWrapperView.frame)-951)<0.5,@"recommendations now reach actual window edge");
    check(fabs(CGRectGetMaxX(watch->_engagementPanelView.frame)-951)<0.5,@"engagement panel reaches actual window edge");
    CGRect after=watch->_watchNextWrapperView.frame;
    [watch layoutSubviews_compact];
    check(fabs(CGRectGetMaxX(watch->_watchNextWrapperView.frame)-951)<0.5,@"compact watch path repairs the same right-side gap");
    check([watch watchNextSafeAreaInsets].right==84,@"compact path restores native control insets after layout");
    check([watch watchNextSafeAreaInsets].right==84,@"native control insets unchanged outside column layout");
    check(watch.safeAreaInsets.right==84 && self.window.safeAreaInsets.right==0,@"both distinct UIKit safe-area values preserved");
    NSInteger count=watch.layoutCalls;[watch layoutSubviews_regular];
    check(watch.layoutCalls==count+1,@"exactly one original layout call");
    watch.retainNativePadding=YES;[watch layoutSubviews_regular];
    check(fabs(CGRectGetMaxX(watch->_watchNextWrapperView.frame)-951)<0.5,@"measured frame fallback repairs retained native padding");
    watch.retainNativePadding=NO;
    watch.frame=CGRectMake(0,0,867,669);[watch layoutSubviews_regular];
    check(fabs(CGRectGetMaxX([watch convertRect:watch.bounds toView:self.window])-951)<0.5,@"narrow outer watch viewport expands before native child layout");
    watch.fullscreen=YES;[watch layoutSubviews_regular];
    check(!TPWatchGeometryEligible(watch) && [watch watchNextSafeAreaInsets].right==84,@"fullscreen keeps original native insets");
    watch.fullscreen=NO;watch.frame=layer.bounds;watch.hidden=YES;[watch layoutSubviews_regular];
    check(!TPWatchGeometryEligible(watch),@"hidden preview unchanged");watch.hidden=NO;
    watch.transform=CGAffineTransformMakeScale(.3,.3);
    check(!TPWatchGeometryEligible(watch),@"scaled miniplayer unchanged");watch.transform=CGAffineTransformIdentity;
    UIView *small=[[UIView alloc]initWithFrame:CGRectMake(0,0,300,200)];[layer addSubview:small];
    check(!TPWatchExpandTrailing(small,self.window),@"small content is not expanded");
    UIView *wideGap=[[UIView alloc]initWithFrame:CGRectMake(0,0,600,669)];[layer addSubview:wideGap];
    check(!TPWatchExpandTrailing(wideGap,self.window),@"intentional broad sidebar gap is not expanded");
    // Exercise real Auto Layout external anchors without removing vertical or internal control constraints.
    UIView *constrained=[UIView new];constrained.translatesAutoresizingMaskIntoConstraints=NO;[layer addSubview:constrained];
    NSLayoutConstraint *left=[constrained.leadingAnchor constraintEqualToAnchor:layer.leadingAnchor constant:550];
    NSLayoutConstraint *right=[constrained.trailingAnchor constraintEqualToAnchor:layer.trailingAnchor constant:-84];
    NSLayoutConstraint *top=[constrained.topAnchor constraintEqualToAnchor:layer.topAnchor constant:10];
    NSLayoutConstraint *height=[constrained.heightAnchor constraintEqualToConstant:640];
    [NSLayoutConstraint activateConstraints:@[left,right,top,height]];[layer layoutIfNeeded];
    UIView *control=[UIView new];control.translatesAutoresizingMaskIntoConstraints=NO;[constrained addSubview:control];
    NSLayoutConstraint *aspect=[control.widthAnchor constraintEqualToAnchor:control.heightAnchor];aspect.active=YES;
    check(TPWatchExpandTrailing(constrained,self.window),@"identified external horizontal constraints repaired");
    [layer layoutIfNeeded];
    check(fabs(CGRectGetMaxX(constrained.frame)-951)<0.5 && fabs(constrained.frame.origin.y-10)<0.5,@"Auto Layout expands horizontally while retaining vertical placement");
    check(!left.active && !right.active && top.active && height.active && aspect.active,@"only conflicting external horizontal anchors displaced");
    NSUInteger installed=layer.constraints.count;TPWatchExpandTrailing(constrained,self.window);[layer layoutIfNeeded];
    check(layer.constraints.count==installed,@"repeated layout does not duplicate constraints");
    right.active=YES;TPWatchExpandTrailing(constrained,self.window);
    check(!right.active,@"native reactivation of displaced trailing anchor is handled");
    [constrained removeFromSuperview];UIView *newParent=[[UIView alloc]initWithFrame:layer.bounds];[layer addSubview:newParent];[newParent addSubview:constrained];
    NSLayoutConstraint *newRight=[constrained.trailingAnchor constraintEqualToAnchor:newParent.trailingAnchor constant:-84];
    [NSLayoutConstraint activateConstraints:@[[constrained.leadingAnchor constraintEqualToAnchor:newParent.leadingAnchor constant:550],newRight,[constrained.topAnchor constraintEqualToAnchor:newParent.topAnchor],[constrained.heightAnchor constraintEqualToConstant:640]]];[newParent layoutIfNeeded];
    check(TPWatchExpandTrailing(constrained,self.window),@"reparented Auto Layout view reinstalls constraints on its current parent");[newParent layoutIfNeeded];
    check(fabs(CGRectGetMaxX(constrained.frame)-951)<0.5 && !newRight.active,@"reparented content uses the current window conversion");
    self.window.bounds=CGRectMake(0,0,669,951);
    check(!TPWatchGeometryEligible(watch),@"portrait geometry not modified");
    BOOL passed=YES;for(NSDictionary *c in checks)if(![c[@"passed"]boolValue])passed=NO;
    NSDictionary *report=@{@"passed":@(passed),@"checks":checks,@"fixtureOnly":@YES,@"physicalDeviceTested":@NO,@"beforeFeedRect":NSStringFromCGRect(before),@"afterFeedRect":NSStringFromCGRect(after)};
    NSData *data=[NSJSONSerialization dataWithJSONObject:report options:NSJSONWritingPrettyPrinted error:nil];
    NSString *path=[NSSearchPathForDirectoriesInDomains(NSDocumentDirectory,NSUserDomainMask,YES).firstObject stringByAppendingPathComponent:@"fixture.json"];
    [data writeToFile:path atomically:YES];NSLog(@"FIXTURE %@",passed?@"PASS":@"FAIL");exit(passed?0:1);
}
@end
int main(int argc,char**argv){@autoreleasepool{return UIApplicationMain(argc,argv,nil,NSStringFromClass(FixtureApp.class));}}
